"""Generate model-agnostic feature importance with SHAP when data exists."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import shap

from price_of_demand.modeling.features import make_price_level_features


def explain_model(dataset_path: Path, model_path: Path, output_path: Path) -> pd.DataFrame:
    import joblib

    frame = pd.read_csv(dataset_path)
    features, _ = make_price_level_features(frame)
    artifact = joblib.load(model_path)
    values = shap.Explainer(artifact["model"])(features)
    importance = pd.DataFrame({"feature": features.columns, "mean_abs_shap": abs(values.values).mean(axis=0)})
    importance = importance.sort_values("mean_abs_shap", ascending=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(output_path, index=False)
    return importance
