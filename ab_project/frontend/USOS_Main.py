import subprocess
import sys
import logging

import streamlit as st

from ab_project.db import UsosDB
from ab_project.logging_setup import initialize_logging
from ab_project.usosapi.usosapi import USOSAPIConnection, USOSAPIException
from ab_project.config.config import app_config


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
    
    st.markdown("---")
    
    st.subheader("Udostępnij swój plan zajęć")
    if st.button("Pozyskaj URL autoryzacji"):
        st.session_state.authorisation = True
        st.session_state["usos_connection"] = USOSAPIConnection(
            api_base_address=app_config.usosapi.api_base_address,
            consumer_key=app_config.usosapi.consumer_key,
            consumer_secret=app_config.usosapi.consumer_secret
        )
        st.session_state["authorization_url"] = st.session_state.usos_connection.get_authorization_url()
        # st.session_state["authorization_url"] = "https://google.com"
        
    authorisation_con = st.container()
    if st.session_state.authorisation:
        authorisation_con.info(f"""
Za pomocą poniższego linku można zalogować się za pomocą uczelnianego konta. 
Pozwoli to naszej aplikacji pobrać twój plan zajęć.

> [Zaloguj się za pomocą USOS API]({st.session_state.authorization_url})

Zaloguj się za pomocą uczelnianego konta i skopiuj kod autoryzacji.
Zatem wklej otrzymany kod w poniższe pole i kliknij na przycisk `Autoryzuj`.
        """)
        authorisation_pin = authorisation_con.text_input("Podaj kod autoryzacji:", placeholder="123456")
        if authorisation_con.button("Autoryzuj"):
            try:
                st.session_state.usos_connection.authorize_with_pin(authorisation_pin)
            except (USOSAPIException, KeyError):
                st.error("Błąd autoryzacji. Spróbuj ponownie. Aby wygenerować nowy link autoryzacji załaduj stronę ponownie.")
            else:
                # await pull_data(st.session_state.usos_connection, st.session_state.db)
                st.session_state.authorisation = False
                st.success("""
Autoryzacja przeszła pomyślnie.

Pierwsze zmiany na stronie będą widoczne w ciągu jednej minuty. Wszystkie zajęcia zostaną zaimportowane w ciągu godziny.
                """)
                at, ats = st.session_state.usos_connection.get_access_data()
                logging.info(f"Start collecting USOS data from: {at=} {ats=}")
                subprocess.Popen([
                    sys.executable, 'ab_project/usos_loader.py', 
                    '--access_token', at,
                    '--access_token_secret', ats
                    ], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

    st.markdown("---")

    st.subheader("Diagram relacyjnej bazy danych")
    st.image("database.png")
    
    st.markdown("---")

    st.subheader("Schemat aplikacji bazodanowej")
    st.image("2023-01-05 AB Project Diagram.png")


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS Main",
    )
    if "authorisation" not in st.session_state:
        st.session_state["authorisation"] = False
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
