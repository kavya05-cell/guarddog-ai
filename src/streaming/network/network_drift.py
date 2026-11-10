import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.drift.detector import detect_drift
from src.streaming.network.network_anomaly_detector import (
    FEATURE_COLUMNS,
    extract_features
)

REFERENCE_PATH = Path("data/processed/network_reference.csv")
REPORT_PATH = Path("data/processed/network_drift_report.json")
HISTORY_PATH = Path("data/processed/network_drift_history.jsonl")

DRIFT_BATCH_SIZE = 100


def prepare_network_dataframe(flows):
    records = []

    for flow in flows:
        features = extract_features(flow)
        features["protocol"] = flow.get("protocol", "OTHER")
        records.append(features)

    columns = list(FEATURE_COLUMNS) + ["protocol"]

    return pd.DataFrame(records).reindex(columns=columns)


def get_overall_status(results):
    statuses = []

    for feature in results["numerical"].values():
        statuses.append(feature["ks"]["status"])
        statuses.append(feature["psi"]["status"])

    for feature in results["categorical"].values():
        statuses.append(feature["chi_square"]["status"])

    statuses = [status for status in statuses if status != "unavailable"]

    if not statuses:
        return "unavailable"

    if "alert" in statuses:
        return "alert"

    if "warning" in statuses:
        return "warning"

    return "stable"


def evaluate_network_batch(flows, batch_number):
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(
            f"Network reference dataset not found: {REFERENCE_PATH}. "
            "Run build_network_reference.py first."
        )

    if not flows:
        return None

    reference_df = pd.read_csv(REFERENCE_PATH)
    current_df = prepare_network_dataframe(flows)

    results = detect_drift(reference_df, current_df)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "batch_number": batch_number,
        "reference_dataset": str(REFERENCE_PATH),
        "reference_rows": int(len(reference_df)),
        "current_rows": int(len(current_df)),
        "overall_status": get_overall_status(results),
        "results": results
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(report, default=str) + "\n")

    temporary_path = REPORT_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(report, indent=4, default=str),
        encoding="utf-8"
    )
    temporary_path.replace(REPORT_PATH)

    return report