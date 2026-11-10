import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

SUMMARY_PATH = Path("data/processed/network_traffic_summary.json")
ALERT_LOG_PATH = Path("data/processed/network_anomaly_alerts.jsonl")

st.set_page_config(
    page_title="GuardDog AI | Network Monitor",
    page_icon="🛡️",
    layout="wide"
)


@st.fragment(run_every=3)
def network_dashboard():
    st.title("GuardDog AI")
    st.caption("Live Network Intrusion Detection and Traffic Monitoring")

    if not SUMMARY_PATH.exists():
        st.error("Network traffic summary not found. Start the Kafka consumer first.")
        return

    try:
        with SUMMARY_PATH.open("r", encoding="utf-8") as file:
            summary = json.load(file)
    except (json.JSONDecodeError, OSError):
        st.warning("Network summary is being updated. Retrying...")
        return

    total_flows = summary.get("total_flows", 0)
    anomalous_flows = summary.get("anomalous_flows", 0)
    total_packets = summary.get("total_packets", 0)
    total_bytes = summary.get("total_bytes", 0)
    normal_flows = total_flows - anomalous_flows

    status = "ALERT" if anomalous_flows > 0 else "MONITORING"

    st.header("Current Network Health")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Status", status)
    col2.metric("Flows Processed", f"{total_flows:,}")
    col3.metric("Anomalous Flows", f"{anomalous_flows:,}")
    col4.metric("Total Packets", f"{total_packets:,}")
    col5.metric("Total Traffic", f"{total_bytes / (1024 * 1024):.2f} MB")

    st.caption(
        f"Consumer started: {summary.get('started_at', 'N/A')} | "
        f"Last updated: {summary.get('last_updated', 'N/A')}"
    )

    st.divider()

    st.header("Traffic Overview")

    protocol_counts = summary.get("protocol_counts", {})

    if protocol_counts:
        protocol_df = pd.DataFrame(
            list(protocol_counts.items()),
            columns=["Protocol", "Flows"]
        )

        fig = px.pie(
            protocol_df,
            names="Protocol",
            values="Flows",
            title="Network Flows by Protocol",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No protocol data available yet.")

    st.divider()

    st.header("Top Network Sources and Destinations")

    source_col, port_col = st.columns(2)

    source_counts = summary.get("source_ip_counts", {})
    destination_port_counts = summary.get("destination_port_counts", {})

    with source_col:
        st.subheader("Top Source IPs")

        if source_counts:
            source_df = pd.DataFrame(
                list(source_counts.items()),
                columns=["Source IP", "Flows"]
            ).sort_values("Flows", ascending=True)

            fig = px.bar(
                source_df,
                x="Flows",
                y="Source IP",
                orientation="h",
                title="Flows by Source IP"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No source IP data available.")

    with port_col:
        st.subheader("Top Destination Ports")

        if destination_port_counts:
            port_df = pd.DataFrame(
                list(destination_port_counts.items()),
                columns=["Destination Port", "Flows"]
            ).sort_values("Flows", ascending=True)

            fig = px.bar(
                port_df,
                x="Flows",
                y="Destination Port",
                orientation="h",
                title="Flows by Destination Port"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No destination port data available.")

    st.divider()

    st.header("Recent Network Flows")

    recent_flows = summary.get("recent_flows", [])

    if recent_flows:
        flows_df = pd.DataFrame(recent_flows)

        if "prediction" in flows_df.columns:
            flows_df["prediction"] = flows_df["prediction"].str.upper()

        st.dataframe(
            flows_df.sort_values(
                "timestamp",
                ascending=False,
                na_position="last"
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No network flows have been processed yet.")

    st.divider()

    st.header("Recent Anomaly Alerts")

    if ALERT_LOG_PATH.exists():
        try:
            with ALERT_LOG_PATH.open("r", encoding="utf-8") as file:
                alert_lines = file.readlines()

            alerts = [
                json.loads(line)
                for line in alert_lines[-100:]
                if line.strip()
            ]

            if alerts:
                alerts_df = pd.DataFrame(alerts)

                st.dataframe(
                    alerts_df.sort_values(
                        "timestamp",
                        ascending=False,
                        na_position="last"
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No anomaly alerts recorded.")
        except (json.JSONDecodeError, OSError):
            st.warning("The alert log is being updated. Retry shortly.")
    else:
        st.info("Anomaly alert log not found.")


network_dashboard()
