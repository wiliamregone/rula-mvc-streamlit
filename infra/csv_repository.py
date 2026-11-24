"""Exportação das medições para CSV."""

import csv
import io

from models.medicoes import CAMPOS


def gerar_csv(medicoes):
    buffer = io.StringIO(newline="")

    escritor = csv.writer(buffer)

    escritor.writerow([
        "frame",
        "tempo_s",
        "lado",
        *CAMPOS,
    ])

    for indice, tempo in enumerate(medicoes.tempos):
        lado = medicoes.lados[indice]

        valores = [
            medicoes.dados[campo][indice]
            for campo in CAMPOS
        ]

        escritor.writerow([
            indice,
            tempo,
            lado or "",
            *valores,
        ])

    return buffer.getvalue().encode("utf-8-sig")