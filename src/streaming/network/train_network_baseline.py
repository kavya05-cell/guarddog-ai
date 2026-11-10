import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from src.streaming.network.network_anomaly_detector import (
    FEATURE_COLUMNS,
    prepare_feature_frame
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "network_flows.jsonl"
MODEL_PATH = PROJECT_ROOT / "models" / "network" / "isolation_forest_baseline.joblib"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "network_baseline_report.json"


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Network flow data not found: {DATA_PATH}"
        )

    df = pd.read_json(DATA_PATH, lines=True)

    if len(df) < 100:
        raise ValueError(
            f"At least 100 flows are required. Found {len(df)}."
        )

    features = prepare_feature_frame(
        df.to_dict(orient="records")
    )

    features = features.replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    model = Pipeline([
        ("scaler", RobustScaler()),
        ("detector", IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=42,
            n_jobs=-1
        ))
    ])

    model.fit(features)

    predictions = model.predict(features)
    anomaly_scores = model.decision_function(features)

    anomaly_count = int((predictions == -1).sum())
    normal_count = int((predictions == 1).sum())

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    report = {
        "model": "IsolationForest",
        "training_flows": int(len(features)),
        "feature_columns": FEATURE_COLUMNS,
        "normal_flows": normal_count,
        "anomalous_flows": anomaly_count,
        "anomaly_percentage": round(
            anomaly_count / len(features) * 100,
            2
        ),
        "score_min": float(anomaly_scores.min()),
        "score_max": float(anomaly_scores.max()),
        "score_mean": float(anomaly_scores.mean()),
        "model_path": str(MODEL_PATH)
    }

    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()