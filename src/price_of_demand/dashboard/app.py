"""Ticketing demand console for the current pricing data connector."""

import sys
from pathlib import Path

# Add repository root to path so config can be imported from anywhere
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import json

import pandas as pd
import streamlit as st

from config import MODEL_DIR, PROCESSED_DATA_DIR

st.set_page_config(page_title="Price of Demand | Ticketing Console", page_icon="TKT", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
    :root { --ink:#17233d; --muted:#59647c; --paper:#f1f5fb; --paper-dark:#d9e4f3; --line:#b5c5dc; --red:#e74b66; --blue:#1476d4; --deep:#123d75; --sky:#61c9f2; --yellow:#ffd166; }
    .stApp { background-color:var(--paper); background-image:linear-gradient(rgba(20,118,212,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(20,118,212,.045) 1px,transparent 1px); background-size:32px 32px; color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(241,245,251,.88); }
    [data-testid="stSidebar"] { background:#e5eef9; border-right:1px solid var(--line); }
    h1,h2,h3,p,label,div { font-family:'Space Mono',monospace; }
    h1,h2,h3 { font-family:'Bebas Neue',sans-serif; color:var(--ink); letter-spacing:.02em; }
    h1 { letter-spacing:.01em; font-size:5rem; line-height:.82; margin-bottom:.3rem; max-width:760px; }
    h2 { font-size:2.4rem; letter-spacing:.03em; }
    .eyebrow { color:var(--red); font-family:'Space Mono',monospace; font-size:.68rem; letter-spacing:.16em; text-transform:uppercase; }
    .masthead { border-top:5px solid var(--ink); border-bottom:2px solid var(--ink); padding:12px 0 14px; margin-bottom:30px; display:flex; justify-content:space-between; align-items:flex-end; }
    .masthead-word { font-family:'Bebas Neue',sans-serif; font-size:2rem; letter-spacing:.08em; line-height:.8; }
    .masthead-meta { font-size:.62rem; color:var(--muted); text-transform:uppercase; letter-spacing:.1em; text-align:right; }
    .lede { color:var(--muted); max-width:650px; font-size:.8rem; line-height:1.7; }
    .source { border-left:5px solid var(--blue); background:rgba(255,255,255,.7); color:var(--muted); padding:13px 16px; font-size:.72rem; line-height:1.6; }
    .show-strip { display:flex; gap:0; margin:3px 0 34px; height:66px; }
    .show-ticket { background:var(--blue); color:white; min-width:170px; padding:9px 14px; border-right:2px dashed rgba(255,255,255,.55); position:relative; overflow:hidden; }
    .show-ticket:nth-child(2) { background:var(--red); transform:translateY(8px); }
    .show-ticket:nth-child(3) { background:var(--deep); transform:translateY(-3px); }
    .show-ticket:before,.show-ticket:after { content:''; position:absolute; width:13px; height:13px; background:var(--paper); border-radius:50%; right:-7px; top:25px; }
    .show-ticket:after { left:-7px; right:auto; }
    .show-ticket-top { font-family:'Space Mono',monospace; font-size:.55rem; letter-spacing:.12em; text-transform:uppercase; opacity:.8; }
    .show-ticket-name { font-family:'Bebas Neue',sans-serif; font-size:1.45rem; letter-spacing:.04em; line-height:1; margin-top:5px; }
    .ticket { background:#fff; color:var(--ink); padding:28px 30px; border:2px solid var(--deep); border-left:10px solid var(--red); position:relative; overflow:hidden; box-shadow:8px 8px 0 var(--paper-dark); }
    .ticket:after { content:''; position:absolute; right:38px; top:0; bottom:0; border-left:1px dashed #8da5c1; }
    .ticket-kicker { color:var(--blue); font-family:'Space Mono',monospace; font-size:.64rem; letter-spacing:.13em; text-transform:uppercase; }
    .ticket-title { font-family:'Bebas Neue',sans-serif; font-size:2.6rem; letter-spacing:.03em; line-height:.9; max-width:74%; margin:12px 0 25px; }
    .ticket-meta { color:var(--muted); font-family:'Space Mono',monospace; font-size:.62rem; text-transform:uppercase; }
    .ticket-price { color:var(--red); font-family:'Space Mono',monospace; font-size:1.85rem; font-weight:700; }
    .signal { border-top:1px solid var(--line); padding-top:12px; margin-top:12px; }
    .signal-label { color:var(--muted); font-family:'Space Mono',monospace; font-size:.6rem; letter-spacing:.1em; text-transform:uppercase; }
    [data-testid="stMetric"] { background:rgba(255,250,240,.55); border:1px solid var(--line); padding:14px 16px; border-radius:0; }
    [data-testid="stMetricLabel"] { color:var(--muted); font-family:'IBM Plex Mono',monospace; text-transform:uppercase; font-size:.6rem; }
    [data-testid="stMetricValue"] { color:var(--deep); font-family:'Space Mono',monospace; }
    [data-testid="stSidebar"] [data-testid="stExpander"] { border:1px solid var(--line); background:rgba(255,255,255,.38); }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary { color:var(--deep); font-family:'Space Mono',monospace; font-size:.6rem; letter-spacing:.06em; text-transform:uppercase; white-space:nowrap; }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary svg { color:var(--red); }
    .block-container { max-width:1320px; padding-top:2.2rem; }
    .stSelectbox label { font-family:'Space Mono',monospace; color:var(--red); text-transform:uppercase; font-size:.65rem; letter-spacing:.1em; }
    [data-testid="stSelectbox"] { background:rgba(255,255,255,.72); border:2px solid var(--blue); padding:12px 14px 4px; box-shadow:4px 4px 0 var(--paper-dark); }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div { background:#fff; border:1px solid var(--line); min-height:46px; }
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="singleValue"] { font-family:'Space Mono',monospace; font-size:.72rem; color:#17233d !important; -webkit-text-fill-color:#17233d !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="masthead"><div class="masthead-word">PRICE<br>OF DEMAND</div><div class="masthead-meta">BOX OFFICE LEDGER / 01<br>PRIMARY MARKET OBSERVATORY</div></div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">A FIELD GUIDE TO LISTED PRICES</div>', unsafe_allow_html=True)
st.title("Read the ticket, not the noise.")
st.markdown(
    '<p class="lede">Choose an event to see its listed price band, time-to-show, and collection signal. The market view below puts that one ticket in context.</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="show-strip"><div class="show-ticket"><div class="show-ticket-top">LIVE / PRICE BAND</div><div class="show-ticket-name">ADMIT ONE</div></div><div class="show-ticket"><div class="show-ticket-top">TRACK / DEMAND</div><div class="show-ticket-name">FRONT ROW</div></div><div class="show-ticket"><div class="show-ticket-top">DATA / SIGNAL</div><div class="show-ticket-name">TONIGHT</div></div></div>', unsafe_allow_html=True)
dataset_path = PROCESSED_DATA_DIR / "event_panel.csv"
if not dataset_path.exists():
    st.info("No processed observations yet. Run the daily poll, then build the dataset.")
    st.stop()

frame = pd.read_csv(dataset_path)
panel_path = Path("data/event_panel.csv")
if panel_path.exists():
    panel_ids = pd.read_csv(panel_path)["event_id"].dropna().astype(str)
    frame = frame.loc[frame["event_id"].astype(str).isin(panel_ids)].copy()
if "price_mid" not in frame.columns:
    if {"price_min", "price_max"}.issubset(frame.columns):
        frame["price_mid"] = frame[["price_min", "price_max"]].mean(axis=1)
    else:
        frame["price_mid"] = pd.NA
if "poll_timestamp" in frame.columns:
    frame["poll_timestamp"] = pd.to_datetime(frame["poll_timestamp"], utc=True, errors="coerce")
price_rows = frame.dropna(subset=["price_mid"]).copy()
positive_price_rows = price_rows.loc[price_rows["price_mid"].gt(0)].copy()
poll_dates = frame["poll_timestamp"].dt.date.nunique() if "poll_timestamp" in frame else 0
coverage = len(price_rows) / len(frame) if len(frame) else 0

latest = frame.sort_values("poll_timestamp").drop_duplicates("event_id", keep="last")
event_labels = {}
for _, row in latest.sort_values("event_name").iterrows():
    name = row.get("event_name") or row["event_id"]
    market = row.get("market") or "market unknown"
    event_labels[f"{name}  /  {market}"] = row["event_id"]

with st.sidebar:
    with st.expander("Ticketmaster / data details", expanded=False):
        st.markdown('<div class="eyebrow">CONNECTOR</div>', unsafe_allow_html=True)
        st.code("ticketmaster.discovery", language="text")
        st.caption("Primary-market event listings. Resale prices are not represented.")

st.markdown('<div class="source"><b>DATA LAYER / LISTED INVENTORY</b><br>These are current Ticketmaster price ranges, captured by our own polling process. Missing ranges stay visible as missing rather than being imputed.</div>', unsafe_allow_html=True)
st.write("")

st.subheader("Pick an event")
st.caption("Start here: choose a show to open its ticket and price readout.")
selected_label = st.selectbox("SELECT A SHOW", list(event_labels))
selected_id = event_labels[selected_label]
selected_history = frame.loc[frame["event_id"].eq(selected_id)].sort_values("poll_timestamp")
selected = selected_history.iloc[-1]
selected_price = selected.get("price_mid")
selected_currency = selected.get("currency") or "USD"
selected_days = selected.get("days_until_event")
days_label = "date unavailable"
if pd.notna(selected_days):
    days_label = "event date passed" if selected_days < 0 else f"{selected_days:.0f} days to show"
price_label = "Price not listed"
if pd.notna(selected_price) and selected_price == 0:
    price_label = "FREE / NO CHARGE"
elif pd.notna(selected_price):
    price_label = f"{selected_currency} {selected_price:,.2f} midpoint"

st.markdown(
    f'<div class="ticket"><div class="ticket-kicker">LIVE LISTING / {selected.get("genre") or "EVENT"}</div><div class="ticket-title">{selected.get("event_name") or selected_id}</div><div class="ticket-meta">{selected.get("market") or "Market unknown"}  |  {selected.get("venue_name") or "Venue unknown"}</div><div class="signal"><div class="signal-label">Listed price midpoint</div><div class="ticket-price">{price_label}</div></div><div class="ticket-meta">{days_label}  |  captured {selected["poll_timestamp"].date()}</div></div>',
    unsafe_allow_html=True,
)
st.write("")
price_card, timing_card, history_card = st.columns(3)
with price_card:
    st.markdown('<div class="signal-label">PRICE BAND</div>', unsafe_allow_html=True)
    if selected.get("price_status") == "free_or_no_charge" or selected.get("price_min") == 0:
        st.metric("Min to max", "Free / no charge")
    elif pd.notna(selected.get("price_min")):
        st.metric("Min to max", f"{selected_currency} {selected['price_min']:,.2f} - {selected['price_max']:,.2f}")
    else:
        st.metric("Min to max", "Not listed")
with timing_card:
    st.markdown('<div class="signal-label">TIME SIGNAL</div>', unsafe_allow_html=True)
    st.metric("Days to event", f"{selected_days:.1f}" if pd.notna(selected_days) else "Unknown")
with history_card:
    st.markdown('<div class="signal-label">OBSERVATION SIGNAL</div>', unsafe_allow_html=True)
    st.metric("Saved snapshots", len(selected_history))

st.subheader("What does this event look like over time?")
if len(selected_history) > 1 and selected_history["price_mid"].notna().sum() > 1:
    st.line_chart(selected_history.set_index("poll_timestamp")[["price_min", "price_max", "price_mid"]], color=["#9bd7e5", "#ff765d", "#b9e8c5"])
else:
    st.info("This event has one usable price observation so far. Another daily poll will turn this card into a price path.")

st.divider()
st.subheader("Market context")
market_left, market_right = st.columns([1.15, 1])
with market_left:
    st.caption("Listed midpoint by event. Free-entry and unlisted events are excluded from this paid-ticket comparison.")
    if positive_price_rows.empty:
        st.info("No listed prices are available yet.")
    else:
        chart_data = positive_price_rows.set_index("event_name")["price_mid"].sort_values(ascending=True)
        st.bar_chart(chart_data, color="#ff765d", height=340)
with market_right:
    st.caption("Price coverage is the share of collected event snapshots with a listed range.")
    st.metric("Events tracked", f"{frame['event_id'].nunique():,}")
    st.metric("Price coverage", f"{coverage:.0%}")
    timing = frame.dropna(subset=["days_until_event", "price_mid"])
    if not timing.empty:
        st.scatter_chart(timing, x="days_until_event", y="price_mid", color="genre", height=230)

with st.expander("Model results and research notes"):
    st.caption("The current models predict listed price level across events. They do not claim causal elasticity or historical price movement.")
    metrics_path = MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame(metrics).T, use_container_width=True)
    else:
        st.info("Run the training pipeline to generate model metrics.")

st.divider()
st.markdown('<div class="eyebrow">MODEL STATUS</div>', unsafe_allow_html=True)
metrics_path = MODEL_DIR / "metrics.json"
if poll_dates >= 2 and metrics_path.exists():
    st.dataframe(pd.read_json(metrics_path).T, use_container_width=True)
else:
    st.caption("Current-price models are trained across events. Price-change models remain gated until repeated observations accumulate.")
