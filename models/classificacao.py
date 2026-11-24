"""Classificações angulares preservadas do código original."""

import math


def classificar_ombro(angulo):
    if angulo <= 20:
        return 1

    if angulo <= 45:
        return 2

    if angulo <= 90:
        return 3

    return 4


def classificar_cotovelo(angulo):
    if 60 <= angulo <= 100:
        return 1

    if angulo < 30 or angulo > 150:
        return 3

    return 2


def classificar_tronco(angulo):
    if angulo <= 20:
        return 1

    if angulo <= 60:
        return 2

    return 4


def classificar_coxa(angulo):
    if 70 <= angulo <= 100:
        return 1

    if angulo < 45 or angulo > 135:
        return 3

    return 2


CLASSIFICADORES = {
    "ombro": classificar_ombro,
    "cotovelo": classificar_cotovelo,
    "tronco": classificar_tronco,
    "coxa": classificar_coxa,
}


def classificar_medias(medias):
    classificacoes = {}

    for chave, valor in medias.items():
        if not math.isfinite(valor):
            classificacoes[chave] = None
            continue

        articulacao = chave.rsplit("_", 1)[0]

        classificador = CLASSIFICADORES[articulacao]

        classificacoes[chave] = classificador(valor)

    return classificacoes