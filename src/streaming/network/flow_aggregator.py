
import json
import sys
from datetime import datetime, timezone

flows = {}


def flow_key(record):
    source = (record.get("src_ip"), record.get("src_port"))
    destination = (record.get("dst_ip"), record.get("dst_port"))
    return record.get("protocol"), tuple(sorted((source, destination)))


def process_record(record):
    if not record.get("src_ip") or not record.get("dst_ip"):
        return

    try:
        packet_time = datetime.fromisoformat(
            record["timestamp"].replace("Z", "+00:00")
        ).timestamp()
    except (KeyError, ValueError, TypeError):
        return

    key = flow_key(record)
    source = (record.get("src_ip"), record.get("src_port"))
    size = int(record.get("packet_size", 0))

    if key not in flows:
        flows[key] = {
            "first_seen": packet_time,
            "last_seen": packet_time,
            "protocol": record.get("protocol"),
            "src_ip": record.get("src_ip"),
            "dst_ip": record.get("dst_ip"),
            "src_port": record.get("src_port"),
            "dst_port": record.get("dst_port"),
            "forward_source": source,
            "total_packets": 0,
            "total_bytes": 0,
            "forward_packets": 0,
            "backward_packets": 0,
            "forward_bytes": 0,
            "backward_bytes": 0
        }

    flow = flows[key]
    flow["first_seen"] = min(flow["first_seen"], packet_time)
    flow["last_seen"] = max(flow["last_seen"], packet_time)
    flow["total_packets"] += 1
    flow["total_bytes"] += size

    if source == flow["forward_source"]:
        flow["forward_packets"] += 1
        flow["forward_bytes"] += size
    else:
        flow["backward_packets"] += 1
        flow["backward_bytes"] += size


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


def main():
    for line in sys.stdin:
        try:
            process_record(json.loads(line))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    for flow in flows.values():
        print(json.dumps(build_flow_record(flow)), flush=True)


if __name__ == "__main__":
    main()
