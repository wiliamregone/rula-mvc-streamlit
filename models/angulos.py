"""Cálculos geométricos e seleção do lado analisado."""

import math


def calcular_angulo_3d(a, b, c, tipo="generic"):
    """
    Calcula o ângulo A-B-C.

    Preserva as convenções e a equação do código original.
    """

    ba = [a[i] - b[i] for i in range(3)]
    bc = [c[i] - b[i] for i in range(3)]

    produto_escalar = sum(
        ba[i] * bc[i]
        for i in range(3)
    )

    magnitude_ba = math.sqrt(
        sum(valor * valor for valor in ba)
    )

    magnitude_bc = math.sqrt(
        sum(valor * valor for valor in bc)
    )

    cosseno = produto_escalar / (
        magnitude_ba * magnitude_bc + 1e-6
    )

    cosseno = max(-1.0, min(1.0, cosseno))

    angulo_interno = math.degrees(
        math.acos(cosseno)
    )

    if tipo == "trunk":
        return 90.0 - angulo_interno

    if tipo == "hinge":
        return 180.0 - angulo_interno

    if tipo == "ankle":
        return angulo_interno - 180.0

    return angulo_interno


ARTICULACOES = (
    "ombro",
    "cotovelo",
    "tronco",
    "coxa",
)


# Índices dos pontos do MediaPipe Pose.
# Esses números evitam importar MediaPipe no Model.
PONTOS = {
    "dir": {
        "quadril": 24,
        "ombro": 12,
        "cotovelo": 14,
        "pulso": 16,
        "joelho": 26,
        "tornozelo": 28,
    },
    "esq": {
        "quadril": 23,
        "ombro": 11,
        "cotovelo": 13,
        "pulso": 15,
        "joelho": 25,
        "tornozelo": 27,
    },
}


TRIPLAS = {
    "ombro": (
        "quadril",
        "ombro",
        "cotovelo",
    ),
    "cotovelo": (
        "ombro",
        "cotovelo",
        "pulso",
    ),
    "tronco": (
        "ombro",
        "quadril",
        "joelho",
    ),
    "coxa": (
        "quadril",
        "joelho",
        "tornozelo",
    ),
}


def medir_pose(pontos):
    """
    Retorna:
        (lado, angulos), quando existem pontos válidos;
        None, quando a medição não pode ser realizada.
    """

    if pontos is None or len(pontos) < 33:
        return None

    visibilidade_direita = pontos[12].visibility
    visibilidade_esquerda = pontos[11].visibility

    if visibilidade_direita >= visibilidade_esquerda:
        lado = "dir"
    else:
        lado = "esq"

    indices = PONTOS[lado]

    coordenadas = {
        nome: (
            pontos[indice].x,
            pontos[indice].y,
            pontos[indice].z,
        )
        for nome, indice in indices.items()
    }

    coordenadas_validas = all(
        math.isfinite(valor)
        for ponto in coordenadas.values()
        for valor in ponto
    )

    if not coordenadas_validas:
        return None

    angulos = {}

    for articulacao, tripla in TRIPLAS.items():
        a, b, c = (
            coordenadas[nome]
            for nome in tripla
        )

        # Mantém o tipo generic usado no script original.
        angulos[articulacao] = calcular_angulo_3d(
            a,
            b,
            c,
        )

    return lado, angulos