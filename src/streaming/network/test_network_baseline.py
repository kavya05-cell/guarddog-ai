import json
from pathlib import Path

import joblib
from .network_anomaly_detector import prepare_feature_frame

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "network" / "isolation_forest_baseline.joblib"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "network_flows.jsonl"


def main():
    model = joblib.load(MODEL_PATH)

    with DATA_PATH.open("r", encoding="utf-8") as file:
        flow = json.loads(file.readline())

    features = prepare_feature_frame([flow])

    prediction = int(model.predict(features)[0])
    score = float(model.decision_function(features)[0])

    result = {
        "flow": {
            "protocol": flow.get("protocol"),
            "src_ip": flow.get("src_ip"),
            "dst_ip": flow.get("dst_ip"),
            "src_port": flow.get("src_port"),
            "dst_port": flow.get("dst_port")
        },
        "prediction": "anomaly" if prediction == -1 else "normal",
        "anomaly_score": score
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()