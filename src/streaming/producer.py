import json
import time

import pandas as pd
from kafka import KafkaProducer

DATASET_PATH = "data/processed/telco_drifted.csv"
KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-telco-drifted"
RECORD_DELAY = 0.05

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

data = pd.read_csv(DATASET_PATH).sample(frac=1, random_state=42).reset_index(drop=True)

for _, row in data.iterrows():
    record = row.where(pd.notna(row), None).to_dict()
    producer.send(TOPIC_NAME, value=record)
    time.sleep(RECORD_DELAY)

producer.flush()
producer.close()

print(f"Sent {len(data)} records to Kafka topic '{TOPIC_NAME}'.")