import json
from pathlib import Path

import pandas as pd

from src.streaming.network.network_anomaly_detector import (
    FEATURE_COLUMNS,
    extract_features
)

FLOW_LOG_PATH = Path("data/processed/network_flows.jsonl")
REFERENCE_PATH = Path("data/processed/network_reference.csv")


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

            flow = json.loads(line)
            features = extract_features(flow)
            features["protocol"] = flow.get("protocol", "OTHER")
            records.append(features)

    if len(records) < 100:
        raise ValueError(
            "At least 100 historical network flows are required."
        )

    columns = list(FEATURE_COLUMNS) + ["protocol"]
    reference_df = pd.DataFrame(records)

    reference_df = reference_df.reindex(columns=columns)
    reference_df = reference_df.dropna(subset=list(FEATURE_COLUMNS))

    if len(reference_df) < 100:
        raise ValueError(
            "Not enough valid historical flows to build a reference."
        )

    REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    reference_df.to_csv(REFERENCE_PATH, index=False)

    print(f"Reference dataset created: {REFERENCE_PATH}")
    print(f"Reference flows: {len(reference_df)}")


if __name__ == "__main__":
    main()