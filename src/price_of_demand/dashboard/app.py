"""Ticketing demand console for the current pricing data connector."""

import sys
from pathlib import Path

# Add repository root to path so config can be imported from anywhere
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import json

import pandas as pd
import streamlit as st

from config import EVENT_PANEL_PATH, MODEL_DIR, PROCESSED_DATA_DIR

st.set_page_config(page_title="Price of Demand", page_icon="🎟️", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    :root { --paper:#FBF3E7; --panel:#FFFFFF; --panel-alt:#F3E9D8; --ink:#221A2E; --muted:#6E6478; --coral:#FF5A3C; --blue:#2F5DFF; --yellow:#FFC53D; --line:#221A2E; }
    .stApp { background-color:var(--paper); background-image:radial-gradient(rgba(34,26,46,.10) 1.5px,transparent 1.5px); background-size:15px 15px; color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(251,243,231,.9); }
    [data-testid="stSidebar"] { background:var(--panel-alt); border-right:3px solid var(--ink); }
    h1,h2,h3,p,label,div,span { font-family:'Space Grotesk',sans-serif; }
    h1,h2,h3 { font-family:'Archivo Black',sans-serif; color:var(--ink); letter-spacing:-.01em; }
    h1 { font-size:4.2rem; line-height:.97; margin-bottom:.4rem; max-width:800px; }
    h2 { font-size:1.9rem; }
    h3 { font-size:1.5rem; }
    .eyebrow { color:var(--coral); font-weight:700; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; }
    .masthead { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:4px solid var(--ink); padding-bottom:14px; margin-bottom:10px; }
    .masthead-word { font-family:'Archivo Black',sans-serif; font-size:1.7rem; letter-spacing:.01em; line-height:.95; }
    .masthead-meta { font-size:.66rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; text-align:right; font-weight:600; max-width:220px; }
    .lede { color:var(--muted); max-width:640px; font-size:.95rem; line-height:1.6; margin-bottom:20px; }
    .route-strip { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin:4px 0 32px; }
    .route-step { background:var(--panel); border:2px solid var(--ink); border-radius:999px; padding:7px 16px; font-weight:700; font-size:.7rem; letter-spacing:.03em; text-transform:uppercase; white-space:nowrap; }
    .route-step.is-a { border-color:var(--coral); color:var(--coral); }
    .route-step.is-b { border-color:var(--blue); color:var(--blue); }
    .route-step.is-c { border-color:#B8860B; color:#8a6100; background:#FFF7E1; }
    .route-step.is-d { border-color:var(--ink); color:var(--ink); }
    .route-arrow { color:var(--muted); font-size:1rem; }
    .source { border:2px solid var(--ink); border-radius:14px; background:var(--panel); color:var(--muted); padding:14px 18px; font-size:.82rem; line-height:1.6; margin-bottom:8px; }
    .source b { color:var(--ink); }
    .bill { background:var(--panel); border:3px solid var(--ink); border-radius:20px; padding:30px 32px 26px; position:relative; box-shadow:8px 8px 0 var(--panel-alt); }
    .bill-kicker { color:var(--blue); font-weight:700; font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; }
    .bill-title { font-family:'Archivo Black',sans-serif; font-size:2.3rem; line-height:1.03; letter-spacing:-.01em; margin:10px 0 14px; max-width:82%; }
    .bill-meta { color:var(--muted); font-size:.78rem; font-weight:600; text-transform:uppercase; letter-spacing:.03em; }
    .stamp-row { display:flex; align-items:center; gap:18px; margin:18px 0 16px; flex-wrap:wrap; }
    .stamp-label { color:var(--muted); font-size:.66rem; letter-spacing:.1em; text-transform:uppercase; font-weight:700; margin-bottom:6px; }
    .stamp { display:inline-block; background:var(--coral); color:#fff; font-weight:700; font-size:1.4rem; padding:10px 22px; border-radius:999px; transform:rotate(-2.5deg); box-shadow:4px 4px 0 var(--ink); }
    .stat-label { color:var(--muted); font-weight:700; font-size:.66rem; letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px; }
    [data-testid="stMetric"] { background:var(--panel); border:2px solid var(--ink); border-top:6px solid var(--coral); border-radius:14px; padding:14px 16px; }
    [data-testid="stMetricLabel"] { color:var(--muted); font-weight:600; text-transform:uppercase; font-size:.62rem; letter-spacing:.06em; }
    [data-testid="stMetricValue"] { color:var(--ink); font-family:'Archivo Black',sans-serif; font-size:1.4rem; }
    [data-testid="stSidebar"] [data-testid="stExpander"] { border:2px solid var(--ink); border-radius:12px; background:var(--panel); }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary { color:var(--ink); font-weight:700; font-size:.68rem; letter-spacing:.03em; text-transform:uppercase; white-space:nowrap; }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary svg { color:var(--coral); }
    [data-testid="stExpander"] { border:2px solid var(--ink) !important; border-radius:14px !important; background:var(--panel); }
    .block-container { max-width:1280px; padding-top:2.1rem; }
    .stSelectbox label { font-weight:700; color:var(--ink); text-transform:uppercase; font-size:.8rem; letter-spacing:.03em; }
    [data-testid="stSelectbox"] { background:var(--panel); border:3px solid var(--coral); border-radius:16px; padding:14px 18px 8px; box-shadow:6px 6px 0 var(--ink); margin-bottom:8px; }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div { background:#fff; border:2px solid var(--ink); border-radius:10px; min-height:50px; }
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="singleValue"] { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:.85rem; color:#221A2E !important; -webkit-text-fill-color:#221A2E !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="masthead"><div class="masthead-word">PRICE OF<br>DEMAND</div><div class="masthead-meta">ISSUE NO. 01<br>A LIVE-MUSIC PRICE WATCH</div></div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">STAGE ONE OF FOUR</div>', unsafe_allow_html=True)
st.title("Pick a show. See what it costs.")
st.markdown(
    '<p class="lede">We track a fixed lineup of live-music events on Ticketmaster and check their listed prices every day. Choose one below to see its current price, then scroll down to see how it compares across the whole lineup and what our early models notice.</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="route-strip"><span class="route-step is-a">① PICK A SHOW</span><span class="route-arrow">&rarr;</span><span class="route-step is-b">② SEE ITS PRICE</span><span class="route-arrow">&rarr;</span><span class="route-step is-c">③ COMPARE THE MARKET</span><span class="route-arrow">&rarr;</span><span class="route-step is-d">④ READ THE MODEL NOTES</span></div>', unsafe_allow_html=True)
dataset_path = PROCESSED_DATA_DIR / "event_panel.csv"
if not dataset_path.exists():
    st.info("No processed observations yet. Run the daily poll, then build the dataset.")
    st.stop()

frame = pd.read_csv(dataset_path)
if EVENT_PANEL_PATH.exists():
    panel_ids = pd.read_csv(EVENT_PANEL_PATH)["event_id"].dropna().astype(str)
    frame = frame.loc[frame["event_id"].astype(str).isin(panel_ids)].copy()
if "price_mid" not in frame.columns:
    if {"price_min", "price_max"}.issubset(frame.columns):
        frame["price_mid"] = frame[["price_min", "price_max"]].mean(axis=1)
    else:
        frame["price_mid"] = pd.NA
if "poll_timestamp" in frame.columns:
    frame["poll_timestamp"] = pd.to_datetime(frame["poll_timestamp"], utc=True, errors="coerce")
price_rows = frame.dropna(subset=["price_mid"]).copy()
poll_dates = frame["poll_timestamp"].dt.date.nunique() if "poll_timestamp" in frame else 0
coverage = len(price_rows) / len(frame) if len(frame) else 0

latest = frame.sort_values("poll_timestamp").drop_duplicates("event_id", keep="last")
latest_positive_price_rows = latest.loc[latest["price_mid"].gt(0)].copy()
event_labels = {}
for _, row in latest.sort_values("event_name").iterrows():
    name = row.get("event_name") or row["event_id"]
    market = row.get("market") or "market unknown"
    # Include event start date to distinguish multiple shows of same artist
    if pd.notna(row.get("event_start")):
        date_str = pd.to_datetime(row["event_start"]).strftime("%b %d")
        label = f"{name}  /  {market}  ({date_str})"
    else:
        label = f"{name}  /  {market}"
    event_labels[row["event_id"]] = label

with st.sidebar:
    with st.expander("How we collect this data", expanded=False):
        st.markdown('<div class="eyebrow">DATA SOURCE</div>', unsafe_allow_html=True)
        st.code("ticketmaster.discovery", language="text")
        st.caption("Only primary-market Ticketmaster listings are tracked here. Resale prices are not represented.")

st.markdown('<div class="source"><b>Where this data comes from.</b> These are live Ticketmaster price ranges, collected by our own daily polling process. If a price is missing, we show it as missing rather than guessing at it.</div>', unsafe_allow_html=True)
st.write("")

st.subheader("① Pick a show")
st.caption("This is the only thing you need to do — everything below updates to match your choice.")
selected_id = st.selectbox("Choose a show", list(event_labels), format_func=lambda eid: event_labels[eid])
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

st.write("")
st.subheader("② See its price")
st.markdown(
    f'<div class="bill"><div class="bill-kicker">NOW TRACKING / {selected.get("genre") or "EVENT"}</div><div class="bill-title">{selected.get("event_name") or selected_id}</div><div class="bill-meta">{selected.get("market") or "Market unknown"}  |  {selected.get("venue_name") or "Venue unknown"}</div><div class="stamp-row"><div><div class="stamp-label">Listed price midpoint</div><span class="stamp">{price_label}</span></div></div><div class="bill-meta">{days_label}  |  checked {selected["poll_timestamp"].date()}</div></div>',
    unsafe_allow_html=True,
)
st.write("")
price_card, timing_card, history_card = st.columns(3)
with price_card:
    st.markdown('<div class="stat-label">What it costs</div>', unsafe_allow_html=True)
    if selected.get("price_status") == "free_or_no_charge" or selected.get("price_min") == 0:
        st.metric("Low to high", "Free / no charge")
    elif pd.notna(selected.get("price_min")) and pd.notna(selected.get("price_max")) and selected.get("price_max") > selected.get("price_min"):
        st.metric("Low to high", f"{selected_currency} {selected['price_min']:,.2f} - {selected['price_max']:,.2f}")
    elif pd.notna(selected.get("price_min")):
        st.metric("Low to high", f"{selected_currency} {selected['price_min']:,.2f}+")
    else:
        st.metric("Low to high", "Not listed")
with timing_card:
    st.markdown('<div class="stat-label">How soon it is</div>', unsafe_allow_html=True)
    st.metric("Days until the show", f"{selected_days:.1f}" if pd.notna(selected_days) else "Unknown")
with history_card:
    st.markdown('<div class="stat-label">How often we\'ve checked</div>', unsafe_allow_html=True)
    st.metric("Snapshots saved", len(selected_history))

if len(selected_history) > 1 and selected_history["price_mid"].notna().sum() > 1:
    st.write("")
    st.subheader("Its price over time")
    st.caption("We check this show's price every day — here's how it has moved so far.")
    st.line_chart(selected_history.set_index("poll_timestamp")[["price_min", "price_max", "price_mid"]], color=["#2F5DFF", "#FF5A3C", "#221A2E"])
    st.divider()
st.write("")
st.subheader("③ Compare the market")
st.caption("Different shows cost different amounts for obvious reasons — a stadium tour and a bar gig aren't the same product, and this isn't claiming they should be. This section is here to show where the show you picked sits within everything we're tracking, and whether prices in general move as shows get closer.")
market_left, market_right = st.columns([1.15, 1])
with market_left:
    st.markdown('<div class="stat-label">Listed midpoint, every tracked show</div>', unsafe_allow_html=True)
    if latest_positive_price_rows.empty:
        st.info("No listed prices are available yet.")
    else:
        chart_data = latest_positive_price_rows.set_index("event_name")["price_mid"].sort_values(ascending=True)
        st.bar_chart(chart_data, color="#FF5A3C", height=340)
        if pd.notna(selected_price) and selected_price > 0:
            percentile = latest_positive_price_rows["price_mid"].lt(selected_price).sum() / len(latest_positive_price_rows) * 100
            st.caption(f"The show you picked — **{selected.get('event_name') or selected_id}** at {selected_currency} {selected_price:,.2f} — is priced higher than {percentile:.0f}% of the {len(latest_positive_price_rows)} tracked shows with a listed price.")
with market_right:
    st.markdown('<div class="stat-label">Tracking coverage &amp; timing</div>', unsafe_allow_html=True)
    st.caption("The share of tracked shows with a listed price, and how price relates to days left until showtime.")
    st.metric("Shows we're tracking", f"{frame['event_id'].nunique():,}")
    st.metric("Share with a listed price", f"{coverage:.0%}")
    timing = frame.dropna(subset=["days_until_event", "price_mid"])
    if not timing.empty:
        st.scatter_chart(timing, x="days_until_event", y="price_mid", color="genre", height=230)

def render_model_metrics(metrics: dict) -> None:
    """Show per-model error metrics, skipping non-model metadata keys like analysis_target."""
    model_rows = {name: values for name, values in metrics.items() if isinstance(values, dict)}
    st.caption(
        "RMSE and MAE are both measured in dollars — they show how far off the model's price guess was "
        "from the real listed price, on average, for shows it wasn't trained on. RMSE punishes big misses "
        "harder than MAE. Lower is better for both."
    )
    st.dataframe(pd.DataFrame(model_rows).T, use_container_width=True)
    if isinstance(metrics.get("analysis_target"), str):
        st.caption(f"What it's predicting: `{metrics['analysis_target']}`")


st.write("")
st.subheader("④ Read the model notes")
st.caption("We're experimenting with models that predict a show's price from how soon it is, venue size, and genre. This is an early pattern check, not a claim about cause and effect.")
with st.expander("See the model's accuracy numbers"):
    metrics_path = MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        render_model_metrics(json.loads(metrics_path.read_text(encoding="utf-8")))
    else:
        st.info("Run the training pipeline to generate model metrics.")

st.divider()
st.markdown('<div class="eyebrow">IS THE PRICE CHANGING OVER TIME?</div>', unsafe_allow_html=True)
metrics_path = MODEL_DIR / "metrics.json"
if poll_dates >= 2 and metrics_path.exists():
    render_model_metrics(json.loads(metrics_path.read_text(encoding="utf-8")))
else:
    st.caption("Today's-price models are trained across all shows already. Price-change models stay off until we've collected repeated observations for the same shows.")
