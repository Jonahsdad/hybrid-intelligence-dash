# streamlit_app.py
from __future__ import annotations
import importlib
import streamlit as st

st.set_page_config(page_title="HYBRID INTELLIGENCE SYSTEMS", layout="wide")

st.sidebar.title("HYBRID INTELLIGENCE SYSTEMS")
st.sidebar.caption("Forecast OS • powered by LIPE")
st.sidebar.divider()

ARENAS = [
    {"key": "crypto flagship", "module": "pages.crypto_flagship"},
]

choices = [a["key"] for a in ARENAS]
choice = st.sidebar.selectbox("Choose Your Arena", choices, index=0)

st.markdown("### HYBRID INTELLIGENCE SYSTEMS | Global Forecast OS")
st.metric("Engine", "Idle")

arena = next(a for a in ARENAS if a["key"] == choice)
mod = importlib.import_module(arena["module"])
mod.show()
