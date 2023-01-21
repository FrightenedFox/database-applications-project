import streamlit as st

from ab_project.db import UsosDB
from ab_project.logging_setup import initialize_logging


@st.experimental_singleton
def init_connection():
    initialize_logging()
    database = UsosDB()
    database.connect()
    return database


def main():
    st.header("Mini USOS 🎈")

    st.markdown("Projekt z przedmiotu Aplikacje bazodanowe.")
    st.markdown("Autorzy: Norbert Cyran, Vitalii Morskyi.")

    st.subheader("Diagram relacyjnej bazy danych")
    st.image("Media/database.png")
    st.markdown("---")
    st.subheader("Schemat aplikacji bazodanowej")
    st.image("Media/2023-01-05 AB Project Diagram.png")


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS Main",
    )
    main()
