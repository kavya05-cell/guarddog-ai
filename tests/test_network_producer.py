from scapy.all import IP, TCP

from src.streaming.network import network_producer


def setup_function():
    network_producer.flows.clear()


def test_bidirectional_packets_are_grouped_into_one_flow():
    forward = (
        IP(src="192.168.1.10", dst="192.168.1.20")
        / TCP(sport=50000, dport=443)
    )
    forward.time = 1767261600.0

    backward = (
        IP(src="192.168.1.20", dst="192.168.1.10")
        / TCP(sport=443, dport=50000)
    )
    backward.time = 1767261602.0

    network_producer.process_packet(forward)
    network_producer.process_packet(backward)

    assert len(network_producer.flows) == 1

    flow = next(iter(network_producer.flows.values()))

    assert flow["total_packets"] == 2
    assert flow["forward_packets"] == 1
    assert flow["backward_packets"] == 1
    assert flow["total_bytes"] == len(forward) + len(backward)
    assert flow["forward_bytes"] == len(forward)
    assert flow["backward_bytes"] == len(backward)
from unittest.mock import Mock

from scapy.all import IP, TCP

from src.streaming.network import network_producer


def setup_function():
    network_producer.flows.clear()


def test_expired_flow_is_published_and_removed(monkeypatch):
    packet = (
        IP(src="192.168.1.10", dst="192.168.1.20")
        / TCP(sport=50000, dport=443)
    )
    packet.time = 1767261600.0

    network_producer.process_packet(packet)

    key = next(iter(network_producer.flows))

    network_producer.flows[key]["last_activity"] = 0

    producer = Mock()

    monkeypatch.setattr(network_producer.time, "monotonic", lambda: 10)

    network_producer.expire_flows(producer)

    producer.send.assert_called_once()
    producer.flush.assert_called_once()

    assert key not in network_producer.flows

    sent_record = producer.send.call_args.kwargs["value"]

    assert sent_record["total_packets"] == 1
    assert sent_record["total_bytes"] == len(packet)
