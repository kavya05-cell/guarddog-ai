from unittest.mock import Mock

from src.streaming.network.network_consumer import (
    score_flow,
    create_summary,
    update_summary
)


def test_score_flow_returns_anomaly():
    model = Mock()
    model.predict.return_value = [-1]
    model.decision_function.return_value = [-0.25]

    flow = {
        "flow_duration": 2,
        "total_packets": 10,
        "total_bytes": 500,
        "packets_per_second": 5,
        "bytes_per_second": 250,
        "forward_packets": 6,
        "backward_packets": 4,
        "forward_bytes": 300,
        "backward_bytes": 200
    }

    prediction, score = score_flow(model, flow)

    assert prediction == "anomaly"
    assert score == -0.25
    model.predict.assert_called_once()
    model.decision_function.assert_called_once()


def test_score_flow_returns_normal():
    model = Mock()
    model.predict.return_value = [1]
    model.decision_function.return_value = [0.15]

    prediction, score = score_flow(model, {})

    assert prediction == "normal"
    assert score == 0.15


def test_summary_counts_flows_packets_bytes_and_anomalies():
    summary = create_summary()

    flow = {
        "protocol": "TCP",
        "src_ip": "192.168.1.10",
        "dst_ip": "192.168.1.20",
        "dst_port": 443,
        "total_packets": 10,
        "total_bytes": 500,
        "flow_duration": 2,
        "timestamp": "2026-01-01T10:00:00+00:00"
    }

    update_summary(summary, flow, "anomaly", -0.25)

    assert summary["total_flows"] == 1
    assert summary["anomalous_flows"] == 1
    assert summary["total_packets"] == 10
    assert summary["total_bytes"] == 500
    assert summary["protocol_counts"]["TCP"] == 1
    assert summary["source_ip_counts"]["192.168.1.10"] == 1
    assert summary["destination_port_counts"]["443"] == 1
    assert summary["recent_flows"][0]["prediction"] == "anomaly"

import json


def test_append_json_line_writes_valid_json(tmp_path):
    path = tmp_path / "flows.jsonl"

    record = {
        "protocol": "TCP",
        "total_packets": 5,
        "prediction": "anomaly"
    }

    from src.streaming.network.network_consumer import append_json_line

    append_json_line(path, record)

    written = json.loads(path.read_text(encoding="utf-8"))

    assert written == record


def test_save_summary_serializes_counters(tmp_path, monkeypatch):
    from src.streaming.network import network_consumer

    output_path = tmp_path / "summary.json"
    monkeypatch.setattr(network_consumer, "OUTPUT_PATH", output_path)

    summary = network_consumer.create_summary()
    flow = {
        "protocol": "UDP",
        "src_ip": "192.168.1.5",
        "dst_ip": "192.168.1.10",
        "dst_port": 53,
        "total_packets": 3,
        "total_bytes": 180,
        "flow_duration": 1.5,
        "timestamp": "2026-01-01T10:00:00+00:00"
    }

    network_consumer.update_summary(summary, flow, "normal", 0.2)
    network_consumer.save_summary(summary)

    saved = json.loads(output_path.read_text(encoding="utf-8"))

    assert saved["total_flows"] == 1
    assert saved["total_packets"] == 3
    assert saved["total_bytes"] == 180
    assert saved["protocol_counts"]["UDP"] == 1
    assert saved["source_ip_counts"]["192.168.1.5"] == 1
    assert saved["destination_port_counts"]["53"] == 1


def test_summary_keeps_only_100_recent_flows():
    from src.streaming.network.network_consumer import (
        create_summary,
        update_summary
    )

    summary = create_summary()

    for index in range(105):
        flow = {
            "protocol": "TCP",
            "src_ip": f"192.168.1.{index}",
            "dst_ip": "192.168.1.20",
            "dst_port": 443,
            "total_packets": 1,
            "total_bytes": 100,
            "flow_duration": 1,
            "timestamp": f"2026-01-01T10:00:{index:02d}+00:00"
        }

        update_summary(summary, flow, "normal", 0.1)

    assert summary["total_flows"] == 105
    assert len(summary["recent_flows"]) == 100
