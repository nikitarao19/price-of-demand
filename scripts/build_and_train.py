"""Rebuild the processed dataset and train the model comparison."""

from config import MODEL_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR
from price_of_demand.data.build_dataset import build_dataset
from price_of_demand.modeling.train_models import train_models


if __name__ == "__main__":
    dataset = build_dataset(RAW_DATA_DIR, PROCESSED_DATA_DIR / "event_panel.csv")
    results = train_models(PROCESSED_DATA_DIR / "event_panel.csv", MODEL_DIR)
    print(f"Processed {len(dataset)} observations")
    for block_name, block in results.items():
        print(f"--- {block_name} ---")
        if block.get("status") == "not_enough_data":
            print(f"  skipped: {block['usable_rows']}/{block['minimum_required']} usable rows")
            continue
        for name, metrics in block.items():
            if not isinstance(metrics, dict):
                continue
            print(f"  {name}: RMSE={metrics['rmse']:.3f}, MAE={metrics['mae']:.3f}")
