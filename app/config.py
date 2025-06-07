__module_name__ = "config"

import streamlit as st

def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
