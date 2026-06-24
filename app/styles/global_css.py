import streamlit as st


def load_css():

    st.markdown(
        """
        <style>

        .card{
            background-color:#111827;
            padding:25px;
            border-radius:20px;
            border:1px solid #1f2937;
            margin-bottom:20px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )