
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="HSPT Study Lab",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

html_path = Path(__file__).parent / "index.html"

if html_path.exists():
    html = html_path.read_text(encoding="utf-8")
    components.html(
        html,
        height=1600,
        scrolling=True,
    )
else:
    st.error("index.html was not found. Make sure it is in the same GitHub repository as app.py.")
