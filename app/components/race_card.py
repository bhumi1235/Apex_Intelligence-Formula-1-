import streamlit as st


def render_race_card():

    left, right = st.columns([2,1])

    with left:

        st.markdown(
        """
<div class="card">

<h2>LIVE TRACK VISUALIZATION</h2>

Coming Soon

</div>
""",
unsafe_allow_html=True
)

        st.write("Coming Soon")

    with right:

        st.markdown(
"""
<div class="card">

<h2>Belgian Grand Prix</h2>

Circuit de Spa-Francorchamps

<br><br>

44 Laps

<br><br>

29 June 2026

<br><br>

Sunny

</div>
""",
unsafe_allow_html=True
)
