import argparse
import json
import time
from datetime import datetime, timezone

from scapy.all import IP, IPv6, TCP, UDP, ICMP, sniff


def extract_packet_features(packet):
    timestamp = datetime.now(timezone.utc).isoformat()

    features = {
        "timestamp": timestamp,
        "packet_size": len(packet),
        "protocol": "OTHER",
        "src_ip": None,
        "dst_ip": None,
        "src_port": None,
        "dst_port": None,
        "tcp_flags": None,
        "ttl": None
    }

    if IP in packet:
        ip = packet[IP]
        features["src_ip"] = ip.src
        features["dst_ip"] = ip.dst
        features["ttl"] = ip.ttl
    elif IPv6 in packet:
        ip = packet[IPv6]
        features["src_ip"] = ip.src
        features["dst_ip"] = ip.dst
        features["ttl"] = ip.hlim

    if TCP in packet:
        transport = packet[TCP]
        features["protocol"] = "TCP"
        features["src_port"] = transport.sport
        features["dst_port"] = transport.dport
        features["tcp_flags"] = str(transport.flags)
    elif UDP in packet:
        transport = packet[UDP]
        features["protocol"] = "UDP"
        features["src_port"] = transport.sport
        features["dst_port"] = transport.dport
    elif ICMP in packet:
        features["protocol"] = "ICMP"

    return features


def capture_packets(interface, packet_limit, duration):
    captured = 0
    started_at = time.monotonic()

    def process_packet(packet):
        nonlocal captured

        features = extract_packet_features(packet)
        print(json.dumps(features), flush=True)
        captured += 1

        return packet_limit > 0 and captured >= packet_limit

    def stop_capture(packet):
        if packet_limit > 0 and captured >= packet_limit:
            return True

        return duration > 0 and time.monotonic() - started_at >= duration

    sniff(
        iface=interface,
        prn=process_packet,
        stop_filter=stop_capture,
        store=False,
        timeout=duration if duration > 0 else None
    )

    print(json.dumps({
        "event": "capture_finished",
        "packets_captured": captured
    }), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True)
    parser.add_argument("--count", type=int, default=0)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()

    capture_packets(
        interface=args.interface,
        packet_limit=args.count,
        duration=args.duration
    )
