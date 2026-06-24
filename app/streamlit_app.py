import streamlit as st
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from styles.global_css import load_css
from components.navbar import render_navbar

st.set_page_config(page_title="Apex Intelligence", page_icon="🏎️", layout="wide", initial_sidebar_state="collapsed")
load_css()
render_navbar()

# ── Hero ───────────────────────────────────────────────
st.markdown("""
<div class="apex-hero">
  <div class="sub-label">Round 4 · 2026 FIA Formula One World Championship</div>
  <h1 class="race-name">BRITISH <span>GRAND PRIX</span></h1>
  <p class="tagline">Silverstone Circuit &nbsp;·&nbsp; 5 July 2026</p>
</div>
""", unsafe_allow_html=True)

# ── Session Status Bar ─────────────────────────────────
st.markdown("""
<div class="session-bar">
  <span class="live-badge"><span class="live-dot"></span>PREDICTION ACTIVE</span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Session<span class="sb-val">&nbsp;RACE</span></span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Lap<span class="sb-val">&nbsp;—&nbsp;/ 52</span></span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Track<span class="sb-val">&nbsp;DRY</span></span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Air<span class="sb-val">&nbsp;18°C</span></span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Track Temp<span class="sb-val">&nbsp;32°C</span></span>
  <span class="sb-sep">|</span>
  <span class="sb-item">Model<span class="sb-val">&nbsp;XGBoost v2</span></span>
</div>
""", unsafe_allow_html=True)

st.markdown('<span class="section-label">Race Intelligence · Predicted Timing Tower</span>', unsafe_allow_html=True)

# ── Timing Tower Data ──────────────────────────────────
TIMING = [
    {"pos":1,  "code":"VER","name":"M. VERSTAPPEN", "team":"Red Bull Racing","color":"#3671C6","gap":"LEADER","intv":"—",      "lap":"1:27.432","lap_cls":"purple","spd":315,"s1":"purple","s2":"purple","s3":"green"},
    {"pos":2,  "code":"HAM","name":"L. HAMILTON",   "team":"Mercedes",       "color":"#27F4D2","gap":"+3.187","intv":"+3.187", "lap":"1:27.891","lap_cls":"green", "spd":312,"s1":"green","s2":"purple","s3":"yellow"},
    {"pos":3,  "code":"LEC","name":"C. LECLERC",    "team":"Ferrari",        "color":"#E8002D","gap":"+8.731","intv":"+5.544", "lap":"1:28.102","lap_cls":"white", "spd":308,"s1":"yellow","s2":"green","s3":"green"},
    {"pos":4,  "code":"RUS","name":"G. RUSSELL",    "team":"Mercedes",       "color":"#27F4D2","gap":"+11.40","intv":"+2.669", "lap":"1:28.345","lap_cls":"white", "spd":306,"s1":"white","s2":"white","s3":"yellow"},
    {"pos":5,  "code":"SAI","name":"C. SAINZ",      "team":"Ferrari",        "color":"#E8002D","gap":"+15.80","intv":"+4.400", "lap":"1:28.491","lap_cls":"white", "spd":305,"s1":"white","s2":"yellow","s3":"white"},
    {"pos":6,  "code":"NOR","name":"L. NORRIS",     "team":"McLaren",        "color":"#FF8000","gap":"+19.30","intv":"+3.500", "lap":"1:28.610","lap_cls":"white", "spd":304,"s1":"yellow","s2":"white","s3":"white"},
    {"pos":7,  "code":"ALO","name":"F. ALONSO",     "team":"Aston Martin",   "color":"#358C75","gap":"+24.60","intv":"+5.300", "lap":"1:28.892","lap_cls":"white", "spd":302,"s1":"white","s2":"white","s3":"white"},
    {"pos":8,  "code":"PIA","name":"O. PIASTRI",    "team":"McLaren",        "color":"#FF8000","gap":"+28.10","intv":"+3.500", "lap":"1:29.011","lap_cls":"white", "spd":301,"s1":"white","s2":"white","s3":"green"},
    {"pos":9,  "code":"STR","name":"L. STROLL",     "team":"Aston Martin",   "color":"#358C75","gap":"+33.50","intv":"+5.400", "lap":"1:29.340","lap_cls":"white", "spd":298,"s1":"white","s2":"white","s3":"white"},
    {"pos":10, "code":"OCO","name":"E. OCON",       "team":"Alpine",         "color":"#FF87BC","gap":"+38.00","intv":"+4.500", "lap":"1:29.612","lap_cls":"white", "spd":296,"s1":"white","s2":"white","s3":"white"},
]


def tt_row(r):
    p = r["pos"]
    pos_cls = "tt-pos p1" if p == 1 else ("tt-pos p2" if p == 2 else ("tt-pos p3" if p == 3 else "tt-pos"))
    gap_cls = "tt-gap leader" if p == 1 else "tt-gap"
    lap_cls = f"tt-lap {r['lap_cls']}"
    pos_str = f"{p:02d}"
    return (
        f'<div class="tt-row">'
        f'<span class="{pos_cls}">{pos_str}</span>'
        f'<span class="tt-dot" style="background:{r["color"]};"></span>'
        f'<div class="tt-sectors">'
        f'<div class="tt-s {r["s1"]}"></div>'
        f'<div class="tt-s {r["s2"]}"></div>'
        f'<div class="tt-s {r["s3"]}"></div>'
        f'</div>'
        f'<div class="tt-driver"><span class="tt-code">{r["code"]}</span><span class="tt-name">{r["name"]}</span></div>'
        f'<span class="{gap_cls}">{r["gap"]}</span>'
        f'<span class="tt-int">{r["intv"]}</span>'
        f'<span class="{lap_cls}">{r["lap"]}</span>'
        f'<span class="tt-spd">{r["spd"]}</span>'
        f'</div>'
    )


tower_html = (
    '<div class="timing-tower">'
    '<div class="tt-head">'
    '<span>POS</span><span></span><span>S</span>'
    '<span>DRIVER</span><span style="text-align:right">GAP</span>'
    '<span style="text-align:right">INT</span>'
    '<span style="text-align:right">BEST LAP</span>'
    '<span style="text-align:right">KPH</span>'
    '</div>'
    + "".join(tt_row(r) for r in TIMING)
    + '</div>'
)

st.markdown(tower_html, unsafe_allow_html=True)

# ── Circuit + Race Info ────────────────────────────────
st.markdown('<span class="section-label">Circuit & Race Information</span>', unsafe_allow_html=True)
col_cct, col_info = st.columns([6, 4], gap="medium")

with col_cct:
    st.markdown("""
<div class="circuit-card">
  <svg width="100%" height="230" viewBox="0 0 560 240" fill="none">
    <path d="M88 135 L88 90 C88 68,104 56,130 54 L198 51 C222 50,238 57,246 70
             C258 56,280 50,302 53 L342 58 C368 62,386 76,388 98
             C402 86,422 88,432 106 C443 126,437 148,425 161 L412 182
             C405 197,395 209,377 215 L345 227 C322 235,292 235,267 229
             L217 215 C192 207,172 197,158 179 C144 161,136 147,126 145
             C112 143,93 145,88 135"
          stroke="#E10600" stroke-width="8" stroke-linecap="round"/>
    <path d="M103 135 L103 94 C103 78,116 68,134 66 L196 63 C216 62,228 68,236 79
             C248 67,268 62,288 65 L330 70 C352 74,368 86,370 105
             C384 96,400 99,408 114 C417 130,413 149,403 160 L393 178
             C388 190,380 200,364 206 L336 216 C316 223,290 223,269 218
             L225 206 C204 199,188 190,175 175 C163 160,156 148,146 146
             C136 144,108 146,103 135"
          stroke="#1a2540" stroke-width="4" stroke-linecap="round"/>
    <rect x="82" y="100" width="21" height="3" fill="#F0F4F8" rx="1"/>
    <rect x="82" y="107" width="21" height="3" fill="#E10600" rx="1"/>
    <text x="109" y="112" fill="#8899AA" font-size="8" font-family="JetBrains Mono,monospace" letter-spacing=".08em">S/F</text>
    <text x="72" y="87" fill="#E10600" font-size="13">&#8593;</text>
    <text x="238" y="41"  fill="#374151" font-size="8.5" font-family="Inter,sans-serif">COPSE</text>
    <text x="388" y="78"  fill="#374151" font-size="8.5" font-family="Inter,sans-serif">MAGGOTTS</text>
    <text x="432" y="140" fill="#374151" font-size="8.5" font-family="Inter,sans-serif">CHAPEL</text>
    <text x="368" y="238" fill="#374151" font-size="8.5" font-family="Inter,sans-serif">STOWE</text>
    <text x="175" y="244" fill="#374151" font-size="8.5" font-family="Inter,sans-serif">LUFFIELD</text>
    <text x="32"  y="148" fill="#374151" font-size="8.5" font-family="Inter,sans-serif">WOODCOTE</text>
  </svg>
  <div style="font-size:.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#8899AA;margin-top:.4rem;">Silverstone Circuit &nbsp;·&nbsp; 5.891 km</div>
</div>
""", unsafe_allow_html=True)

with col_info:
    st.markdown("""
<div class="apex-card">
  <h3>Race Information</h3>
  <div class="stat-row"><span class="stat-lbl">Date</span><span class="stat-val">5 Jul 2026</span></div>
  <div class="stat-row"><span class="stat-lbl">Laps</span><span class="stat-val">52</span></div>
  <div class="stat-row"><span class="stat-lbl">Length</span><span class="stat-val">5.891 km</span></div>
  <div class="stat-row"><span class="stat-lbl">Distance</span><span class="stat-val">306.198 km</span></div>
  <div class="stat-row"><span class="stat-lbl">Weather</span><span class="stat-val">Cloudy · 18°C</span></div>
  <div class="stat-row"><span class="stat-lbl">Tyre</span><span class="stat-val">Med → Hard</span></div>
  <div class="stat-row" style="border:none"><span class="stat-lbl">Confidence</span><span class="stat-val" style="color:#E10600;">Low</span></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="apex-card">
  <h3>Prediction Summary</h3>
  <div class="stat-row"><span class="stat-lbl">Predicted Winner</span><span class="stat-val">VER</span></div>
  <div class="stat-row"><span class="stat-lbl">Podium Prob.</span><span class="stat-val">91%</span></div>
  <div class="stat-row" style="border:none"><span class="stat-lbl">Model Confidence</span><span class="stat-val">84%</span></div>
</div>
""", unsafe_allow_html=True)

# ── Predicted Podium ───────────────────────────────────
st.markdown('<span class="section-label">Predicted Podium</span>', unsafe_allow_html=True)
st.markdown("""
<div class="podium-wrap">
  <div class="podium-col p2">
    <div class="podium-info">
      <div class="podium-num">2</div>
      <div class="podium-driver-name">L. Hamilton</div>
      <div class="podium-driver-team">Mercedes</div>
    </div>
    <div class="podium-block"></div>
  </div>
  <div class="podium-col p1">
    <div class="podium-info">
      <div class="podium-num">1</div>
      <div class="podium-driver-name">M. Verstappen</div>
      <div class="podium-driver-team">Red Bull Racing</div>
    </div>
    <div class="podium-block"></div>
  </div>
  <div class="podium-col p3">
    <div class="podium-info">
      <div class="podium-num">3</div>
      <div class="podium-driver-name">C. Leclerc</div>
      <div class="podium-driver-team">Ferrari</div>
    </div>
    <div class="podium-block"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Prediction Factors ─────────────────────────────────
st.markdown('<span class="section-label">Key Prediction Factors</span>', unsafe_allow_html=True)
st.markdown("""
<div class="apex-card">
  <ul style="color:#8899AA;font-size:.8rem;padding-left:1.1rem;line-height:2;margin:0;">
    <li><span style="color:#F0F4F8;font-weight:700;">Skill Score 98/100</span> — Highest on the grid</li>
    <li><span style="color:#F0F4F8;font-weight:700;">Qualifying Index 95/100</span> — Strong one-lap pace at Silverstone</li>
    <li><span style="color:#F0F4F8;font-weight:700;">Reliability 97%</span> — Red Bull DNF risk classified Low</li>
    <li><span style="color:#F0F4F8;font-weight:700;">Track Affinity</span> — 4 wins in last 5 visits to Silverstone</li>
  </ul>
</div>
""", unsafe_allow_html=True)