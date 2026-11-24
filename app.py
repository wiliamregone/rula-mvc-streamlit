"""Inicialização da aplicação Streamlit."""

import streamlit as st

from controllers.analise_controller import (
    AnaliseController,
)
from views.streamlit_view import (
    StreamlitView,
)


def main():
    st.set_page_config(
        page_title="Análise postural MVC",
        layout="wide",
    )

    controlador = AnaliseController()
    interface = StreamlitView()

    interface.executar(controlador)


if __name__ == "__main__":
    main()