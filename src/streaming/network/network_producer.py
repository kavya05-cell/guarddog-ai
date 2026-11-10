import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from scapy.all import IP, IPv6, TCP, UDP, ICMP, sniff

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "guarddog-network-live"
FLOW_TIMEOUT = 5
CLEANUP_INTERVAL = 1

DEFAULT_OUTPUT_PATH = Path("data/processed/network_flows.jsonl")

flows = {}


def extract_packet_features(packet):
    timestamp = float(packet.time) if hasattr(packet, "time") else time.time()

    features = {
        "timestamp": datetime.fromtimestamp(
            timestamp, timezone.utc
        ).isoformat(),
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
        features["src_ip"] = packet[IP].src
        features["dst_ip"] = packet[IP].dst
        features["ttl"] = packet[IP].ttl
    elif IPv6 in packet:
        features["src_ip"] = packet[IPv6].src
        features["dst_ip"] = packet[IPv6].dst
        features["ttl"] = packet[IPv6].hlim

    if TCP in packet:
        features["protocol"] = "TCP"
        features["src_port"] = packet[TCP].sport
        features["dst_port"] = packet[TCP].dport
        features["tcp_flags"] = str(packet[TCP].flags)
    elif UDP in packet:
        features["protocol"] = "UDP"
        features["src_port"] = packet[UDP].sport
        features["dst_port"] = packet[UDP].dport
    elif ICMP in packet:
        features["protocol"] = "ICMP"

    return features


def get_flow_key(record):
    source = (record["src_ip"], record["src_port"])
    destination = (record["dst_ip"], record["dst_port"])

    return record["protocol"], tuple(sorted((source, destination)))


def process_packet(packet):
    record = extract_packet_features(packet)

    if not record["src_ip"] or not record["dst_ip"]:
        return

    key = get_flow_key(record)
    source = (record["src_ip"], record["src_port"])
    timestamp = datetime.fromisoformat(record["timestamp"]).timestamp()

    if key not in flows:
        flows[key] = {
            "first_seen": timestamp,
            "last_seen": timestamp,
            "last_activity": time.monotonic(),
            "protocol": record["protocol"],
            "src_ip": record["src_ip"],
            "dst_ip": record["dst_ip"],
            "src_port": record["src_port"],
            "dst_port": record["dst_port"],
            "forward_source": source,
            "total_packets": 0,
            "total_bytes": 0,
            "forward_packets": 0,
            "backward_packets": 0,
            "forward_bytes": 0,
            "backward_bytes": 0
        }

    flow = flows[key]

    flow["first_seen"] = min(flow["first_seen"], timestamp)
    flow["last_seen"] = max(flow["last_seen"], timestamp)
    flow["last_activity"] = time.monotonic()
    flow["total_packets"] += 1
    flow["total_bytes"] += record["packet_size"]

    if source == flow["forward_source"]:
        flow["forward_packets"] += 1
        flow["forward_bytes"] += record["packet_size"]
    else:
        flow["backward_packets"] += 1
        flow["backward_bytes"] += record["packet_size"]


def build_flow_record(flow):
    duration = max(0.0, flow["last_seen"] - flow["first_seen"])

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": flow["protocol"],
        "src_ip": flow["src_ip"],
        "dst_ip": flow["dst_ip"],
        "src_port": flow["src_port"],
        "dst_port": flow["dst_port"],
        "flow_duration": duration,
        "total_packets": flow["total_packets"],
        "total_bytes": flow["total_bytes"],
        "packets_per_second": (
            flow["total_packets"] / duration if duration > 0 else 0.0
        ),
        "bytes_per_second": (
            flow["total_bytes"] / duration if duration > 0 else 0.0
        ),
        "forward_packets": flow["forward_packets"],
        "backward_packets": flow["backward_packets"],
        "forward_bytes": flow["forward_bytes"],
        "backward_bytes": flow["backward_bytes"]
    }


def publish_flow(producer, key, output_file=None):
    flow = flows.pop(key, None)

    if flow is None:
        return

    record = build_flow_record(flow)

    if output_file is not None:
        output_file.write(json.dumps(record) + "\n")
        output_file.flush()

        print(
            f"Saved baseline flow: {record['protocol']} "
            f"{record['src_ip']}:{record['src_port']} -> "
            f"{record['dst_ip']}:{record['dst_port']} "
            f"| packets={record['total_packets']} "
            f"| bytes={record['total_bytes']}",
            flush=True
        )
    else:
        producer.send(TOPIC_NAME, value=record)
        producer.flush()

        print(
            f"Published flow: {record['protocol']} "
            f"{record['src_ip']}:{record['src_port']} -> "
            f"{record['dst_ip']}:{record['dst_port']} "
            f"| packets={record['total_packets']} "
            f"| bytes={record['total_bytes']}",
            flush=True
        )


def expire_flows(producer, output_file=None):
    now = time.monotonic()

    expired = [
        key for key, flow in flows.items()
        if now - flow["last_activity"] >= FLOW_TIMEOUT
    ]

    for key in expired:
        publish_flow(producer, key, output_file)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--interface", required=True)
    parser.add_argument("--duration", type=int, default=0)
    parser.add_argument(
        "--mode",
        choices=["live", "baseline"],
        default="live"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH
    )
    parser.add_argument(
        "--append",
        action="store_true"
    )

    args = parser.parse_args()

    if args.duration < 0:
        parser.error("--duration cannot be negative")

    if args.mode == "baseline" and args.duration <= 0:
        parser.error("Baseline mode requires a positive --duration")

    producer = None
    output_file = None

    if args.mode == "baseline":
        args.output.parent.mkdir(parents=True, exist_ok=True)

        file_mode = "a" if args.append else "w"

        output_file = args.output.open(
            file_mode,
            encoding="utf-8"
        )

        print("Starting network baseline collection.", flush=True)
        print(f"Output file: {args.output}", flush=True)
        print(f"Collection duration: {args.duration} seconds", flush=True)

    else:
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda value: json.dumps(value).encode("utf-8")
        )

        print(f"Publishing to Kafka topic: {TOPIC_NAME}", flush=True)

    start_time = time.monotonic()
    last_cleanup = start_time

    def on_packet(packet):
        process_packet(packet)

    print(f"Capturing on interface: {args.interface}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)

    try:
        while True:
            sniff(
                iface=args.interface,
                count=1,
                timeout=1,
                prn=on_packet,
                store=False
            )

            now = time.monotonic()

            if now - last_cleanup >= CLEANUP_INTERVAL:
                expire_flows(producer, output_file)
                last_cleanup = now

            if args.duration > 0 and now - start_time >= args.duration:
                break

    except KeyboardInterrupt:
        print("Stopping capture.", flush=True)

    finally:
        for key in list(flows):
            publish_flow(producer, key, output_file)

        if producer is not None:
            producer.flush()
            producer.close()

        if output_file is not None:
            output_file.close()

        print("Network capture completed.", flush=True)


if __name__ == "__main__":
    main()