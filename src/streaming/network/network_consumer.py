import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from kafka import KafkaConsumer

from network_anomaly_detector import FEATURE_COLUMNS, extract_features

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-network-live"
OUTPUT_PATH = Path("data/processed/network_traffic_summary.json")
FLOW_LOG_PATH = Path("data/processed/network_flows.jsonl")
ALERT_LOG_PATH = Path("data/processed/network_anomaly_alerts.jsonl")
MODEL_PATH = Path("models/network/isolation_forest_baseline.joblib")
GROUP_ID = "guarddog-network-analysis-v1"


def append_json_line(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def create_summary():
    return {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": None,
        "total_flows": 0,
        "anomalous_flows": 0,
        "total_packets": 0,
        "total_bytes": 0,
        "protocol_counts": Counter(),
        "source_ip_counts": Counter(),
        "destination_port_counts": Counter(),
        "recent_flows": []
    }


def update_summary(summary, flow, prediction, anomaly_score):
    summary["total_flows"] += 1
    summary["total_packets"] += int(flow.get("total_packets", 0))
    summary["total_bytes"] += int(flow.get("total_bytes", 0))
    summary["protocol_counts"][flow.get("protocol", "OTHER")] += 1

    if prediction == "anomaly":
        summary["anomalous_flows"] += 1

    source_ip = flow.get("src_ip")
    if source_ip:
        summary["source_ip_counts"][source_ip] += 1

    destination_port = flow.get("dst_port")
    if destination_port is not None:
        summary["destination_port_counts"][str(destination_port)] += 1

    summary["last_updated"] = datetime.now(timezone.utc).isoformat()

    recent_flow = {
        "timestamp": flow.get("timestamp"),
        "protocol": flow.get("protocol"),
        "src_ip": source_ip,
        "dst_ip": flow.get("dst_ip"),
        "src_port": flow.get("src_port"),
        "dst_port": destination_port,
        "total_packets": flow.get("total_packets", 0),
        "total_bytes": flow.get("total_bytes", 0),
        "flow_duration": flow.get("flow_duration", 0),
        "prediction": prediction,
        "anomaly_score": float(anomaly_score)
    }

    summary["recent_flows"].append(recent_flow)
    summary["recent_flows"] = summary["recent_flows"][-100:]


def save_summary(summary):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output = {
        **summary,
        "protocol_counts": dict(summary["protocol_counts"]),
        "source_ip_counts": dict(summary["source_ip_counts"].most_common(20)),
        "destination_port_counts": dict(
            summary["destination_port_counts"].most_common(20)
        )
    }

    temporary_path = OUTPUT_PATH.with_name(
        f"network_traffic_summary_{__import__('os').getpid()}.tmp"
    )

    temporary_path.write_text(
        json.dumps(output, indent=2, default=str),
        encoding="utf-8"
    )

    for attempt in range(5):
        try:
            temporary_path.replace(OUTPUT_PATH)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2)


def score_flow(model, flow):
    feature_record = extract_features(flow)
    feature_frame = pd.DataFrame(
        [feature_record],
        columns=FEATURE_COLUMNS
    )

    prediction_value = int(model.predict(feature_frame)[0])
    anomaly_score = float(model.decision_function(feature_frame)[0])

    prediction = "anomaly" if prediction_value == -1 else "normal"

    return prediction, anomaly_score


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda data: json.loads(data.decode("utf-8"))
    )

    summary = create_summary()

    print(f"Reading network flows from {TOPIC_NAME}", flush=True)
    print(f"Loaded model from {MODEL_PATH}", flush=True)
    print(f"Writing summary to {OUTPUT_PATH}", flush=True)
    print(f"Writing anomaly alerts to {ALERT_LOG_PATH}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)

    try:
        for message in consumer:
            flow = message.value

            if not isinstance(flow, dict):
                continue

            prediction, anomaly_score = score_flow(model, flow)

            logged_flow = {
                **flow,
                "prediction": prediction,
                "anomaly_score": anomaly_score
            }

            append_json_line(FLOW_LOG_PATH, logged_flow)

            update_summary(
                summary,
                flow,
                prediction,
                anomaly_score
       )

            if prediction == "anomaly":
                alert = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "flow_timestamp": flow.get("timestamp"),
                    "protocol": flow.get("protocol"),
                    "src_ip": flow.get("src_ip"),
                    "dst_ip": flow.get("dst_ip"),
                    "src_port": flow.get("src_port"),
                    "dst_port": flow.get("dst_port"),
                    "total_packets": flow.get("total_packets", 0),
                    "total_bytes": flow.get("total_bytes", 0),
                    "anomaly_score": anomaly_score,
                    "alert": "Unusual network flow detected"
                }

                append_json_line(ALERT_LOG_PATH, alert)

                print(
                    f"ANOMALY | {flow.get('protocol')} | "
                    f"{flow.get('src_ip')}:{flow.get('src_port')} -> "
                    f"{flow.get('dst_ip')}:{flow.get('dst_port')} | "
                    f"Score: {anomaly_score:.6f}",
                    flush=True
                )

            save_summary(summary)

            print(
                f"Flows: {summary['total_flows']} | "
                f"Anomalies: {summary['anomalous_flows']} | "
                f"Packets: {summary['total_packets']} | "
                f"Bytes: {summary['total_bytes']} | "
                f"Protocol: {flow.get('protocol', 'OTHER')}",
                flush=True
            )

    except KeyboardInterrupt:
        print("Stopping network analysis consumer.", flush=True)
    finally:
        save_summary(summary)
        consumer.close()


if __name__ == "__main__":
    main()
