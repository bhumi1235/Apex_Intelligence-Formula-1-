import streamlit as st


def render_prediction_cards():

    col1, col2, col3 = st.columns(3)

    col1,col2,col3=st.columns(3)

    with col1:

        st.markdown(
    """
    <div class="card">

    <h3>Predicted Winner</h3>

    Verstappen

    </div>
    """,
    unsafe_allow_html=True
    )

    with col2:
        st.markdown(
            """
            <div class="card">

            <h3>Podium Probability</h3>

            91%

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">

            <h3>Confidence</h3>

            84%

            </div>
            """,
            unsafe_allow_html=True
        )