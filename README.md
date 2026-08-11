# Price of Demand

A reproducible study of listed concert-ticket prices using the Ticketmaster Discovery API.

## Status

The same-day analysis is runnable now: it discovers future events, collects current listed-price ranges, builds a processed dataset, trains linear and gradient-boosting models for current price level, and serves a Streamlit dashboard with price coverage, genre differences, timing, and model metrics. Longitudinal price-change modeling remains a future extension because Ticketmaster does not provide prior `priceRanges` through the Discovery API.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put the API key in `.env`, then replace the placeholder row in `data/event_panel.csv` with the fixed panel. Run:

```bash
python -m scripts.poll_prices
```

Raw snapshots are gitignored. The API key is also gitignored and must never be committed.

## Dashboard

```bash
streamlit run src/price_of_demand/dashboard/app.py
```

The current model predicts listed price level across events; it does not claim causal elasticity or historical price movement. Those analyses require repeated observations of the same event panel.
