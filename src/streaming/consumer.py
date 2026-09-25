import json
from datetime import datetime

import pandas as pd
from kafka import KafkaConsumer

from src.drift.detector import detect_drift

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-telco-drifted"
REFERENCE_DATASET = "data/processed/telco_clean.csv"
REPORT_PATH = "data/processed/streaming_drift_report.json"
BATCH_SIZE = 100
EXPECTED_RECORDS = 7043

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="guarddog-drift-consumer-v2",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)

reference_df = pd.read_csv(REFERENCE_DATASET)

records = []
batch_number = 0
total_records = 0
report = []

def process_batch(records, batch_number):
    current_df = pd.DataFrame(records)
    results = detect_drift(reference_df, current_df)

    stable = 0
    warning = 0
    alert = 0

    for feature_results in results.values():
        for result in feature_results.values():
            for test_result in result.values():
                status = test_result["status"]

                if status == "stable":
                    stable += 1
                elif status == "warning":
                    warning += 1
                elif status == "alert":
                    alert += 1

    if alert > 0:
        overall_status = "alert"
    elif warning > 0:
        overall_status = "warning"
    else:
        overall_status = "stable"

    batch_report = {
        "batch_number": batch_number,
        "timestamp": datetime.now().isoformat(),
        "records": len(current_df),
        "stable": stable,
        "warning": warning,
        "alert": alert,
        "overall_status": overall_status,
        "results": results
    }

    report.append(batch_report)

    with open(REPORT_PATH, "w") as file:
        json.dump(report, file, indent=4)

    print(f"\nBatch {batch_number}")
    print(f"Records: {len(current_df)}")
    print(f"Stable: {stable}")
    print(f"Warning: {warning}")
    print(f"Alert: {alert}")
    print(f"Overall Status: {overall_status.upper()}")

for message in consumer:
    records.append(message.value)
    total_records += 1

    if len(records) == BATCH_SIZE:
        batch_number += 1
        process_batch(records, batch_number)
        records = []

    if total_records == EXPECTED_RECORDS:
        break

if records:
    batch_number += 1
    process_batch(records, batch_number)

consumer.close()

print(f"\nTotal records processed: {total_records}")
print(f"Total batches processed: {batch_number}")