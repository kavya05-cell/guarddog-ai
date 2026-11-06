
import json
from datetime import datetime

import pandas as pd
from kafka import KafkaConsumer, TopicPartition
from kafka.serializer import Deserializer

from src.drift.detector import detect_drift

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-telco-drifted"
REFERENCE_DATASET = "data/processed/telco_clean.csv"
REPORT_PATH = "data/processed/streaming_drift_report.json"
BATCH_SIZE = 100
EXPECTED_RECORDS = 7043


class JSONDeserializer(Deserializer):
    def deserialize(self, topic, headers, data):
        return json.loads(data.decode("utf-8"))


consumer = KafkaConsumer(
    bootstrap_servers=KAFKA_SERVER,
    enable_auto_commit=False,
    value_deserializer=JSONDeserializer()
)

partition = TopicPartition(TOPIC_NAME, 0)
consumer.assign([partition])
consumer.seek(partition, 0)

print("Consumer assigned to partition 0 at offset 0.", flush=True)

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

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"\nBatch {batch_number}", flush=True)
    print(f"Records: {len(current_df)}", flush=True)
    print(f"Stable: {stable}", flush=True)
    print(f"Warning: {warning}", flush=True)
    print(f"Alert: {alert}", flush=True)
    print(f"Overall Status: {overall_status.upper()}", flush=True)


try:
    while total_records < EXPECTED_RECORDS:
        messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)

        for _, message_list in messages.items():
            for message in message_list:
                records.append(message.value)
                total_records += 1

                if len(records) == BATCH_SIZE:
                    batch_number += 1
                    process_batch(records, batch_number)
                    records = []

                if total_records >= EXPECTED_RECORDS:
                    break

            if total_records >= EXPECTED_RECORDS:
                break

    if records:
        batch_number += 1
        process_batch(records, batch_number)

finally:
    consumer.close()

print(f"\nTotal records processed: {total_records}", flush=True)
print(f"Total batches processed: {batch_number}", flush=True)
