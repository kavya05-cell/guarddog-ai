import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.fairness.audit import run_fairness_audit

TELCO_REPORT_PATH = Path("data/processed/streaming_drift_report.json")
TELCO_DATA_PATH = Path("data/processed/telco_clean.csv")

NETWORK_SUMMARY_PATH = Path("data/processed/network_traffic_summary.json")
NETWORK_DRIFT_PATH = Path("data/processed/network_drift_report.json")
NETWORK_HISTORY_PATH = Path("data/processed/network_drift_history.jsonl")
NETWORK_ALERT_PATH = Path("data/processed/network_anomaly_alerts.jsonl")

st.set_page_config(
    page_title="GuardDog AI",
    page_icon="🛡️",
    layout="wide"
)


def load_json(path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def load_jsonl(path, limit=200):
    if not path.exists():
        return []

    records = []

    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return []

    return records[-limit:]


def render_telco_monitoring():
    st.title("Model Monitoring")
    st.caption("Telco Data Drift Detection and Fairness Monitoring")

    report = load_json(TELCO_REPORT_PATH)

    if not report:
        st.warning("Telco streaming drift report not found or empty.")
        return

    latest_batch = report[-1]

    st.header("Current Model Health")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Overall Status",
        latest_batch.get("overall_status", "N/A").upper()
    )

    col2.metric(
        "Records Processed",
        sum(batch.get("records", 0) for batch in report)
    )

    col3.metric(
        "Batches Processed",
        len(report)
    )

    col4.metric(
        "Stable",
        latest_batch.get("stable", 0)
    )

    col5.metric(
        "Alerts",
        latest_batch.get("alert", 0)
    )

    st.divider()

    st.header("Drift Status Over Time")

    trend_data = [
        {
            "Batch": batch.get("batch_number"),
            "Stable": batch.get("stable", 0),
            "Warning": batch.get("warning", 0),
            "Alert": batch.get("alert", 0)
        }
        for batch in report
    ]

    trend_df = pd.DataFrame(trend_data)

    if not trend_df.empty:
        fig = px.line(
            trend_df,
            x="Batch",
            y=["Stable", "Warning", "Alert"],
            markers=True,
            title="Drift Status by Batch"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.header("Latest Batch Analysis")

    numerical_rows = []
    categorical_rows = []

    for feature, tests in latest_batch.get("results", {}).get(
        "numerical", {}
    ).items():
        ks = tests.get("ks", {})
        psi = tests.get("psi", {})

        numerical_rows.append({
            "Feature": feature,
            "KS Statistic": ks.get("statistic"),
            "KS P-Value": ks.get("p_value"),
            "KS Status": ks.get("status"),
            "PSI": psi.get("psi"),
            "PSI Status": psi.get("status")
        })

    for feature, tests in latest_batch.get("results", {}).get(
        "categorical", {}
    ).items():
        chi_square = tests.get("chi_square", {})

        categorical_rows.append({
            "Feature": feature,
            "Chi-Square Statistic": chi_square.get("statistic"),
            "P-Value": chi_square.get("p_value"),
            "Status": chi_square.get("status")
        })

    st.subheader("Numerical Features")

    if numerical_rows:
        st.dataframe(
            pd.DataFrame(numerical_rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No numerical drift results available.")

    st.subheader("Categorical Features")

    if categorical_rows:
        st.dataframe(
            pd.DataFrame(categorical_rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No categorical drift results available.")

    st.divider()

    st.header("Batch Details")

    batch_numbers = [
        batch.get("batch_number")
        for batch in report
    ]

    selected_batch_number = st.selectbox(
        "Select Batch",
        batch_numbers,
        index=len(batch_numbers) - 1,
        key="telco_batch"
    )

    selected_batch = next(
        batch for batch in report
        if batch.get("batch_number") == selected_batch_number
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Batch", selected_batch.get("batch_number"))
    col2.metric("Records", selected_batch.get("records", 0))
    col3.metric("Warnings", selected_batch.get("warning", 0))
    col4.metric("Alerts", selected_batch.get("alert", 0))

    st.write(f"Timestamp: {selected_batch.get('timestamp', 'N/A')}")
    st.write(
        f"Overall Status: "
        f"{selected_batch.get('overall_status', 'N/A').upper()}"
    )

    st.subheader("Detected Drift")

    selected_rows = []

    for feature, tests in selected_batch.get("results", {}).get(
        "numerical", {}
    ).items():
        for test_name, result in tests.items():
            if result.get("status") != "stable":
                selected_rows.append({
                    "Feature": feature,
                    "Test": test_name.upper(),
                    "Value": result.get(
                        "statistic",
                        result.get("psi")
                    ),
                    "P-Value": result.get("p_value"),
                    "Status": result.get("status")
                })

    for feature, tests in selected_batch.get("results", {}).get(
        "categorical", {}
    ).items():
        for test_name, result in tests.items():
            if result.get("status") != "stable":
                selected_rows.append({
                    "Feature": feature,
                    "Test": test_name.upper(),
                    "Value": result.get("statistic"),
                    "P-Value": result.get("p_value"),
                    "Status": result.get("status")
                })

    if selected_rows:
        st.dataframe(
            pd.DataFrame(selected_rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No warning or alert drift detected in this batch.")

    st.divider()

    st.header("Outcome Disparity Audit")

    st.caption(
        "This section compares observed churn outcomes across "
        "demographic groups. It does not establish whether a "
        "trained model's predictions are fair."
    )

    if not TELCO_DATA_PATH.exists():
        st.warning("Cleaned Telco dataset not found.")
        return

    try:
        fairness_df = pd.read_csv(TELCO_DATA_PATH)
        fairness_results = run_fairness_audit(fairness_df)

        overall_churn_rate = fairness_df["Churn Value"].mean() * 100

        col1, col2 = st.columns(2)

        col1.metric("Customers Audited", f"{len(fairness_df):,}")
        col2.metric("Overall Churn Rate", f"{overall_churn_rate:.2f}%")

        for audit_name, audit_data in fairness_results.items():
            st.subheader(audit_name)

            col1, col2 = st.columns(2)

            with col1:
                st.write("Group Churn Metrics")
                st.dataframe(
                    audit_data["group_metrics"].round(3),
                    use_container_width=True,
                    hide_index=True
                )

            with col2:
                st.write("Churn Rate Ratios")
                st.dataframe(
                    audit_data["rate_ratios"].round(3),
                    use_container_width=True,
                    hide_index=True
                )

    except Exception as error:
        st.error(f"Unable to generate fairness audit: {error}")


def render_network_monitoring():
    st.title("Network Monitoring")
    st.caption("Real-Time Network Traffic and Drift Monitoring")

    summary = load_json(NETWORK_SUMMARY_PATH)

    if summary is None:
        st.error("Network traffic summary not found. Start the Kafka consumer.")
        return

    total_flows = summary.get("total_flows", 0)
    anomalous_flows = summary.get("anomalous_flows", 0)
    total_packets = summary.get("total_packets", 0)
    total_bytes = summary.get("total_bytes", 0)

    normal_flows = max(total_flows - anomalous_flows, 0)

    anomaly_rate = (
        anomalous_flows / total_flows * 100
        if total_flows else 0
    )

    drift_report = load_json(NETWORK_DRIFT_PATH)

    drift_status = (
        drift_report.get("overall_status", "unavailable")
        if drift_report else "unavailable"
    )

    st.header("Current Network Health")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Flows", f"{total_flows:,}")
    col2.metric("Anomalous Flows", f"{anomalous_flows:,}")
    col3.metric("Normal Flows", f"{normal_flows:,}")
    col4.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")
    col5.metric("Drift Status", drift_status.upper())

    st.caption(
        f"Consumer started: {summary.get('started_at', 'N/A')} | "
        f"Last updated: {summary.get('last_updated', 'N/A')}"
    )

    st.divider()

    st.header("Network Traffic Statistics")

    col1, col2 = st.columns(2)

    col1.metric("Total Packets", f"{total_packets:,}")
    col2.metric("Total Traffic", f"{total_bytes / (1024 * 1024):.2f} MB")

    st.divider()

    st.header("Traffic Overview")

    protocol_counts = summary.get("protocol_counts", {})

    if protocol_counts:
        protocol_df = pd.DataFrame(
            list(protocol_counts.items()),
            columns=["Protocol", "Flows"]
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                protocol_df,
                names="Protocol",
                values="Flows",
                title="Network Flows by Protocol",
                hole=0.45
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                protocol_df,
                x="Protocol",
                y="Flows",
                title="Protocol Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No protocol data available.")

    st.divider()

    st.header("Network Drift Analysis")

    if drift_report is None:
        st.warning("Network drift report not available yet.")
    else:
        st.write(
            f"Latest batch: {drift_report.get('batch_number', 'N/A')} | "
            f"Timestamp: {drift_report.get('timestamp', 'N/A')}"
        )

        st.write(
            f"Reference flows: "
            f"{drift_report.get('reference_rows', 0):,} | "
            f"Current batch: {drift_report.get('current_rows', 0):,}"
        )

        st.subheader("Numerical Feature Drift")

        numerical_rows = []

        for feature, tests in drift_report.get(
            "results", {}
        ).get("numerical", {}).items():

            ks = tests.get("ks", {})
            psi = tests.get("psi", {})

            numerical_rows.append({
                "Feature": feature,
                "KS Statistic": ks.get("statistic"),
                "KS P-Value": ks.get("p_value"),
                "KS Status": ks.get("status"),
                "PSI": psi.get("psi"),
                "PSI Status": psi.get("status")
            })

        if numerical_rows:
            numerical_df = pd.DataFrame(numerical_rows)

            st.dataframe(
                numerical_df,
                use_container_width=True,
                hide_index=True
            )

            psi_df = numerical_df.dropna(subset=["PSI"])

            if not psi_df.empty:
                fig = px.bar(
                    psi_df,
                    x="Feature",
                    y="PSI",
                    color="PSI Status",
                    title="Population Stability Index by Feature",
                    hover_data=["KS P-Value"]
                )

                fig.add_hline(
                    y=0.10,
                    line_dash="dash",
                    annotation_text="Warning threshold"
                )

                fig.add_hline(
                    y=0.25,
                    line_dash="dash",
                    annotation_text="Alert threshold"
                )

                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Categorical Feature Drift")

        categorical_rows = []

        for feature, tests in drift_report.get(
            "results", {}
        ).get("categorical", {}).items():

            result = tests.get("chi_square", {})

            categorical_rows.append({
                "Feature": feature,
                "Chi-Square Statistic": result.get("statistic"),
                "P-Value": result.get("p_value"),
                "Status": result.get("status")
            })

        if categorical_rows:
            st.dataframe(
                pd.DataFrame(categorical_rows),
                use_container_width=True,
                hide_index=True
            )

        st.subheader("Detected Drift Features")

        detected_rows = []

        for feature, tests in drift_report.get(
            "results", {}
        ).get("numerical", {}).items():

            for test_name, result in tests.items():
                if result.get("status") in ("warning", "alert"):
                    detected_rows.append({
                        "Feature": feature,
                        "Test": test_name.upper(),
                        "Value": result.get(
                            "psi",
                            result.get("statistic")
                        ),
                        "P-Value": result.get("p_value"),
                        "Status": result.get("status")
                    })

        for feature, tests in drift_report.get(
            "results", {}
        ).get("categorical", {}).items():

            for test_name, result in tests.items():
                if result.get("status") in ("warning", "alert"):
                    detected_rows.append({
                        "Feature": feature,
                        "Test": test_name.upper(),
                        "Value": result.get("statistic"),
                        "P-Value": result.get("p_value"),
                        "Status": result.get("status")
                    })

        if detected_rows:
            st.dataframe(
                pd.DataFrame(detected_rows),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No drift warnings or alerts in the latest batch.")

    st.divider()

    st.header("Historical Network Drift")

    history = load_jsonl(NETWORK_HISTORY_PATH, limit=200)

    if history:
        history_df = pd.DataFrame(history)

        if "overall_status" in history_df.columns:
            history_df["overall_status"] = (
                history_df["overall_status"].str.upper()
            )

            fig = px.scatter(
                history_df,
                x="batch_number",
                y="overall_status",
                color="overall_status",
                title="Network Drift Status by Batch",
                hover_data=["timestamp", "current_rows"]
            )

            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            history_df[
                [
                    column for column in [
                        "batch_number",
                        "timestamp",
                        "current_rows",
                        "overall_status"
                    ]
                    if column in history_df.columns
                ]
            ].sort_values("batch_number", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No historical network drift batches available yet.")

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

    alerts = load_jsonl(NETWORK_ALERT_PATH, limit=100)

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
        st.success("No anomaly alerts recorded.")


@st.fragment(run_every=5)
def dashboard():
    st.title("🛡️ GuardDog AI")
    st.caption("Continuous Model Integrity and Network Observability")

    model_tab, network_tab = st.tabs([
        "Model Monitoring",
        "Network Monitoring"
    ])

    with model_tab:
        render_telco_monitoring()

    with network_tab:
        render_network_monitoring()


dashboard()