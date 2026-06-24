import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from styles.global_css import load_css
from components.navbar import render_navbar

load_css()
render_navbar()

# ── Hero ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="apex-hero">
      <div class="sub-label">Flagship Feature</div>
      <h1 class="race-name">WHAT-IF <span>SIMULATOR</span></h1>
      <p class="tagline">Rewrite History. &nbsp;·&nbsp; What could have happened differently?</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Race Selection ──────────────────────────────────────────────────────
st.markdown('<span class="section-label">Race Selection</span>', unsafe_allow_html=True)

col_season, col_race = st.columns(2, gap="medium")
with col_season:
    season = st.selectbox("Season", [2025, 2024, 2023, 2022, 2021, 2020])
with col_race:
    race = st.selectbox("Race", [
        "Belgian Grand Prix", "Monaco Grand Prix", "British Grand Prix",
        "Italian Grand Prix", "Japanese Grand Prix",
    ])

# ── Track Simulation Area (reserved) ───────────────────────────────────
st.markdown('<span class="section-label">Track Simulation Area</span>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="track-reserved">
      <div class="track-reserved-icon">&#9711;</div>
      <div class="track-reserved-title">Drag-and-Drop Race Simulation</div>
      <div class="track-reserved-sub">
        Interact with driver positions directly on the circuit layout &nbsp;·&nbsp; Coming in v3
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Original Grid ───────────────────────────────────────────────────────
st.markdown('<span class="section-label">Original Starting Grid</span>', unsafe_allow_html=True)

ORIGINAL_GRID = [
    {"pos": 1,  "driver": "Max Verstappen",   "team": "Red Bull Racing",  "time": "1:41.252"},
    {"pos": 2,  "driver": "Lewis Hamilton",   "team": "Mercedes",         "time": "1:41.581"},
    {"pos": 3,  "driver": "Charles Leclerc",  "team": "Ferrari",          "time": "1:41.720"},
    {"pos": 4,  "driver": "Lando Norris",     "team": "McLaren",          "time": "1:41.899"},
    {"pos": 5,  "driver": "Carlos Sainz",     "team": "Ferrari",          "time": "1:42.003"},
    {"pos": 6,  "driver": "George Russell",   "team": "Mercedes",         "time": "1:42.104"},
    {"pos": 7,  "driver": "Fernando Alonso",  "team": "Aston Martin",     "time": "1:42.340"},
    {"pos": 8,  "driver": "Oscar Piastri",    "team": "McLaren",          "time": "1:42.511"},
    {"pos": 9,  "driver": "Lance Stroll",     "team": "Aston Martin",     "time": "1:42.688"},
    {"pos": 10, "driver": "Esteban Ocon",     "team": "Alpine",           "time": "1:42.900"},
]

rows = "".join(
    f"""
    <div class="result-row">
      <span class="rr-pos">P{r['pos']}</span>
      <div class="rr-driver">
        <div class="rr-name">{r['driver']}</div>
        <div class="rr-team">{r['team']}</div>
      </div>
      <span class="rr-time">{r['time']}</span>
    </div>
    """
    for r in ORIGINAL_GRID
)

st.markdown(f'<div class="results-table">{rows}</div>', unsafe_allow_html=True)

# ── Scenario Editor ─────────────────────────────────────────────────────
st.markdown('<span class="section-label">Scenario Editor</span>', unsafe_allow_html=True)

DRIVERS = [
    "Max Verstappen", "Lewis Hamilton", "Charles Leclerc", "Lando Norris",
    "Carlos Sainz", "George Russell", "Fernando Alonso", "Oscar Piastri",
    "Lance Stroll", "Esteban Ocon",
]

st.markdown('<div class="apex-card">', unsafe_allow_html=True)
se1, se2 = st.columns(2, gap="large")

with se1:
    st.markdown("**Grid Modifier**")
    swap_a = st.selectbox("Move driver to P1", DRIVERS, index=1, key="swap_a")
    penalty = st.selectbox("Grid Penalty", ["None", "+5 places", "+10 places", "Pit Lane Start"])

with se2:
    st.markdown("**Race Events**")
    force_dnf = st.selectbox("Force DNF", ["None"] + DRIVERS, key="dnf")
    weather   = st.selectbox("Weather Change", ["No Change", "Rain (Lap 10)", "Rain (Lap 30)", "Safety Car"])

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)
btn_col, _ = st.columns([2, 5])
with btn_col:
    simulate = st.button("▶  Run Simulation", use_container_width=True, type="primary")

if simulate:
    st.success("✅  Simulation complete — results loaded below.")

# ── Results Comparison ──────────────────────────────────────────────────
st.markdown('<span class="section-label">Simulation Results</span>', unsafe_allow_html=True)

ORIGINAL  = [{"pos":1,"d":"Verstappen"},{"pos":2,"d":"Hamilton"},{"pos":3,"d":"Leclerc"},{"pos":4,"d":"Norris"},{"pos":5,"d":"Sainz"}]
SIMULATED = [{"pos":1,"d":"Hamilton","delta":"+1"},{"pos":2,"d":"Verstappen","delta":"-1"},{"pos":3,"d":"Norris","delta":"+1"},{"pos":4,"d":"Leclerc","delta":"-1"},{"pos":5,"d":"Sainz","delta":"—"}]

col_orig, col_sim = st.columns(2, gap="medium")

with col_orig:
    orig_rows = "".join(
        f"""
        <div class="result-row">
          <span class="rr-pos">P{r['pos']}</span>
          <div class="rr-driver"><div class="rr-name">{r['d']}</div></div>
        </div>
        """
        for r in ORIGINAL
    )
    st.markdown(
        f"""
        <div style="font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:#9CA3AF;font-weight:700;margin-bottom:.5rem;">
          Original Result
        </div>
        <div class="results-table">{orig_rows}</div>
        """,
        unsafe_allow_html=True,
    )

with col_sim:
    def _delta_cls(d):
        if d.startswith("+"): return "gain"
        if d.startswith("-"): return "loss"
        return ""

    sim_rows = "".join(
        f"""
        <div class="result-row">
          <span class="rr-pos">P{r['pos']}</span>
          <div class="rr-driver"><div class="rr-name">{r['d']}</div></div>
          <span class="{_delta_cls(r['delta'])}" style="font-size:.82rem;font-weight:700;">{r['delta']}</span>
        </div>
        """
        for r in SIMULATED
    )
    st.markdown(
        f"""
        <div style="font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;color:#E10600;font-weight:700;margin-bottom:.5rem;">
          Simulated Result
        </div>
        <div class="results-table">{sim_rows}</div>
        """,
        unsafe_allow_html=True,
    )

# ── Race Timeline Impact ────────────────────────────────────────────────
st.markdown('<span class="section-label">Race Timeline Impact</span>', unsafe_allow_html=True)

TIMELINE = [
    {"lap": "Lap 1",  "event": "Hamilton gains <span class='gain'>+2 places</span> off the line from P3 to P1"},
    {"lap": "Lap 18", "event": "Verstappen pits under VSC — <span class='gain'>undercut succeeds</span>, rejoins P2"},
    {"lap": "Lap 27", "event": "Safety Car deployed — <span class='loss'>Leclerc DNF</span> at Pouhon corner"},
    {"lap": "Lap 36", "event": "Hamilton extends lead to <span class='gain'>+4.7s</span> over Verstappen"},
    {"lap": "Lap 44", "event": "Verstappen closes gap — <span class='loss'>-0.8s</span> per lap to Hamilton"},
]

tl_html = "".join(
    f'<div class="tl-item"><span class="tl-lap">{t["lap"]}</span><span class="tl-evt">{t["event"]}</span></div>'
    for t in TIMELINE
)

st.markdown(f'<div class="apex-card">{tl_html}</div>', unsafe_allow_html=True)