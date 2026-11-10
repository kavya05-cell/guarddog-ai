import pandas as pd

from src.streaming.network.network_anomaly_detector import (
    FEATURE_COLUMNS,
    extract_features,
    prepare_feature_frame
)


def test_extract_features_returns_all_expected_columns():
    flow = {
        "flow_duration": 2,
        "total_packets": 10,
        "total_bytes": 500
    }

    features = extract_features(flow)

    assert list(features.keys()) == FEATURE_COLUMNS
    assert features["flow_duration"] == 2.0
    assert features["total_packets"] == 10.0
    assert features["total_bytes"] == 500.0


def test_missing_features_default_to_zero():
    features = extract_features({})

    assert len(features) == len(FEATURE_COLUMNS)
    assert all(value == 0.0 for value in features.values())


def test_invalid_values_default_to_zero():
    flow = {
        "flow_duration": "invalid",
        "total_packets": None,
        "total_bytes": 100
    }

    features = extract_features(flow)

    assert features["flow_duration"] == 0.0
    assert features["total_packets"] == 0.0
    assert features["total_bytes"] == 100.0


def test_feature_frame_replaces_nan_and_infinity():
    flows = [
        {
            "flow_duration": float("nan"),
            "total_packets": float("inf"),
            "total_bytes": float("-inf")
        }
    ]

    frame = prepare_feature_frame(flows)

    assert list(frame.columns) == FEATURE_COLUMNS
    assert frame.isna().sum().sum() == 0
    assert (frame == float("inf")).sum().sum() == 0
    assert (frame == float("-inf")).sum().sum() == 0


def test_feature_frame_handles_multiple_flows():
    flows = [
        {"total_packets": 5},
        {"total_packets": 10}
    ]

    frame = prepare_feature_frame(flows)

    assert isinstance(frame, pd.DataFrame)
    assert len(frame) == 2
    assert frame["total_packets"].tolist() == [5.0, 10.0]
