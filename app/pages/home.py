import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from styles.global_css import load_css
from components.navbar import render_navbar
from components.podium import render_podium
from components.table import render_classification_table

load_css()
render_navbar()

# ── Hero ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="apex-hero">
      <div class="sub-label">Round 4 &nbsp;·&nbsp; 2026 Season</div>
      <h1 class="race-name">BRITISH <span>GRAND PRIX</span></h1>
      <p class="tagline">Predict the Future. &nbsp;·&nbsp; Upcoming Race Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Race Center ────────────────────────────────────────────────────────
col_track, col_info = st.columns([7, 3])

with col_track:
    st.markdown(
        """
        <div class="track-viz-placeholder">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="28" stroke="#1F2937" stroke-width="2"/>
            <circle cx="32" cy="32" r="18" stroke="#E10600" stroke-width="2" stroke-dasharray="4 4"/>
            <circle cx="32" cy="12" r="3" fill="#E10600"/>
          </svg>
          <span class="viz-label">Track Visualization</span>
          <span>Live race map &nbsp;·&nbsp; Coming in v3</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_info:
    st.markdown(
        """
        <div class="apex-card">
          <h3>Race Information</h3>
          <p class="card-value" style="font-size:1.1rem;">British Grand Prix</p>
          <p class="card-sub">Silverstone Circuit</p>
          <br/>
          <div class="driver-stat-row"><span class="stat-label">Laps</span><span class="stat-val">52</span></div>
          <div class="driver-stat-row"><span class="stat-label">Date</span><span class="stat-val">5 Jul 2026</span></div>
          <div class="driver-stat-row"><span class="stat-label">Weather</span><span class="stat-val">Cloudy, 18 °C</span></div>
          <div class="driver-stat-row"><span class="stat-label">Confidence</span><span class="stat-val" style="color:#E10600">Low</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Prediction Metric Cards ────────────────────────────────────────────
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        """
        <div class="apex-card">
          <h3>Predicted Winner</h3>
          <p class="card-value">M. Verstappen</p>
          <p class="card-sub">Red Bull Racing</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """
        <div class="apex-card">
          <h3>Podium Probability</h3>
          <p class="card-value">91%</p>
          <p class="card-sub">Top-3 finish likelihood</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        """
        <div class="apex-card">
          <h3>Model Confidence</h3>
          <p class="card-value">84%</p>
          <p class="card-sub">Based on 2020–2025 data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Predicted Podium ───────────────────────────────────────────────────
st.markdown('<p class="section-label">Predicted Podium</p>', unsafe_allow_html=True)
render_podium(
    p1={"driver": "Max Verstappen",  "team": "Red Bull Racing"},
    p2={"driver": "Lewis Hamilton",  "team": "Mercedes"},
    p3={"driver": "Charles Leclerc", "team": "Ferrari"},
)

# ── Full Classification ────────────────────────────────────────────────
st.markdown('<p class="section-label">Predicted Classification</p>', unsafe_allow_html=True)

CLASSIFICATION = [
    {"pos": 1,  "driver": "Max Verstappen",   "team": "Red Bull",     "time": "1:22:34.001"},
    {"pos": 2,  "driver": "Lewis Hamilton",    "team": "Mercedes",     "time": "+3.2s"},
    {"pos": 3,  "driver": "Charles Leclerc",   "team": "Ferrari",      "time": "+8.7s"},
    {"pos": 4,  "driver": "George Russell",    "team": "Mercedes",     "time": "+11.4s"},
    {"pos": 5,  "driver": "Carlos Sainz",      "team": "Ferrari",      "time": "+15.8s"},
    {"pos": 6,  "driver": "Lando Norris",      "team": "McLaren",      "time": "+19.3s"},
    {"pos": 7,  "driver": "Fernando Alonso",   "team": "Aston Martin", "time": "+24.6s"},
    {"pos": 8,  "driver": "Oscar Piastri",     "team": "McLaren",      "time": "+28.1s"},
    {"pos": 9,  "driver": "Lance Stroll",      "team": "Aston Martin", "time": "+33.5s"},
    {"pos": 10, "driver": "Esteban Ocon",      "team": "Alpine",       "time": "+38.0s"},
]
render_classification_table(CLASSIFICATION)

# ── Prediction Explanation ─────────────────────────────────────────────
st.markdown('<p class="section-label">Why This Prediction?</p>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="apex-card">
      <ul style="color:#9CA3AF;font-size:0.9rem;padding-left:1.2rem;line-height:1.9;">
        <li><span style="color:#F9FAFB;font-weight:600;">Highest Skill Score</span> &nbsp;— Verstappen leads at 98 / 100</li>
        <li><span style="color:#F9FAFB;font-weight:600;">Strong Qualifying Pace</span> &nbsp;— 95 / 100 qualifying index</li>
        <li><span style="color:#F9FAFB;font-weight:600;">Low DNF Risk</span> &nbsp;— RBR reliability score: 97%</li>
        <li><span style="color:#F9FAFB;font-weight:600;">Track Affinity</span> &nbsp;— 4 wins at Silverstone in last 5 visits</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)