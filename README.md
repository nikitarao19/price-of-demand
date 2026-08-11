# Price of Demand

A reproducible study of listed concert-ticket prices using the Ticketmaster Discovery API.

## Status

It discovers a panel of events, polls their current listed-price ranges, builds a processed dataset, trains linear and gradient-boosting models for current price level, and serves a Streamlit dashboard with price coverage, genre/timing context, and model metrics.

Because Ticketmaster's Discovery API only returns the *current* `priceRanges` (not history), longitudinal price movement has to be assembled from our own repeated polls rather than pulled from the API directly:

- A cross-show **timing proxy** (`price_of_demand.analysis.elasticity`) always runs once there are at least 3 listed prices with known dates - it pools all tracked shows to estimate how price correlates with days-to-show. It's a correlation across different shows, not a causal read on any one show's price path.
- A real **price-change model** trains automatically once at least 10 usable observations exist where the same event has been polled more than once (see `price_of_demand.modeling.features.make_features`). Until then, the dashboard reports how many tracked shows currently qualify instead of a model it can't yet train honestly.

**Known limitation:** `venue_capacity` and `tier` are always blank. Ticketmaster's Discovery API doesn't expose venue capacity, and `tier` was meant to be a manually-assigned category - neither has ever been populated, so that feature contributes nothing to the models yet. Fixing it means hand-curating those two columns in `data/event_panel.csv`, not a code change.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put the API key in `.env`, then generate a tracked panel:

```bash
python -m scripts.discover_panel   # writes data/event_panel.csv - only re-run this to deliberately replace the panel
python -m scripts.poll_prices      # poll current prices for whatever's in the panel
python -m scripts.build_and_train  # rebuild the processed dataset and retrain models
```

Re-running `discover_panel` replaces the tracked panel wholesale, which resets longitudinal history for any events it drops - only do this on purpose, not as part of routine polling.

Raw snapshots are gitignored. The API key is also gitignored and must never be committed.

## Automation

`.github/workflows/daily-poll.yml` polls the existing panel and retrains daily (`scripts.poll_prices` + `scripts.build_and_train` only - it never re-runs `discover_panel`, so the tracked panel stays stable), then commits the refreshed `data/processed/event_panel.csv` and `models/metrics.json` so the deployed dashboard picks it up. It needs a `TICKETMASTER_API_KEY` repository secret:

```bash
gh secret set TICKETMASTER_API_KEY --body "$(grep -m1 '^TICKETMASTER_API_KEY=' .env | cut -d= -f2-)"
```

## Dashboard

```bash
streamlit run src/price_of_demand/dashboard/app.py
```
