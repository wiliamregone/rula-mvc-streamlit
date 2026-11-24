"""Coordenação do processamento da análise postural."""

from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import math

from models.angulos import medir_pose
from models.medicoes import Medicoes

from infra.pose_detector import PoseDetector
from infra.video_io import (
    VideoLeitor,
    VideoGravador,
    converter_mp4,
)
from infra.csv_repository import gerar_csv

from views.anotacao_view import anotar_frame


@dataclass(frozen=True)
class Configuracao:
    inicio_s: float = 0.0
    max_quadros: int = 900
    max_pixels: int = 1920 * 1080


class AnaliseController:
    def __init__(self, detector_factory=PoseDetector):
        self.detector_factory = detector_factory

    def executar(
        self,
        conteudo,
        extensao,
        config=Configuracao(),
        progresso=None,
    ):
        if not conteudo:
            raise ValueError(
                "Selecione um vídeo não vazio."
            )

        if len(conteudo) > 100 * 1024 * 1024:
            raise ValueError(
                "O vídeo deve ter no máximo 100 MB."
            )

        extensao = extensao.lower()

        extensoes_validas = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
        }

        if extensao not in extensoes_validas:
            raise ValueError(
                "Formato de arquivo não aceito."
            )

        if (
            not math.isfinite(config.inicio_s)
            or config.inicio_s < 0
            or config.max_quadros < 1
        ):
            raise ValueError(
                "Configuração de análise inválida."
            )

        medicoes = Medicoes()

        with TemporaryDirectory(
            prefix="rula_"
        ) as pasta_temporaria:

            pasta = Path(pasta_temporaria)

            entrada = pasta / (
                "entrada" + extensao
            )

            intermediario = pasta / "anotado.avi"
            destino = pasta / "anotado.mp4"

            entrada.write_bytes(conteudo)

            # Recursos são fechados na ordem inversa
            # de sua abertura, inclusive após exceções.
            with ExitStack() as recursos:
                leitor = recursos.enter_context(
                    VideoLeitor(entrada)
                )

                quantidade_pixels = (
                    leitor.largura * leitor.altura
                )

                if quantidade_pixels > config.max_pixels:
                    raise ValueError(
                        "Resolução acima do limite "
                        "de 1920 × 1080 pixels."
                    )

                gravador = recursos.enter_context(
                    VideoGravador(
                        intermediario,
                        leitor.fps,
                        (
                            leitor.largura,
                            leitor.altura,
                        ),
                    )
                )

                detector = recursos.enter_context(
                    self.detector_factory()
                )

                truncado = False

                for indice, frame in enumerate(
                    leitor.quadros()
                ):
                    if indice >= config.max_quadros:
                        truncado = True
                        break

                    tempo = indice / leitor.fps

                    if tempo >= config.inicio_s:
                        pontos = detector.detectar(
                            frame
                        )
                    else:
                        pontos = None

                    medicao = medir_pose(pontos)

                    medicoes.adicionar(
                        tempo,
                        medicao,
                    )

                    frame_anotado = anotar_frame(
                        frame,
                        pontos,
                        medicao,
                    )

                    gravador.escrever(
                        frame_anotado
                    )

                    if (
                        progresso is not None
                        and (indice + 1) % 30 == 0
                    ):
                        progresso(indice + 1)

            if not medicoes.tempos:
                raise RuntimeError(
                    "O vídeo não contém "
                    "quadros decodificáveis."
                )

            # O gravador já está fechado neste ponto.
            converter_mp4(
                intermediario,
                destino,
            )

            video_bytes = destino.read_bytes()

        # O diretório temporário já foi removido.
        return {
            "medicoes": medicoes,
            "resumo": medicoes.resumo(),
            "csv": gerar_csv(medicoes),
            "video": video_bytes,
            "truncado": truncado,
            "config": config,
        }