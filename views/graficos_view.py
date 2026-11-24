"""Gráficos de evolução, médias e classificações."""

import io
import math

import matplotlib

matplotlib.use("Agg")

from matplotlib.figure import Figure


CORES_CLASSES = {
    1: "green",
    2: "gold",
    3: "orange",
    4: "red",
}


def criar_graficos(medicoes, resumo):
    figuras = {}

    grupos = [
        (
            "sup",
            ("ombro", "cotovelo"),
            (20, 45, 90),
        ),
        (
            "inf",
            ("tronco", "coxa"),
            (0, 20, 60),
        ),
    ]

    # Gráficos 1 e 2: evolução temporal.
    for grupo, articulacoes, limites in grupos:
        figura = Figure(figsize=(10, 5))
        eixo = figura.subplots()

        valores_validos = [
            valor
            for lado in ("dir", "esq")
            for articulacao in articulacoes
            for valor in medicoes.dados[
                f"{articulacao}_{lado}"
            ]
            if math.isfinite(valor)
        ]

        teto = max(
            [
                limites[-1] + 10,
                *[
                    valor + 10
                    for valor in valores_validos
                ],
            ]
        )

        superiores = (
            limites[1],
            limites[2],
            teto,
        )

        for inferior, superior, cor in zip(
            limites,
            superiores,
            ("green", "gold", "red"),
        ):
            eixo.axhspan(
                inferior,
                superior,
                color=cor,
                alpha=0.2,
            )

        for lado in ("dir", "esq"):
            for articulacao in articulacoes:
                chave = f"{articulacao}_{lado}"

                eixo.plot(
                    medicoes.tempos,
                    medicoes.dados[chave],
                    label=chave,
                )

        faixas = [
            ("verde", "darkgreen"),
            ("amarela", "goldenrod"),
            ("vermelha", "darkred"),
        ]

        for nome, cor in faixas:
            media = resumo["faixas"][
                f"{nome}_{grupo}"
            ]

            if math.isfinite(media):
                eixo.axhline(
                    media,
                    color=cor,
                    linestyle="--",
                    label=(
                        "Média faixa direita: "
                        f"{media:.1f}°"
                    ),
                )

        eixo.set(
            xlabel="Tempo (s)",
            ylabel="Ângulo (graus)",
            title=(
                "Evolução: "
                + " / ".join(articulacoes)
            ),
        )

        eixo.legend(fontsize=8)
        eixo.grid(True)

        figura.tight_layout()

        figuras[f"evolucao_{grupo}"] = figura

    # Gráfico 3: médias por articulação.
    figura = Figure(figsize=(10, 5))
    eixo = figura.subplots()

    nomes = list(resumo["medias"])
    medias = list(resumo["medias"].values())

    eixo.bar(
        nomes,
        medias,
        color="skyblue",
    )

    eixo.tick_params(
        axis="x",
        rotation=45,
    )

    eixo.set(
        title="Médias por articulação e lado",
        ylabel="Ângulo (graus)",
    )

    figura.tight_layout()

    figuras["medias"] = figura

    # Gráficos 4 e 5: classes angulares.
    grupos_classificacao = [
        ("sup", ("ombro", "cotovelo")),
        ("inf", ("tronco", "coxa")),
    ]

    for grupo, articulacoes in grupos_classificacao:
        figura = Figure(figsize=(10, 5))
        eixo = figura.subplots()

        nomes = [
            f"{articulacao}_{lado}"
            for lado in ("dir", "esq")
            for articulacao in articulacoes
        ]

        classes = [
            resumo["classificacoes"][nome]
            for nome in nomes
        ]

        alturas = [
            classe if classe is not None else 0
            for classe in classes
        ]

        cores = [
            CORES_CLASSES.get(classe, "gray")
            for classe in classes
        ]

        eixo.bar(
            nomes,
            alturas,
            color=cores,
        )

        for indice, classe in enumerate(classes):
            if classe is None:
                eixo.text(
                    indice,
                    0.1,
                    "Sem dados",
                    ha="center",
                )

        eixo.set(
            ylim=(0, 5),
            ylabel="Classe angular",
            title="Classificação pelas regras originais",
        )

        eixo.set_yticks([1, 2, 3, 4])

        figura.tight_layout()

        figuras[f"classificacao_{grupo}"] = figura

    return figuras


def figura_png(figura):
    buffer = io.BytesIO()

    figura.savefig(
        buffer,
        format="png",
        dpi=130,
    )

    return buffer.getvalue()