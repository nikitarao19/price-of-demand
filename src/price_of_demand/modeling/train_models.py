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

from price_of_demand.modeling.features import make_price_level_features


def train_models(dataset_path: Path, model_dir: Path) -> dict[str, dict[str, float]]:
    frame = pd.read_csv(dataset_path)
    features, target = make_price_level_features(frame)
    if len(features) < 10:
        raise ValueError("At least 10 events with listed prices are required for training")
    groups = frame.loc[features.index, "event_id"]
    split = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_index, test_index = next(split.split(features, target, groups=groups))
    models = {
        "linear": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "gradient_boosting": HistGradientBoostingRegressor(random_state=42),
    }
    results = {}
    model_dir.mkdir(parents=True, exist_ok=True)
    for name, model in models.items():
        model.fit(features.iloc[train_index], target.iloc[train_index])
        predictions = model.predict(features.iloc[test_index])
        results[name] = {
            "rmse": float(mean_squared_error(target.iloc[test_index], predictions) ** 0.5),
            "mae": float(mean_absolute_error(target.iloc[test_index], predictions)),
        }
        joblib.dump({"model": model, "features": list(features.columns)}, model_dir / f"{name}.joblib")
    results["analysis_target"] = "current_listed_price_midpoint"
    (model_dir / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
