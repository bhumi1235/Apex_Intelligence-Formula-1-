import streamlit as st


def render_navbar():
    st.markdown(
        """
        <div class="apex-navbar">
          <div class="brand">APEX<span>.</span>INTELLIGENCE</div>
          <div class="nav-links">
            <a href="/home"            target="_self">Home</a>
            <a href="/historical"      target="_self">Historical</a>
            <a href="/driver_rankings" target="_self">Driver Rankings</a>
            <a href="/analytics"       target="_self">Analytics</a>
            <a href="/about"           target="_self">About</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )