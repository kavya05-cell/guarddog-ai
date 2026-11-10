import json
from pathlib import Path

import pandas as pd

from src.streaming.network.network_anomaly_detector import (
    FEATURE_COLUMNS,
    extract_features
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

FLOW_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "network_flows.jsonl"
REFERENCE_PATH = PROJECT_ROOT / "data" / "processed" / "network_reference.csv"


def main():
    if not FLOW_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Network flow history not found: {FLOW_LOG_PATH}"
        )

    records = []

    with FLOW_LOG_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                flow = json.loads(line)

                features = extract_features(flow)
                features["protocol"] = flow.get("protocol", "OTHER")

                records.append(features)

            except (json.JSONDecodeError, TypeError, ValueError):
                continue

    if len(records) < 100:
        raise ValueError(
            f"At least 100 valid network flows are required. "
            f"Found {len(records)}."
        )

    columns = list(FEATURE_COLUMNS) + ["protocol"]

    reference_df = pd.DataFrame(records)
    reference_df = reference_df.reindex(columns=columns)

    reference_df = reference_df.replace(
        [float("inf"), float("-inf")],
        float("nan")
    )

    reference_df = reference_df.dropna(
        subset=list(FEATURE_COLUMNS)
    )

    if len(reference_df) < 100:
        raise ValueError(
            "Not enough valid historical flows to build a reference."
        )

    REFERENCE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    reference_df.to_csv(
        REFERENCE_PATH,
        index=False
    )

    print(f"Reference dataset created: {REFERENCE_PATH}")
    print(f"Reference flows: {len(reference_df)}")
    print(f"Reference features: {len(columns)}")


if __name__ == "__main__":
    main()