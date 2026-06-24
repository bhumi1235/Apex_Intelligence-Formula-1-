import streamlit as st


def render_podium(p1: dict, p2: dict, p3: dict):
    """
    Render a three-step podium.
    Each dict has keys: driver, team
    """
    st.markdown(
        f"""
        <div class="apex-podium">
          <div class="podium-card p2">
            <div class="podium-pos">P2</div>
            <div class="podium-driver">{p2["driver"]}</div>
            <div class="podium-team">{p2["team"]}</div>
          </div>
          <div class="podium-card p1">
            <div class="podium-pos">P1 &nbsp;&#127942;</div>
            <div class="podium-driver">{p1["driver"]}</div>
            <div class="podium-team">{p1["team"]}</div>
          </div>
          <div class="podium-card p3">
            <div class="podium-pos">P3</div>
            <div class="podium-driver">{p3["driver"]}</div>
            <div class="podium-team">{p3["team"]}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
