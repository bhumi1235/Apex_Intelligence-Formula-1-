import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg:     #080c12;
  --card:   #0d1421;
  --border: #1a2540;
  --red:    #E10600;
  --white:  #F0F4F8;
  --muted:  #8899AA;
  --purple: #A855F7;
  --green:  #22c55e;
  --yellow: #EAB308;
  --gold:   #FFD700;
  --mono:   'JetBrains Mono', 'Courier New', monospace;
  --sans:   'Inter', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--white);
  font-family: var(--sans);
}
*, *::before, *::after { box-sizing: border-box; }

#MainMenu, header, footer { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stDecoration"] { display: none !important; }

.block-container { padding: 0 2.5rem 3rem !important; max-width: 100% !important; }

/* ── Navbar ─────────────────────────────────────────── */
.apex-navbar {
  display: flex; align-items: center;
  justify-content: space-between;
  height: 60px; padding: 0 2.5rem;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  margin: 0 -2.5rem 2.5rem;
  position: sticky; top: 0; z-index: 999;
}
.brand { font-size: .95rem; font-weight: 800; letter-spacing: .22em; text-transform: uppercase; color: var(--white); }
.brand span { color: var(--red); }
.nav-links a {
  font-size: .68rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted);
  text-decoration: none; margin-left: 2rem;
  padding-bottom: 4px; border-bottom: 2px solid transparent;
  transition: color .2s, border-color .2s;
}
.nav-links a:hover { color: var(--red); border-color: var(--red); }

/* ── Hero ────────────────────────────────────────────── */
.apex-hero { padding: 1.8rem 0 1.4rem; border-bottom: 1px solid var(--border); margin-bottom: 0; }
.sub-label { font-size: .6rem; font-weight: 700; letter-spacing: .22em; text-transform: uppercase; color: var(--red); margin-bottom: .4rem; }
.race-name { font-size: 2.4rem; font-weight: 800; letter-spacing: -.02em; color: var(--white); margin: 0; line-height: 1.05; }
.race-name span { color: var(--red); }
.tagline { color: var(--muted); font-size: .85rem; margin-top: .35rem; }

/* ── Session status bar ──────────────────────────────── */
.session-bar {
  display: flex; align-items: center; gap: 1.5rem;
  padding: .55rem 1.2rem;
  background: var(--card);
  border-bottom: 2px solid var(--red);
  font-family: var(--mono);
  font-size: .68rem; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase;
}
.session-bar .sb-item { color: var(--muted); }
.session-bar .sb-val  { color: var(--white); margin-left: .3rem; }
.session-bar .sb-sep  { color: var(--border); }
.live-badge {
  display: inline-flex; align-items: center; gap: .35rem;
  background: var(--red); color: #fff;
  font-size: .58rem; font-weight: 800; letter-spacing: .14em;
  padding: .18rem .6rem; border-radius: 3px;
}
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: #fff; animation: pulse 1.4s infinite; }
@keyframes pulse { 0%,100%{ opacity:1 } 50%{ opacity:.3 } }

/* ── Timing Tower ───────────────────────────────────── */
.timing-tower { background: var(--card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 1rem; }
.tt-head {
  background: var(--red);
  display: grid;
  grid-template-columns: 36px 12px 28px 1fr 90px 80px 100px 52px;
  gap: .4rem; padding: .4rem 1.2rem;
  font-family: var(--mono); font-size: .58rem; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase; color: rgba(255,255,255,.7);
}
.tt-row {
  display: grid;
  grid-template-columns: 36px 12px 28px 1fr 90px 80px 100px 52px;
  gap: .4rem; align-items: center;
  padding: .55rem 1.2rem;
  border-bottom: 1px solid #0f1826;
  transition: background .15s;
}
.tt-row:last-child { border-bottom: none; }
.tt-row:hover { background: #101d30; }
.tt-pos { font-family: var(--mono); font-size: .82rem; font-weight: 800; color: var(--muted); }
.tt-pos.p1 { color: var(--gold); }
.tt-pos.p2 { color: #C0C0C0; }
.tt-pos.p3 { color: #CD7F32; }
.tt-dot { width: 10px; height: 10px; border-radius: 50%; justify-self: center; }
.tt-sectors { display: flex; flex-direction: column; gap: 2px; }
.tt-s { width: 100%; height: 5px; border-radius: 1px; background: var(--border); }
.tt-s.purple { background: var(--purple); }
.tt-s.green  { background: var(--green); }
.tt-s.yellow { background: var(--yellow); }
.tt-driver { display: flex; flex-direction: column; gap: 1px; }
.tt-code { font-family: var(--mono); font-size: .78rem; font-weight: 800; color: var(--white); letter-spacing: .06em; }
.tt-name { font-size: .64rem; color: var(--muted); letter-spacing: .04em; }
.tt-gap  { font-family: var(--mono); font-size: .78rem; color: var(--muted); text-align: right; }
.tt-gap.leader { color: var(--white); font-weight: 700; }
.tt-int  { font-family: var(--mono); font-size: .72rem; color: #4B6080; text-align: right; }
.tt-lap  { font-family: var(--mono); font-size: .72rem; color: var(--muted); text-align: right; }
.tt-lap.purple { color: var(--purple); font-weight: 700; }
.tt-lap.green  { color: var(--green); }
.tt-spd  { font-family: var(--mono); font-size: .72rem; color: var(--muted); text-align: right; }

/* ── Circuit card ────────────────────────────────────── */
.circuit-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 1.2rem; height: 100%;
  transition: box-shadow .2s;
}
.circuit-card:hover { box-shadow: 0 0 0 1px var(--red); }

/* ── Compact info card ───────────────────────────────── */
.apex-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  padding: .9rem 1.1rem; margin-bottom: .6rem;
  transition: transform .18s, box-shadow .18s;
}
.apex-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,.5); }
.apex-card h3 { font-size: .58rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); margin: 0 0 .3rem; }
.card-value { font-family: var(--mono); font-size: 1.6rem; font-weight: 700; color: var(--white); margin: 0; line-height: 1.1; }
.card-sub   { font-size: .72rem; color: var(--muted); margin-top: .15rem; }

/* ── Stat rows ───────────────────────────────────────── */
.stat-row { display: flex; justify-content: space-between; align-items: center; padding: .4rem 0; border-bottom: 1px solid var(--border); font-size: .78rem; }
.stat-row:last-child { border-bottom: none; }
.stat-lbl { color: var(--muted); }
.stat-val { color: var(--white); font-weight: 600; font-family: var(--mono); }

/* ── Podium ─────────────────────────────────────────── */
.podium-wrap { display: flex; align-items: flex-end; justify-content: center; gap: 3px; height: 280px; margin-bottom: 1.2rem; }
.podium-col  { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; flex: 1; }
.podium-info { text-align: center; padding-bottom: .7rem; }
.podium-num  { font-family: var(--mono); font-size: 3rem; font-weight: 800; line-height: 1; margin-bottom: .15rem; }
.podium-col.p1 .podium-num { color: var(--gold); }
.podium-col.p2 .podium-num { color: #C0C0C0; }
.podium-col.p3 .podium-num { color: #CD7F32; }
.podium-driver-name { font-size: .9rem; font-weight: 700; color: var(--white); }
.podium-driver-team { font-size: .68rem; color: var(--muted); margin-top: 2px; }
.podium-block { width: 100%; border-radius: 5px 5px 0 0; }
.podium-col.p1 .podium-block { height: 140px; background: #141e32; border-top: 3px solid var(--gold); }
.podium-col.p2 .podium-block { height:  88px; background: #111928; border-top: 3px solid #C0C0C0; }
.podium-col.p3 .podium-block { height:  58px; background: #0e1620; border-top: 3px solid #CD7F32; }

/* ── Classification rows ─────────────────────────────── */
.results-table { border-radius: 8px; overflow: hidden; border: 1px solid var(--border); margin-bottom: .8rem; }
.result-row { display: flex; align-items: center; padding: .6rem 1rem; border-bottom: 1px solid #0f1826; transition: background .15s; }
.results-table .result-row:last-child { border-bottom: none; }
.result-row:nth-child(odd)  { background: var(--card); }
.result-row:nth-child(even) { background: #0b1220; }
.result-row:hover { background: #101d30 !important; }
.rr-pos { font-family: var(--mono); font-size: .8rem; font-weight: 800; color: var(--red); width: 36px; flex-shrink: 0; }
.rr-pos.leader { color: var(--gold); }
.rr-driver { flex: 1; }
.rr-name { font-size: .85rem; font-weight: 600; color: var(--white); }
.rr-team { font-size: .68rem; color: var(--muted); margin-top: 1px; }
.rr-time { font-family: var(--mono); font-size: .75rem; color: var(--muted); text-align: right; }
.rr-time.leader { color: var(--white); font-weight: 600; }

/* ── Track reserved area ─────────────────────────────── */
.track-reserved {
  background: linear-gradient(135deg, #0b1220, #0d1421);
  border: 1px dashed #1e2d45; border-radius: 8px;
  min-height: 200px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: .6rem; margin-bottom: 1rem;
}
.track-reserved-title { font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.track-reserved-sub   { font-size: .68rem; color: #3a4f6a; }

/* ── Section label ───────────────────────────────────── */
.section-label { display: block; font-size: .58rem; font-weight: 700; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); margin: 1.8rem 0 .7rem; }

/* ── Timeline ────────────────────────────────────────── */
.tl-item { display: flex; gap: 1rem; align-items: flex-start; padding: .6rem 0; border-bottom: 1px solid var(--border); }
.tl-lap  { font-family: var(--mono); font-size: .6rem; letter-spacing: .12em; text-transform: uppercase; color: var(--red); font-weight: 700; min-width: 50px; padding-top: 2px; }
.tl-evt  { font-size: .82rem; color: var(--white); line-height: 1.5; }
.gain { color: var(--green); font-weight: 600; }
.loss { color: var(--red);   font-weight: 600; }

/* ── Selectbox overrides ─────────────────────────────── */
div[data-testid="stSelectbox"] label { color: var(--muted) !important; font-size: .72rem !important; letter-spacing: .08em; text-transform: uppercase; }
div[data-testid="stSelectbox"] > div > div { background: var(--card) !important; border-color: var(--border) !important; color: var(--white) !important; }
button[kind="primary"] { background: var(--red) !important; border: none !important; font-weight: 700 !important; }

/* ── Driver stat ─────────────────────────────────────── */
.driver-card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.2rem; }
.driver-cname { font-size: 1.25rem; font-weight: 800; color: var(--white); margin: 0 0 .1rem; }
.driver-cteam { font-size: .72rem; color: var(--muted); }
.driver-skill { font-family: var(--mono); font-size: 2.8rem; font-weight: 800; color: var(--red); margin: .6rem 0 .9rem; line-height: 1; }

/* ── Bar charts ──────────────────────────────────────── */
.bar-row { margin-bottom: .6rem; }
.bar-header { display: flex; justify-content: space-between; font-size: .75rem; margin-bottom: .22rem; }
.bar-lbl { color: var(--white); }
.bar-val { color: var(--muted); font-family: var(--mono); }
.bar-track { background: var(--border); border-radius: 3px; height: 5px; }
.bar-fill  { height: 5px; border-radius: 3px; }

@media (max-width: 900px) {
  .block-container { padding: 0 1rem 2rem !important; }
  .apex-navbar { margin: 0 -1rem 2rem; padding: 0 1rem; }
  .tt-head, .tt-row { grid-template-columns: 32px 10px 24px 1fr 70px 60px 80px 42px; }
}
"""


def load_css():
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)