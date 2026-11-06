
import pandas as pd

FEATURE_COLUMNS = [
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


def extract_features(flow):
    features = {}

    for column in FEATURE_COLUMNS:
        value = flow.get(column, 0)

        try:
            features[column] = float(value)
        except (TypeError, ValueError):
            features[column] = 0.0

    return features


def prepare_feature_frame(flows):
    records = [extract_features(flow) for flow in flows]

    frame = pd.DataFrame(records, columns=FEATURE_COLUMNS)
    frame = frame.replace([float("inf"), float("-inf")], 0).fillna(0)

    return frame
