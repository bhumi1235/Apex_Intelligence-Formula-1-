import streamlit as st


def _row(r):
    leader = r["pos"] == 1
    pos_cls = "rr-pos leader" if leader else "rr-pos"
    time_cls = "rr-time leader" if leader else "rr-time"
    # Build each row as a self-contained string — no nested f-string quotes
    pos_str  = f'{r["pos"]:02d}'
    return (
        f'<div class="result-row">'
        f'<span class="{pos_cls}">{pos_str}</span>'
        f'<div class="rr-driver">'
        f'<div class="rr-name">{r["driver"]}</div>'
        f'<div class="rr-team">{r["team"]}</div>'
        f'</div>'
        f'<span class="{time_cls}">{r["time"]}</span>'
        f'</div>'
    )


def render_classification_table(results):
    html = '<div class="results-table">' + "".join(_row(r) for r in results) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _standings_row(d):
    pos_str = f'{d["pos"]:02d}'
    return (
        f'<div class="result-row">'
        f'<span class="rr-pos">{pos_str}</span>'
        f'<div class="rr-driver">'
        f'<div class="rr-name">{d["driver"]}</div>'
        f'<div class="rr-team">{d["team"]}</div>'
        f'</div>'
        f'<span class="rr-time" style="color:#F0F4F8;font-weight:700;font-size:.9rem;">{d["skill"]}</span>'
        f'</div>'
    )


def render_standings_table(drivers):
    html = '<div class="results-table">' + "".join(_standings_row(d) for d in drivers) + "</div>"
    st.markdown(html, unsafe_allow_html=True)
