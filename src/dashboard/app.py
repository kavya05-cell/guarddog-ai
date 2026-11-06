
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.fairness.audit import run_fairness_audit


REPORT_PATH = Path("data/processed/streaming_drift_report.json")
TELCO_DATA_PATH = Path("data/processed/telco_clean.csv")


st.set_page_config(
    page_title="GuardDog AI",
    page_icon="🛡️",
    layout="wide"
)


@st.fragment(run_every=5)
def dashboard():
    if not REPORT_PATH.exists():
        st.error("Streaming drift report not found.")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        report = json.load(file)

    if not report:
        st.warning("No streaming batches are available.")
        return

    latest_batch = report[-1]

    st.title("GuardDog AI")
    st.caption("Continuous Model Integrity and Observability Pipeline")

    st.header("Current Health")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Overall Status",
        latest_batch["overall_status"].upper()
    )

    col2.metric(
        "Records Processed",
        sum(batch["records"] for batch in report)
    )

    col3.metric(
        "Batches Processed",
        len(report)
    )

    col4.metric(
        "Stable",
        latest_batch["stable"]
    )

    col5.metric(
        "Alerts",
        latest_batch["alert"]
    )

    st.divider()

    st.header("Drift Status Over Time")

    trend_data = []

    for batch in report:
        trend_data.append({
            "Batch": batch["batch_number"],
            "Stable": batch["stable"],
            "Warning": batch["warning"],
            "Alert": batch["alert"]
        })

    trend_df = pd.DataFrame(trend_data)

    fig = px.line(
        trend_df,
        x="Batch",
        y=["Stable", "Warning", "Alert"],
        markers=True,
        title="Drift Status by Batch"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.header("Latest Batch Analysis")

    numerical_rows = []
    categorical_rows = []

    for feature, tests in latest_batch["results"].get("numerical", {}).items():
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

    for feature, tests in latest_batch["results"].get("categorical", {}).items():
        chi_square = tests.get("chi_square", {})

        categorical_rows.append({
            "Feature": feature,
            "Chi-Square Statistic": chi_square.get("statistic"),
            "P-Value": chi_square.get("p_value"),
            "Status": chi_square.get("status")
        })

    st.subheader("Numerical Features")

    if numerical_rows:
        numerical_df = pd.DataFrame(numerical_rows)

        st.dataframe(
            numerical_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No numerical drift results available.")

    st.subheader("Categorical Features")

    if categorical_rows:
        categorical_df = pd.DataFrame(categorical_rows)

        st.dataframe(
            categorical_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No categorical drift results available.")

    st.divider()

    st.header("Batch Details")

    batch_numbers = [
        batch["batch_number"]
        for batch in report
    ]

    selected_batch_number = st.selectbox(
        "Select Batch",
        batch_numbers,
        index=len(batch_numbers) - 1
    )

    selected_batch = next(
        batch
        for batch in report
        if batch["batch_number"] == selected_batch_number
    )

    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)

    detail_col1.metric(
        "Batch",
        selected_batch["batch_number"]
    )

    detail_col2.metric(
        "Records",
        selected_batch["records"]
    )

    detail_col3.metric(
        "Warnings",
        selected_batch["warning"]
    )

    detail_col4.metric(
        "Alerts",
        selected_batch["alert"]
    )

    st.write(
        f"Timestamp: {selected_batch['timestamp']}"
    )

    st.write(
        f"Overall Status: {selected_batch['overall_status'].upper()}"
    )

    st.subheader("Detected Drift")

    selected_rows = []

    for feature, tests in selected_batch["results"].get("numerical", {}).items():
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

    for feature, tests in selected_batch["results"].get("categorical", {}).items():
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
        selected_df = pd.DataFrame(selected_rows)

        st.dataframe(
            selected_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(
            "No warning or alert drift detected in this batch."
        )

    st.divider()

    st.header("Outcome Disparity Audit")

    st.caption(
        "This section compares observed churn outcomes across demographic "
        "groups. It measures outcome disparities in the dataset and does "
        "not establish whether a trained model's predictions are fair."
    )

    if not TELCO_DATA_PATH.exists():
        st.warning("Cleaned Telco dataset not found.")
    else:
        try:
            fairness_df = pd.read_csv(TELCO_DATA_PATH)
            fairness_results = run_fairness_audit(fairness_df)

            overall_churn_rate = fairness_df["Churn Value"].mean() * 100

            fairness_col1, fairness_col2 = st.columns(2)

            fairness_col1.metric(
                "Customers Audited",
                f"{len(fairness_df):,}"
            )

            fairness_col2.metric(
                "Overall Churn Rate",
                f"{overall_churn_rate:.2f}%"
            )

            for audit_name, audit_data in fairness_results.items():
                st.subheader(audit_name)

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.write("Group Churn Metrics")

                    st.dataframe(
                        audit_data["group_metrics"].round(3),
                        use_container_width=True,
                        hide_index=True
                    )

                with metric_col2:
                    st.write("Churn Rate Ratios")

                    st.dataframe(
                        audit_data["rate_ratios"].round(3),
                        use_container_width=True,
                        hide_index=True
                    )

        except Exception as error:
            st.error(
                f"Unable to generate fairness audit: {error}"
            )


dashboard()
