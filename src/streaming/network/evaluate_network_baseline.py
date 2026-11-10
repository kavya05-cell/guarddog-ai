import json
from pathlib import Path
import joblib
import pandas as pd
from src.streaming.network.network_anomaly_detector import prepare_feature_frame
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "network" / "isolation_forest_baseline.joblib"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "network_flows.jsonl"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "network_baseline_evaluation.json"
def main():
    model = joblib.load(MODEL_PATH)

    df = pd.read_json(DATA_PATH, lines=True)
    features = prepare_feature_frame(df.to_dict(orient="records"))
    predictions = model.predict(features)
    scores = model.decision_function(features)
    results = df[
        ["timestamp", "protocol", "src_ip", "dst_ip", "src_port", "dst_port"]
    ].copy()
    results["prediction"] = [
        "anomaly" if value == -1 else "normal"
        for value in predictions
    ]
    results["anomaly_score"] = scores
    anomaly_count = int((predictions == -1).sum())
    normal_count = int((predictions == 1).sum())
    report = {
        "flows_evaluated": int(len(df)),
        "normal_flows": normal_count,
        "anomalous_flows": anomaly_count,
        "anomaly_percentage": round(
            anomaly_count / len(df) * 100, 2
        ),
        "mean_anomaly_score": float(scores.mean()),
        "most_anomalous_flows": results.nsmallest(
            10, "anomaly_score"
        ).to_dict(orient="records")
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8"
    )
    print(json.dumps(report, indent=2, default=str))
if __name__ == "__main__":
    main()
