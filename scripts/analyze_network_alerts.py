
import pandas as pd

FLOW_PATH = "data/processed/network_flows.jsonl"
ALERT_PATH = "data/processed/network_anomaly_alerts.jsonl"

FEATURES = [
    "flow_duration",
    "total_packets",
    "total_bytes",
    "packets_per_second",
    "bytes_per_second",
    "forward_packets",
    "backward_packets",
    "forward_bytes",
    "backward_bytes"
]

flows = pd.read_json(FLOW_PATH, lines=True)
alerts = pd.read_json(ALERT_PATH, lines=True)

alerts["flow_timestamp"] = pd.to_datetime(
    alerts["flow_timestamp"], utc=True
)
flows["timestamp"] = pd.to_datetime(
    flows["timestamp"], utc=True
)

alerts["flow_key"] = (
    alerts["flow_timestamp"].astype(str)
    + alerts["src_ip"].astype(str)
    + alerts["dst_ip"].astype(str)
    + alerts["src_port"].astype(str)
    + alerts["dst_port"].astype(str)
)

flows["flow_key"] = (
    flows["timestamp"].astype(str)
    + flows["src_ip"].astype(str)
    + flows["dst_ip"].astype(str)
    + flows["src_port"].astype(str)
    + flows["dst_port"].astype(str)
)

anomalies = flows[flows["flow_key"].isin(alerts["flow_key"])].copy()
normal = flows[~flows["flow_key"].isin(alerts["flow_key"])].copy()

print("Matched anomaly flows:", len(anomalies))
print("Normal flows:", len(normal))

print("\nANOMALOUS FLOW FEATURE SUMMARY")
print(
    anomalies[FEATURES]
    .describe(percentiles=[0.5, 0.75, 0.9, 0.95])
    .round(2)
    .to_string()
)

print("\nNORMAL FLOW FEATURE SUMMARY")
print(
    normal[FEATURES]
    .describe(percentiles=[0.5, 0.75, 0.9, 0.95])
    .round(2)
    .to_string()
)
