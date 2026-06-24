import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from styles.global_css import load_css
from components.navbar import render_navbar
from components.table import render_standings_table

load_css()
render_navbar()


# ── Hero ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="apex-hero">
      <div class="sub-label">Powered by Skill Scores</div>
      <h1 class="race-name">DRIVER <span>INTELLIGENCE</span></h1>
      <p class="tagline">Who are the strongest drivers on the grid?</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Championship Standings Table ──────────────────────────────────────
st.markdown('<p class="section-label">Global Rankings</p>', unsafe_allow_html=True)

DRIVERS = [
    {"pos": 1,  "driver": "Max Verstappen",     "team": "Red Bull Racing", "skill": 98},
    {"pos": 2,  "driver": "Lewis Hamilton",      "team": "Mercedes",        "skill": 95},
    {"pos": 3,  "driver": "Charles Leclerc",     "team": "Ferrari",         "skill": 93},
    {"pos": 4,  "driver": "Lando Norris",        "team": "McLaren",         "skill": 91},
    {"pos": 5,  "driver": "Fernando Alonso",     "team": "Aston Martin",    "skill": 90},
    {"pos": 6,  "driver": "Carlos Sainz",        "team": "Ferrari",         "skill": 89},
    {"pos": 7,  "driver": "George Russell",      "team": "Mercedes",        "skill": 88},
    {"pos": 8,  "driver": "Oscar Piastri",       "team": "McLaren",         "skill": 86},
    {"pos": 9,  "driver": "Sergio Perez",        "team": "Red Bull Racing", "skill": 82},
    {"pos": 10, "driver": "Lance Stroll",        "team": "Aston Martin",    "skill": 75},
]

render_standings_table(DRIVERS)

# ── Driver Card ───────────────────────────────────────────────────────
st.markdown('<p class="section-label">Driver Profile</p>', unsafe_allow_html=True)

selected = st.selectbox(
    "Select a driver",
    [d["driver"] for d in DRIVERS],
    label_visibility="collapsed",
)

DRIVER_PROFILES = {
    "Max Verstappen":  {"team": "Red Bull Racing", "skill": 98, "qualifying": 95, "racecraft": 99, "consistency": 97, "teammate_dom": 92},
    "Lewis Hamilton":  {"team": "Mercedes",        "skill": 95, "qualifying": 93, "racecraft": 96, "consistency": 95, "teammate_dom": 88},
    "Charles Leclerc": {"team": "Ferrari",         "skill": 93, "qualifying": 96, "racecraft": 90, "consistency": 88, "teammate_dom": 85},
    "Lando Norris":    {"team": "McLaren",         "skill": 91, "qualifying": 91, "racecraft": 91, "consistency": 87, "teammate_dom": 82},
    "Fernando Alonso": {"team": "Aston Martin",    "skill": 90, "qualifying": 88, "racecraft": 95, "consistency": 91, "teammate_dom": 90},
    "Carlos Sainz":    {"team": "Ferrari",         "skill": 89, "qualifying": 88, "racecraft": 88, "consistency": 89, "teammate_dom": 78},
    "George Russell":  {"team": "Mercedes",        "skill": 88, "qualifying": 90, "racecraft": 86, "consistency": 85, "teammate_dom": 72},
    "Oscar Piastri":   {"team": "McLaren",         "skill": 86, "qualifying": 86, "racecraft": 85, "consistency": 84, "teammate_dom": 77},
    "Sergio Perez":    {"team": "Red Bull Racing", "skill": 82, "qualifying": 79, "racecraft": 84, "consistency": 78, "teammate_dom": 55},
    "Lance Stroll":    {"team": "Aston Martin",    "skill": 75, "qualifying": 73, "racecraft": 74, "consistency": 74, "teammate_dom": 58},
}

profile = DRIVER_PROFILES.get(selected, {})

col_card, col_compare = st.columns([5, 5])

with col_card:
    st.markdown(
        f"""
        <div class="driver-card">
          <div class="driver-name">{selected}</div>
          <div class="driver-team">{profile.get('team', '—')}</div>
          <div class="skill-score">{profile.get('skill', '—')}<span style="font-size:1rem;color:#9CA3AF"> / 100</span></div>
          <div class="driver-stat-row">
            <span class="stat-label">Qualifying</span>
            <span class="stat-val">{profile.get('qualifying', '—')}</span>
          </div>
          <div class="driver-stat-row">
            <span class="stat-label">Racecraft</span>
            <span class="stat-val">{profile.get('racecraft', '—')}</span>
          </div>
          <div class="driver-stat-row">
            <span class="stat-label">Consistency</span>
            <span class="stat-val">{profile.get('consistency', '—')}</span>
          </div>
          <div class="driver-stat-row" style="border-bottom:none">
            <span class="stat-label">Teammate Dominance</span>
            <span class="stat-val">{profile.get('teammate_dom', '—')}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Driver Comparison ──────────────────────────────────────────────────
st.markdown('<p class="section-label">Driver Comparison</p>', unsafe_allow_html=True)

cmp1, cmp2 = st.columns(2)

with cmp1:
    driver_a = st.selectbox("Driver A", [d["driver"] for d in DRIVERS], index=0, key="cmp_a")

with cmp2:
    driver_b = st.selectbox("Driver B", [d["driver"] for d in DRIVERS], index=1, key="cmp_b")

pa = DRIVER_PROFILES.get(driver_a, {})
pb = DRIVER_PROFILES.get(driver_b, {})

STATS = ["skill", "qualifying", "racecraft", "consistency", "teammate_dom"]
LABELS = ["Skill", "Qualifying", "Racecraft", "Consistency", "Teammate Dom."]

cmp_rows = "".join(
    f"""
    <tr>
      <td style="font-weight:{'700' if pa.get(s,0)>pb.get(s,0) else '400'};color:{'#F9FAFB' if pa.get(s,0)>pb.get(s,0) else '#9CA3AF'}">{pa.get(s,'—')}</td>
      <td style="color:#9CA3AF;text-align:center;font-size:0.7rem;letter-spacing:.1em;text-transform:uppercase;">{lbl}</td>
      <td style="text-align:right;font-weight:{'700' if pb.get(s,0)>pa.get(s,0) else '400'};color:{'#F9FAFB' if pb.get(s,0)>pa.get(s,0) else '#9CA3AF'}">{pb.get(s,'—')}</td>
    </tr>
    """
    for s, lbl in zip(STATS, LABELS)
)

st.markdown(
    f"""
    <div class="apex-card" style="padding:0;">
      <div style="display:grid;grid-template-columns:1fr auto 1fr;padding:0.8rem 1rem;border-bottom:1px solid #1F2937;">
        <span style="color:#F9FAFB;font-weight:700;">{driver_a}</span>
        <span style="color:#9CA3AF;font-size:0.75rem;">vs</span>
        <span style="color:#F9FAFB;font-weight:700;text-align:right;">{driver_b}</span>
      </div>
      <table class="apex-table">
        <tbody>{cmp_rows}</tbody>
      </table>
    </div>
    """,
    unsafe_allow_html=True,
)