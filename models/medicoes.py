"""Armazenamento das medições e cálculo das estatísticas."""

from dataclasses import dataclass, field
import math

from .angulos import ARTICULACOES
from .classificacao import classificar_medias


CAMPOS = tuple(
    f"{articulacao}_{lado}"
    for lado in ("dir", "esq")
    for articulacao in ARTICULACOES
)


def media_valida(valores):
    validos = [
        float(valor)
        for valor in valores
        if math.isfinite(valor)
    ]

    if not validos:
        return math.nan

    return sum(validos) / len(validos)


def media_em_faixa(valores, limite_inferior, limite_superior=None):
    selecionados = []

    for valor in valores:
        if limite_superior is None:
            pertence = valor > limite_inferior
        else:
            pertence = (
                limite_inferior
                <= valor
                <= limite_superior
            )

        if pertence:
            selecionados.append(valor)

    return media_valida(selecionados)


@dataclass
class Medicoes:
    dados: dict = field(
        default_factory=lambda: {
            campo: []
            for campo in CAMPOS
        }
    )

    lados: list = field(default_factory=list)
    tempos: list = field(default_factory=list)

    def adicionar(self, tempo, medicao=None):
        if medicao is None:
            lado = None
            angulos = {}
        else:
            lado, angulos = medicao

        for campo in CAMPOS:
            articulacao, sufixo = campo.rsplit("_", 1)

            if sufixo == lado:
                valor = angulos[articulacao]
            else:
                valor = math.nan

            self.dados[campo].append(valor)

        self.lados.append(lado)
        self.tempos.append(tempo)

    def resumo(self):
        medias = {
            campo: media_valida(valores)
            for campo, valores in self.dados.items()
        }

        classificacoes = classificar_medias(medias)

        # Preserva as médias de faixas do script original:
        # apenas dados do lado direito.
        superiores = (
            self.dados["ombro_dir"]
            + self.dados["cotovelo_dir"]
        )

        inferiores = (
            self.dados["tronco_dir"]
            + self.dados["coxa_dir"]
        )

        faixas = {
            "verde_sup": media_em_faixa(
                superiores, 20, 45
            ),
            "amarela_sup": media_em_faixa(
                superiores, 45, 90
            ),
            "vermelha_sup": media_em_faixa(
                superiores, 90
            ),
            "verde_inf": media_em_faixa(
                inferiores, 0, 20
            ),
            "amarela_inf": media_em_faixa(
                inferiores, 20, 60
            ),
            "vermelha_inf": media_em_faixa(
                inferiores, 60
            ),
        }

        quadros_medidos = sum(
            lado is not None
            for lado in self.lados
        )

        return {
            "medias": medias,
            "classificacoes": classificacoes,
            "faixas": faixas,
            "quadros": len(self.tempos),
            "quadros_medidos": quadros_medidos,
        }