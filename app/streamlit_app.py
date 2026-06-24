import streamlit as st

from views.home import show_home
from styles.global_css import load_css



st.set_page_config(
    page_title="Apex Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
load_css()

show_home()