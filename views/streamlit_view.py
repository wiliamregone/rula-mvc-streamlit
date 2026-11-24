"""Interface web da aplicação."""

from pathlib import Path
import hashlib
import io
import zipfile

import pandas as pd
import streamlit as st

from controllers.analise_controller import Configuracao

from .graficos_view import (
    criar_graficos,
    figura_png,
)


class StreamlitView:
    def executar(self, controller):
        st.title(
            "Análise postural por vídeo"
        )

        st.caption(
            "Ângulos e classificações do código original. "
            "Não implementa a pontuação RULA completa."
        )

        st.write(
            "Envie um vídeo, configure a análise "
            "e clique em Analisar."
        )

        st.caption(
            "Até 100 MB e 1920 × 1080 pixels. "
            "O vídeo de saída não contém áudio."
        )

        arquivo = st.file_uploader(
            "Selecione um vídeo",
            type=[
                "mp4",
                "avi",
                "mov",
                "mkv",
            ],
        )

        inicio = st.number_input(
            "Iniciar medições em (s)",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        limite = st.number_input(
            "Máximo de quadros processados",
            min_value=30,
            max_value=3600,
            value=900,
            step=30,
        )

        st.caption(
            "O limite considera os primeiros quadros "
            "do vídeo, sem alterar o FPS."
        )

        if arquivo is not None:
            conteudo = arquivo.getvalue()
        else:
            conteudo = b""

        assinatura = (
            hashlib.sha256(
                conteudo
            ).hexdigest(),
            float(inicio),
            int(limite),
        )

        # Impede apresentar um resultado associado
        # a outro arquivo ou outra configuração.
        if (
            st.session_state.get("assinatura")
            != assinatura
        ):
            st.session_state.pop(
                "resultado",
                None,
            )

        analisar = st.button(
            "Analisar",
            disabled=arquivo is None,
        )

        if analisar:
            st.session_state.pop(
                "resultado",
                None,
            )

            status = st.empty()

            try:
                configuracao = Configuracao(
                    inicio_s=float(inicio),
                    max_quadros=int(limite),
                )

                with st.spinner(
                    "Processando vídeo..."
                ):
                    resultado = controller.executar(
                        conteudo=conteudo,
                        extensao=Path(
                            arquivo.name
                        ).suffix,
                        config=configuracao,
                        progresso=lambda quantidade: (
                            status.info(
                                f"{quantidade} "
                                "quadros processados"
                            )
                        ),
                    )

                st.session_state[
                    "resultado"
                ] = resultado

                st.session_state[
                    "assinatura"
                ] = assinatura

                status.empty()

            except Exception as erro:
                status.empty()

                st.error(
                    "Não foi possível concluir "
                    f"a análise: {erro}"
                )

        resultado = st.session_state.get(
            "resultado"
        )

        if resultado is not None:
            self.mostrar_resultado(
                resultado
            )

    def mostrar_resultado(self, resultado):
        resumo = resultado["resumo"]

        st.success(
            f"{resumo['quadros']} quadros processados; "
            f"{resumo['quadros_medidos']} com medições."
        )

        if resultado["truncado"]:
            st.info(
                "A análise atingiu o limite de quadros. "
                "Os resultados representam somente "
                "o trecho processado."
            )

        if resumo["quadros_medidos"] == 0:
            st.info(
                "Nenhuma medição válida foi encontrada. "
                "Verifique o instante inicial "
                "e o enquadramento da pessoa."
            )

        st.subheader(
            "Vídeo anotado"
        )

        st.video(
            resultado["video"]
        )

        st.subheader(
            "Médias e classificações"
        )

        tabela = pd.DataFrame({
            "Ângulo médio (graus)": (
                resumo["medias"]
            ),
            "Classe angular": (
                resumo["classificacoes"]
            ),
        })

        st.dataframe(
            tabela,
            use_container_width=True,
        )

        st.caption(
            "Valores ausentes permanecem sem classificação."
        )

        st.subheader(
            "Médias por faixa"
        )

        st.caption(
            "Preservando o código original, "
            "estas médias utilizam somente o lado direito."
        )

        tabela_faixas = pd.DataFrame.from_dict(
            resumo["faixas"],
            orient="index",
            columns=[
                "Ângulo médio (graus)"
            ],
        )

        st.dataframe(
            tabela_faixas,
            use_container_width=True,
        )

        st.download_button(
            label="Baixar medições CSV",
            data=resultado["csv"],
            file_name="medicoes.csv",
            mime="text/csv",
        )

        st.download_button(
            label="Baixar vídeo anotado",
            data=resultado["video"],
            file_name="anotado.mp4",
            mime="video/mp4",
        )

        st.subheader(
            "Gráficos"
        )

        figuras = criar_graficos(
            resultado["medicoes"],
            resumo,
        )

        pacote_buffer = io.BytesIO()

        with zipfile.ZipFile(
            pacote_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as pacote:

            for nome, figura in figuras.items():
                st.pyplot(
                    figura,
                    clear_figure=False,
                )

                pacote.writestr(
                    nome + ".png",
                    figura_png(figura),
                )

                figura.clear()

        st.download_button(
            label="Baixar cinco gráficos",
            data=pacote_buffer.getvalue(),
            file_name="graficos.zip",
            mime="application/zip",
        )