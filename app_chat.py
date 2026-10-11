import streamlit as st
from multiagente import gestisci_domanda
from database_orm import crea_sessione
from logging_config import configura_logging

st.title("Jarvis")

if "sessione_id" not in st.session_state:
    configura_logging()
    st.session_state.sessione_id = crea_sessione()
    st.session_state.messaggi = [
         {"ruolo": "assistant", "testo": "Ciao, sono Jarvis! Posso dirti ora e meteo, aprire siti e programmi, gestire le tue note e cercare tra quello che hai scritto. Come posso aiutarti?"}
    ]

# Mostra i messaggi precedenti
for messaggio in st.session_state.messaggi:
    with st.chat_message(messaggio["ruolo"]):
        st.write(messaggio["testo"])

domanda = st.chat_input("Scrivi un messaggio...")

if domanda:
    st.session_state.messaggi.append({"ruolo": "user", "testo": domanda})
    with st.chat_message("user"):
        st.write(domanda)

    with st.chat_message("assistant"):
        with st.spinner("Sto pensando..."):
            risposta = gestisci_domanda(st.session_state.sessione_id, domanda)
        st.write(risposta)

    st.session_state.messaggi.append({"ruolo": "assistant", "testo": risposta})