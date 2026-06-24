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
      <h1 class="race-name">ABOUT <span>APEX INTELLIGENCE</span></h1>
      <p class="tagline">Predict the Future. Rewrite History. A Formula 1 Intelligence Platform.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Vision ────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Vision</p>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="apex-card">
      <p style="color:#9CA3AF;line-height:1.8;font-size:0.9rem;">
        Apex Intelligence is a Formula 1 data platform built to make race prediction and historical
        simulation accessible, interpretable, and visually compelling. It combines machine learning,
        driver skill modelling, and what-if analysis into a single product.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Prediction Engine ─────────────────────────────────────────────────
st.markdown('<p class="section-label">Prediction Engine</p>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="apex-card">
      <p style="color:#9CA3AF;line-height:1.8;font-size:0.9rem;">
        The prediction pipeline uses <strong style="color:#F9FAFB;">XGBoost regression</strong>
        trained on historical race data from 2020–2025. Features include driver skill scores,
        qualifying positions, constructor strength, recent form, and track affinity.
        Strict time-series validation is enforced to prevent data leakage.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Driver Intelligence Engine ────────────────────────────────────────
st.markdown('<p class="section-label">Driver Intelligence Engine</p>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="apex-card">
      <p style="color:#9CA3AF;line-height:1.8;font-size:0.9rem;">
        Each driver is assigned a <strong style="color:#F9FAFB;">Skill Score (0–100)</strong>
        derived from finishing positions relative to teammates, qualifying head-to-heads,
        DNF-adjusted race results, and cross-season consistency. The score evolves as new
        race data is ingested.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── What-If Simulator ─────────────────────────────────────────────────
st.markdown('<p class="section-label">What-If Simulator</p>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="apex-card">
      <p style="color:#9CA3AF;line-height:1.8;font-size:0.9rem;">
        The <strong style="color:#E10600;">Historical What-If Simulator</strong> lets you
        rewrite Formula 1 history by modifying the starting grid, applying grid penalties,
        forcing DNFs, and changing weather conditions. The simulation model re-runs the race
        and returns an alternative classified result alongside a race timeline impact report.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tech Stack ────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Tech Stack</p>', unsafe_allow_html=True)

STACK = [
    ("ML Model",      "XGBoost (regression)"),
    ("Data",          "Ergast API / FastF1"),
    ("Feature Eng.",  "Pandas, NumPy"),
    ("Skill Scores",  "Custom ELO-inspired model"),
    ("Frontend",      "Streamlit + custom HTML/CSS"),
    ("Language",      "Python 3.12"),
]

stack_rows = "".join(
    f"""
    <div class="driver-stat-row">
      <span class="stat-label">{k}</span>
      <span class="stat-val">{v}</span>
    </div>
    """
    for k, v in STACK
)

st.markdown(f'<div class="apex-card">{stack_rows}</div>', unsafe_allow_html=True)

# ── Roadmap ───────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Roadmap</p>', unsafe_allow_html=True)

ROADMAP = [
    ("v1", "Race Prediction",       True),
    ("v2", "What-If Simulator",     True),
    ("v3", "Live Race Intelligence", False),
    ("v4", "Driver Intelligence",    False),
]

roadmap_items = "".join(
    f"""
    <div style="display:flex;align-items:center;gap:1.2rem;padding:0.8rem 0;border-bottom:1px solid #1F2937;">
      <span style="background:{'#E10600' if done else '#1F2937'};color:#F9FAFB;font-size:0.68rem;font-weight:700;
            letter-spacing:.1em;padding:0.3rem 0.7rem;border-radius:5px;">{v}</span>
      <span style="color:{'#F9FAFB' if done else '#9CA3AF'};font-size:0.9rem;">{label}</span>
      {'<span style="margin-left:auto;font-size:0.72rem;color:#22c55e;">✓ Complete</span>' if done else ''}
    </div>
    """
    for v, label, done in ROADMAP
)

st.markdown(f'<div class="apex-card">{roadmap_items}</div>', unsafe_allow_html=True)