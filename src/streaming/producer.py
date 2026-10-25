import json
import os
import time

from dotenv import load_dotenv
from kafka import KafkaProducer

from src.streaming.simulator import stream_records

load_dotenv()

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-telco-drifted"
DATA_SOURCE = os.getenv("DATA_SOURCE", "telco")

DATASETS = {
    "telco": "data/processed/telco_drifted.csv"
}

if DATA_SOURCE not in DATASETS:
    raise ValueError(f"Unsupported DATA_SOURCE: {DATA_SOURCE}")

DATASET_PATH = DATASETS[DATA_SOURCE]
RECORD_DELAY = 0.05

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

total_records = 0

for record in stream_records(DATASET_PATH):
    producer.send(TOPIC_NAME, value=record)
    total_records += 1
    time.sleep(RECORD_DELAY)

producer.flush()
producer.close()

print(f"Data source: {DATA_SOURCE}")
print(f"Sent {total_records} records to Kafka topic '{TOPIC_NAME}'.")