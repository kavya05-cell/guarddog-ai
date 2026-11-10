from src.streaming.network import flow_aggregator


def setup_function():
    flow_aggregator.flows.clear()


def test_bidirectional_packets_are_grouped_into_one_flow():
    forward = {
        "timestamp": "2026-01-01T10:00:00+00:00",
        "protocol": "TCP",
        "src_ip": "192.168.1.10",
        "dst_ip": "192.168.1.20",
        "src_port": 50000,
        "dst_port": 443,
        "packet_size": 100
    }

    backward = {
        "timestamp": "2026-01-01T10:00:02+00:00",
        "protocol": "TCP",
        "src_ip": "192.168.1.20",
        "dst_ip": "192.168.1.10",
        "src_port": 443,
        "dst_port": 50000,
        "packet_size": 200
    }

    flow_aggregator.process_record(forward)
    flow_aggregator.process_record(backward)

    assert len(flow_aggregator.flows) == 1

    flow = next(iter(flow_aggregator.flows.values()))

    assert flow["total_packets"] == 2
    assert flow["total_bytes"] == 300
    assert flow["forward_packets"] == 1
    assert flow["backward_packets"] == 1
    assert flow["forward_bytes"] == 100
    assert flow["backward_bytes"] == 200


def test_flow_duration_and_rates_are_calculated():
    first = {
        "timestamp": "2026-01-01T10:00:00+00:00",
        "protocol": "UDP",
        "src_ip": "192.168.1.10",
        "dst_ip": "192.168.1.20",
        "src_port": 50000,
        "dst_port": 53,
        "packet_size": 100
    }

    second = {
        **first,
        "timestamp": "2026-01-01T10:00:04+00:00",
        "packet_size": 300
    }

    flow_aggregator.process_record(first)
    flow_aggregator.process_record(second)

    flow = next(iter(flow_aggregator.flows.values()))
    result = flow_aggregator.build_flow_record(flow)

    assert result["flow_duration"] == 4.0
    assert result["total_packets"] == 2
    assert result["total_bytes"] == 400
    assert result["packets_per_second"] == 0.5
    assert result["bytes_per_second"] == 100.0


def test_invalid_records_are_ignored():
    flow_aggregator.process_record({})
    flow_aggregator.process_record({
        "src_ip": "192.168.1.10",
        "dst_ip": "192.168.1.20"
    })

    assert len(flow_aggregator.flows) == 0


def test_zero_duration_flow_has_zero_rates():
    record = {
        "timestamp": "2026-01-01T10:00:00+00:00",
        "protocol": "TCP",
        "src_ip": "192.168.1.10",
        "dst_ip": "192.168.1.20",
        "src_port": 50000,
        "dst_port": 443,
        "packet_size": 100
    }

    flow_aggregator.process_record(record)

    flow = next(iter(flow_aggregator.flows.values()))
    result = flow_aggregator.build_flow_record(flow)

    assert result["flow_duration"] == 0.0
    assert result["packets_per_second"] == 0.0
    assert result["bytes_per_second"] == 0.0
