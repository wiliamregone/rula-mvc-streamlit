"""Desenho das medições sobre os quadros."""

import cv2

from models.angulos import PONTOS, TRIPLAS


CORES = {
    "ombro": (255, 0, 0),
    "cotovelo": (0, 0, 255),
    "tronco": (255, 255, 0),
    "coxa": (255, 0, 255),
}


def ponto_medio(ponto_a, ponto_b):
    return (
        int((ponto_a[0] + ponto_b[0]) / 2),
        int((ponto_a[1] + ponto_b[1]) / 2),
    )


def anotar_frame(frame, pontos, medicao):
    if medicao is None:
        return frame

    lado, angulos = medicao

    altura, largura = frame.shape[:2]

    coordenadas = {
        nome: (
            int(pontos[indice].x * largura),
            int(pontos[indice].y * altura),
        )
        for nome, indice in PONTOS[lado].items()
    }

    for articulacao, tripla in TRIPLAS.items():
        nome_a, nome_b, nome_c = tripla

        ponto_a = coordenadas[nome_a]
        ponto_b = coordenadas[nome_b]
        ponto_c = coordenadas[nome_c]

        cv2.line(
            frame,
            ponto_a,
            ponto_b,
            (0, 255, 0),
            2,
        )

        cv2.line(
            frame,
            ponto_b,
            ponto_c,
            (0, 255, 0),
            2,
        )

        posicao_texto = ponto_medio(
            ponto_medio(ponto_a, ponto_b),
            ponto_medio(ponto_b, ponto_c),
        )

        texto = f"{int(angulos[articulacao])} graus"

        cv2.putText(
            frame,
            texto,
            posicao_texto,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            CORES[articulacao],
            2,
        )

    for ponto in coordenadas.values():
        cv2.circle(
            frame,
            ponto,
            5,
            (0, 255, 255),
            -1,
        )

    nome_lado = (
        "direito"
        if lado == "dir"
        else "esquerdo"
    )

    cv2.putText(
        frame,
        f"Lado: {nome_lado}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )

    legenda = [
        ("Ombro", CORES["ombro"]),
        ("Cotovelo", CORES["cotovelo"]),
        ("Tronco-coxa", CORES["tronco"]),
        ("Coxa-perna", CORES["coxa"]),
    ]

    for indice, (nome, cor) in enumerate(legenda):
        cv2.putText(
            frame,
            nome,
            (max(0, largura - 180), 30 + indice * 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            cor,
            1,
        )

    return frame