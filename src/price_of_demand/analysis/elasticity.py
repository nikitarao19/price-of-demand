"""Estimate a timing-proxy price relationship with transparent assumptions."""

from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LinearRegression


def estimate_timing_elasticity(frame: pd.DataFrame) -> dict[str, float]:
    usable = frame.dropna(subset=["price_mid", "days_until_event"])
    if len(usable) < 3:
        raise ValueError("At least 3 observations are required for the timing-proxy estimate")
    model = LinearRegression().fit(usable[["days_until_event"]], usable["price_mid"])
    mean_price = usable["price_mid"].mean()
    mean_days = usable["days_until_event"].mean()
    return {
        "coefficient_price_per_day": float(model.coef_[0]),
        "price_elasticity_proxy": float(model.coef_[0] * mean_days / mean_price),
        "r_squared": float(model.score(usable[["days_until_event"]], usable["price_mid"])),
        "n_observations": float(len(usable)),
    }
