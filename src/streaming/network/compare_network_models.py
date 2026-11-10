import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from src.streaming.network.network_anomaly_detector import FEATURE_COLUMNS, prepare_feature_frame
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "network_flows.jsonl"
ORIGINAL_MODEL_PATH = PROJECT_ROOT / "models" / "network" / "isolation_forest_baseline.joblib"
LOG_MODEL_PATH = PROJECT_ROOT / "models" / "network" / "isolation_forest_log_experiment.joblib"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "network_model_comparison.json"
def main():
    df = pd.read_json(DATA_PATH, lines=True)
    features = prepare_feature_frame(df.to_dict(orient="records"))
    features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
    original_model = joblib.load(ORIGINAL_MODEL_PATH)
    log_model = joblib.load(LOG_MODEL_PATH)
    original_predictions = original_model.predict(features)
    log_predictions = log_model.predict(features)
    original_scores = original_model.decision_function(features)
    log_scores = log_model.decision_function(features)
    original_anomalies = set(np.where(original_predictions == -1)[0])
    log_anomalies = set(np.where(log_predictions == -1)[0])
    common_anomalies = original_anomalies & log_anomalies
    original_only = original_anomalies - log_anomalies
    log_only = log_anomalies - original_anomalies
    results = df.copy()
    results["original_prediction"] = np.where(
        original_predictions == -1, "anomaly", "normal"
    )
    results["log_prediction"] = np.where(
        log_predictions == -1, "anomaly", "normal"
    )
    results["original_score"] = original_scores
    results["log_score"] = log_scores
    selected_columns = [
        "timestamp",
        "protocol",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "flow_duration",
        "total_packets",
        "total_bytes",
        "packets_per_second",
        "bytes_per_second",
        "original_prediction",
        "log_prediction",
        "original_score",
        "log_score"
    ]
    original_top = results.sort_values("original_score").head(10)
    log_top = results.sort_values("log_score").head(10)
    report = {
        "flows_compared": int(len(df)),
        "original_anomalies": int(len(original_anomalies)),
        "log_anomalies": int(len(log_anomalies)),
        "flagged_by_both": int(len(common_anomalies)),
        "original_only": int(len(original_only)),
        "log_only": int(len(log_only)),
        "top_original_anomalies": original_top[selected_columns].to_dict(
            orient="records"
        ),
        "top_log_anomalies": log_top[selected_columns].to_dict(
            orient="records"
        )
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8"
    )
    print(json.dumps({
        "flows_compared": report["flows_compared"],
        "original_anomalies": report["original_anomalies"],
        "log_anomalies": report["log_anomalies"],
        "flagged_by_both": report["flagged_by_both"],
        "original_only": report["original_only"],
        "log_only": report["log_only"],
        "report_path": str(REPORT_PATH)
    }, indent=2))
if __name__ == "__main__":
    main()