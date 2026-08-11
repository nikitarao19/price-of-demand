"""Train and compare a linear baseline with gradient boosting."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from price_of_demand.modeling.features import make_features, make_price_level_features

MIN_TRAINING_ROWS = 10


def _fit_and_score(
    features: pd.DataFrame, target: pd.Series, groups: pd.Series, model_dir: Path, file_prefix: str
) -> dict[str, dict[str, float]]:
    split = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_index, test_index = next(split.split(features, target, groups=groups))
    models = {
        "linear": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "gradient_boosting": HistGradientBoostingRegressor(random_state=42),
    }
    results: dict[str, dict[str, float]] = {}
    for name, model in models.items():
        model.fit(features.iloc[train_index], target.iloc[train_index])
        predictions = model.predict(features.iloc[test_index])
        results[name] = {
            "rmse": float(mean_squared_error(target.iloc[test_index], predictions) ** 0.5),
            "mae": float(mean_absolute_error(target.iloc[test_index], predictions)),
        }
        joblib.dump({"model": model, "features": list(features.columns)}, model_dir / f"{file_prefix}_{name}.joblib")
    return results


def train_models(dataset_path: Path, model_dir: Path) -> dict[str, dict]:
    frame = pd.read_csv(dataset_path)
    model_dir.mkdir(parents=True, exist_ok=True)

    price_level_features, price_level_target = make_price_level_features(frame)
    if len(price_level_features) < MIN_TRAINING_ROWS:
        raise ValueError(f"At least {MIN_TRAINING_ROWS} events with listed prices are required for training")
    price_level_groups = frame.loc[price_level_features.index, "event_id"]
    price_level_results = _fit_and_score(
        price_level_features, price_level_target, price_level_groups, model_dir, "price_level"
    )
    price_level_results["analysis_target"] = "current_listed_price_midpoint"

    # Unlike price level, price-change modeling needs the same event polled more than
    # once, so the panel may not have enough usable rows yet - that's a normal, expected
    # state rather than an error, so it's reported rather than raised.
    price_change_features, price_change_target = make_features(frame)
    if len(price_change_features) >= MIN_TRAINING_ROWS:
        price_change_groups = frame.loc[price_change_features.index, "event_id"]
        price_change_results = _fit_and_score(
            price_change_features, price_change_target, price_change_groups, model_dir, "price_change"
        )
        price_change_results["analysis_target"] = "price_change_since_previous_observation"
    else:
        price_change_results = {
            "status": "not_enough_data",
            "usable_rows": len(price_change_features),
            "minimum_required": MIN_TRAINING_ROWS,
        }

    results = {"price_level": price_level_results, "price_change": price_change_results}
    (model_dir / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
