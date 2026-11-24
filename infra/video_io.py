"""Leitura, gravação e conversão dos vídeos."""

from pathlib import Path
import math
import shutil
import subprocess

import cv2


class VideoLeitor:
    def __init__(self, caminho):
        self.caminho = caminho

    def __enter__(self):
        self.cap = cv2.VideoCapture(
            str(self.caminho)
        )

        try:
            if not self.cap.isOpened():
                raise RuntimeError(
                    "Não foi possível abrir o vídeo."
                )

            self.fps = float(
                self.cap.get(cv2.CAP_PROP_FPS)
            )

            self.largura = int(
                self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            self.altura = int(
                self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            fps_valido = (
                math.isfinite(self.fps)
                and self.fps > 0
            )

            dimensoes_validas = (
                self.largura > 0
                and self.altura > 0
            )

            if not fps_valido or not dimensoes_validas:
                raise RuntimeError(
                    "Vídeo sem FPS ou dimensões válidas."
                )

            return self

        except Exception:
            self.cap.release()
            raise

    def quadros(self):
        while True:
            sucesso, frame = self.cap.read()

            if not sucesso:
                break

            yield frame

    def __exit__(self, tipo, valor, traceback):
        self.cap.release()


class VideoGravador:
    def __init__(self, caminho, fps, dimensoes):
        self.caminho = caminho
        self.fps = fps
        self.dimensoes = dimensoes

    def __enter__(self):
        Path(self.caminho).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        codec = cv2.VideoWriter_fourcc(
            *"MJPG"
        )

        self.out = cv2.VideoWriter(
            str(self.caminho),
            codec,
            self.fps,
            self.dimensoes,
        )

        if not self.out.isOpened():
            self.out.release()

            raise RuntimeError(
                "Não foi possível iniciar a gravação."
            )

        return self

    def escrever(self, frame):
        self.out.write(frame)

    def __exit__(self, tipo, valor, traceback):
        self.out.release()


def converter_mp4(entrada, saida):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg não instalado ou ausente no PATH."
        )

    comando = [
        "ffmpeg",
        "-y",
        "-v", "error",
        "-i", str(entrada),
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(saida),
    ]

    try:
        subprocess.run(
            comando,
            check=True,
            capture_output=True,
            timeout=180,
        )

    except subprocess.CalledProcessError as erro:
        raise RuntimeError(
            "Falha na conversão do vídeo para H.264."
        ) from erro

    except subprocess.TimeoutExpired as erro:
        raise RuntimeError(
            "A conversão ultrapassou o tempo permitido."
        ) from erro

    arquivo_saida = Path(saida)

    if (
        not arquivo_saida.exists()
        or arquivo_saida.stat().st_size == 0
    ):
        raise RuntimeError(
            "O arquivo de vídeo produzido está vazio."
        )