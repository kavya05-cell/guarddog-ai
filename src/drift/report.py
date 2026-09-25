import json
from pathlib import Path

import pandas as pd

from src.drift.detector import detect_drift


def generate_drift_report(reference_path, current_path, output_path):
    reference_df = pd.read_csv(reference_path)
    current_df = pd.read_csv(current_path)

    results = detect_drift(reference_df, current_df)

    report = {
        "reference_dataset": reference_path,
        "current_dataset": current_path,
        "reference_rows": int(reference_df.shape[0]),
        "current_rows": int(current_df.shape[0]),
        "results": results
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return report


def main():
    reference_path = "data/processed/telco_clean.csv"
    current_path = "data/processed/telco_clean.csv"
    output_path = "data/processed/drift_report.json"

    report = generate_drift_report(
        reference_path,
        current_path,
        output_path
    )

    print(f"Reference rows: {report['reference_rows']}")
    print(f"Current rows: {report['current_rows']}")
    print(f"Drift report saved to: {output_path}")


if __name__ == "__main__":
    main()
    