import streamlit as st

def init_session_state():
    defaults = {
        "df": None,
        "ticker": None,
        "pe_ratio": "N/A",
        "sentiment": 0.0,
        "history": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
