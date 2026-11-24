"""Testes das regras do Model."""

from types import SimpleNamespace
import math
import unittest

from models.angulos import (
    calcular_angulo_3d,
    medir_pose,
)
from models.classificacao import (
    classificar_medias,
)
from models.medicoes import (
    Medicoes,
    media_em_faixa,
)


class TestModelo(unittest.TestCase):
    def test_convencoes_angulares(self):
        a = (1, 0, 0)
        b = (0, 0, 0)
        c = (0, 1, 0)

        casos = [
            ("generic", 90),
            ("hinge", 90),
            ("trunk", 0),
            ("ankle", -90),
        ]

        for tipo, esperado in casos:
            with self.subTest(tipo=tipo):
                resultado = calcular_angulo_3d(
                    a,
                    b,
                    c,
                    tipo,
                )

                self.assertAlmostEqual(
                    resultado,
                    esperado,
                )

    def test_sem_dados_nao_classifica(self):
        resultado = classificar_medias({
            "ombro_dir": math.nan,
            "cotovelo_dir": math.nan,
        })

        self.assertIsNone(
            resultado["ombro_dir"]
        )

        self.assertIsNone(
            resultado["cotovelo_dir"]
        )

    def test_ausencia_nao_reutiliza_pontos(self):
        pontos = [
            SimpleNamespace(
                x=indice * 0.01,
                y=indice * 0.02,
                z=indice * 0.001,
                visibility=1.0,
            )
            for indice in range(33)
        ]

        medicoes = Medicoes()

        medicoes.adicionar(
            0.0,
            medir_pose(pontos),
        )

        medicoes.adicionar(
            0.1,
            medir_pose(None),
        )

        self.assertEqual(
            medicoes.lados,
            ["dir", None],
        )

        for valores in medicoes.dados.values():
            self.assertEqual(
                len(valores),
                2,
            )

            self.assertTrue(
                math.isnan(valores[1])
            )

    def test_limites_das_faixas(self):
        valores = [20, 45, 90]

        self.assertEqual(
            media_em_faixa(
                valores,
                20,
                45,
            ),
            32.5,
        )

        self.assertEqual(
            media_em_faixa(
                valores,
                45,
                90,
            ),
            67.5,
        )

    def test_medicao_somente_esquerda(self):
        medicoes = Medicoes()

        medicoes.adicionar(
            0.0,
            (
                "esq",
                {
                    "ombro": 10,
                    "cotovelo": 90,
                    "tronco": 15,
                    "coxa": 90,
                },
            ),
        )

        resumo = medicoes.resumo()

        self.assertEqual(
            resumo["classificacoes"]["ombro_esq"],
            1,
        )

        self.assertIsNone(
            resumo["classificacoes"]["ombro_dir"]
        )

        self.assertTrue(
            math.isnan(
                resumo["faixas"]["verde_sup"]
            )
        )


if __name__ == "__main__":
    unittest.main()