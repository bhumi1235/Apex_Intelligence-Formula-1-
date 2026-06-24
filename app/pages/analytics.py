import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from styles.global_css import load_css
from components.navbar import render_navbar

load_css()
render_navbar()


# ── Hero ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="apex-hero">
      <div class="sub-label">Model Transparency</div>
      <h1 class="race-name">ANALYTICS</h1>
      <p class="tagline">Understand why the model predicts what it predicts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 1. Prediction Factors ─────────────────────────────────────────────
st.markdown('<p class="section-label">Prediction Factors</p>', unsafe_allow_html=True)

FACTORS = {
    "Driver Skill Score":    88,
    "Qualifying Position":   82,
    "Constructor Strength":  74,
    "Recent Form (5 races)": 68,
    "Track Affinity":        61,
    "DNF Risk (inverse)":    55,
    "Teammate Delta":        42,
    "Weather Coefficient":   38,
}

factor_bars = "".join(
    f"""
    <div style="margin-bottom:0.75rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.3rem;">
        <span style="color:#F9FAFB;">{name}</span>
        <span style="color:#9CA3AF;">{val}</span>
      </div>
      <div style="background:#1F2937;border-radius:4px;height:6px;">
        <div style="background:#E10600;width:{val}%;height:6px;border-radius:4px;"></div>
      </div>
    </div>
    """
    for name, val in FACTORS.items()
)

st.markdown(f'<div class="apex-card">{factor_bars}</div>', unsafe_allow_html=True)

# ── 2. Team Strength ──────────────────────────────────────────────────
st.markdown('<p class="section-label">Team Strength</p>', unsafe_allow_html=True)

TEAMS = {
    "Red Bull Racing": 96,
    "Ferrari":         91,
    "Mercedes":        90,
    "McLaren":         88,
    "Aston Martin":    82,
    "Alpine":          72,
    "Williams":        68,
    "AlphaTauri":      65,
    "Alfa Romeo":      62,
    "Haas":            58,
}

team_bars = "".join(
    f"""
    <div style="margin-bottom:0.75rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.3rem;">
        <span style="color:#F9FAFB;">{name}</span>
        <span style="color:#9CA3AF;">{val}</span>
      </div>
      <div style="background:#1F2937;border-radius:4px;height:6px;">
        <div style="background:#6366f1;width:{val}%;height:6px;border-radius:4px;"></div>
      </div>
    </div>
    """
    for name, val in TEAMS.items()
)

st.markdown(f'<div class="apex-card">{team_bars}</div>', unsafe_allow_html=True)

# ── 3. Driver Form ────────────────────────────────────────────────────
st.markdown('<p class="section-label">Driver Form (Last 5 Races)</p>', unsafe_allow_html=True)

import pandas as pd
import altair as alt

form_data = pd.DataFrame({
    "Race":   ["Bahrain", "Saudi", "Australia", "Japan", "China"] * 3,
    "Driver": ["Verstappen"] * 5 + ["Hamilton"] * 5 + ["Leclerc"] * 5,
    "Points": [25, 18, 25, 25, 19,   18, 25, 18, 12, 25,   12, 15, 12, 18, 15],
})

chart = (
    alt.Chart(form_data)
    .mark_line(point=True)
    .encode(
        x=alt.X("Race:N", sort=None),
        y=alt.Y("Points:Q"),
        color=alt.Color("Driver:N", scale=alt.Scale(
            domain=["Verstappen", "Hamilton", "Leclerc"],
            range=["#E10600", "#6b7fff", "#22c55e"],
        )),
        tooltip=["Driver", "Race", "Points"],
    )
    .properties(height=260, background="#111827")
    .configure_view(strokeWidth=0)
    .configure_axis(grid=False, labelColor="#9CA3AF", titleColor="#9CA3AF", domainColor="#1F2937")
    .configure_legend(labelColor="#9CA3AF", titleColor="#9CA3AF")
)

st.markdown('<div class="apex-card">', unsafe_allow_html=True)
st.altair_chart(chart, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── 4. Track Insights ─────────────────────────────────────────────────
st.markdown('<p class="section-label">Track Insights — British Grand Prix</p>', unsafe_allow_html=True)

TRACK_STATS = [
    ("Circuit Length",  "5.891 km"),
    ("Corners",         "18"),
    ("Lap Record",      "1:27.097 — Hamilton (2020)"),
    ("Overtake Index",  "Medium"),
    ("Tyre Degradation","High"),
    ("Weather Avg.",    "Cloudy, 16–20 °C"),
]

track_rows = "".join(
    f"""
    <div class="driver-stat-row">
      <span class="stat-label">{k}</span>
      <span class="stat-val">{v}</span>
    </div>
    """
    for k, v in TRACK_STATS
)

st.markdown(f'<div class="apex-card">{track_rows}</div>', unsafe_allow_html=True)