import streamlit as st

def render_navbar():

    cols = st.columns([2,1,1,1,1,1])

    with cols[0]:
        st.markdown("## APEX INTELLIGENCE")

    st.markdown(
"""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
">

<h1>APEX INTELLIGENCE</h1>

<div>

HOME &nbsp;&nbsp;&nbsp;
HISTORICAL &nbsp;&nbsp;&nbsp;
DRIVER RANKINGS &nbsp;&nbsp;&nbsp;
ANALYTICS &nbsp;&nbsp;&nbsp;
ABOUT

</div>

</div>
""",
unsafe_allow_html=True
)

    st.divider()