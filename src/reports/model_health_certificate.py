import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT_DIR / "data" / "processed" / "streaming_drift_report.json"
OUTPUT_PATH = ROOT_DIR / "data" / "processed" / "model_health_certificate.pdf"


def load_latest_batch():
    with REPORT_PATH.open("r", encoding="utf-8") as file:
        batches = json.load(file)

    if not isinstance(batches, list) or not batches:
        raise ValueError("The streaming drift report must contain a non-empty list.")

    return max(batches, key=lambda batch: batch.get("batch_number", 0))


def extract_feature_statuses(batch):
    feature_rows = []

    results = batch.get("results", {})
    numerical = results.get("numerical", {})
    categorical = results.get("categorical", {})

    for feature, metrics in numerical.items():
        statuses = []

        for metric in metrics.values():
            if isinstance(metric, dict) and metric.get("status"):
                statuses.append(metric["status"])

        feature_status = "stable"

        if "alert" in statuses:
            feature_status = "alert"
        elif "warning" in statuses:
            feature_status = "warning"

        if feature_status != "stable":
            feature_rows.append([feature, feature_status.upper()])

    for feature, metrics in categorical.items():
        statuses = []

        for metric in metrics.values():
            if isinstance(metric, dict) and metric.get("status"):
                statuses.append(metric["status"])

        feature_status = "stable"

        if "alert" in statuses:
            feature_status = "alert"
        elif "warning" in statuses:
            feature_status = "warning"

        if feature_status != "stable":
            feature_rows.append([feature, feature_status.upper()])

    return feature_rows


def build_certificate():
    batch = load_latest_batch()

    batch_number = batch.get("batch_number", "N/A")
    timestamp = batch.get("timestamp", "N/A")
    records = batch.get("records", 0)
    stable = batch.get("stable", 0)
    warning = batch.get("warning", 0)
    alert = batch.get("alert", 0)
    overall_status = str(batch.get("overall_status", "unknown")).upper()

    feature_rows = extract_feature_statuses(batch)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CertificateTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324D"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "CertificateSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#526579"),
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=8,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "CertificateBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#263746"),
    )

    small_style = ParagraphStyle(
        "CertificateSmall",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#526579"),
    )

    status_color = {
        "STABLE": colors.HexColor("#238636"),
        "WARNING": colors.HexColor("#B7791F"),
        "ALERT": colors.HexColor("#B42318"),
    }.get(overall_status, colors.HexColor("#526579"))

    status_style = ParagraphStyle(
        "OverallStatus",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        textColor=status_color,
    )

    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="GuardDog AI Model Health Certificate",
        author="GuardDog AI",
    )

    story = []

    story.append(Paragraph("GUARDDOG AI", title_style))
    story.append(Paragraph("DATA DRIFT HEALTH CERTIFICATE", subtitle_style))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(f"OVERALL DRIFT STATUS: {overall_status}", status_style))
    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            "This certificate summarizes the observed data-distribution health "
            "of the latest monitored batch using the available drift report.",
            body_style,
        )
    )
    story.append(Spacer(1, 5 * mm))

    summary_data = [
        ["Batch Number", str(batch_number), "Records Evaluated", str(records)],
        ["Report Timestamp", str(timestamp), "Stable Checks", str(stable)],
        ["Warning Checks", str(warning), "Alert Checks", str(alert)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[37 * mm, 48 * mm, 37 * mm, 38 * mm],
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6F9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#263746")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DEE7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Drifted Features", heading_style))

    if feature_rows:
        feature_data = [["Feature", "Observed Status"]] + feature_rows

        feature_table = Table(
            feature_data,
            colWidths=[110 * mm, 50 * mm],
            repeatRows=1,
        )

        feature_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DEE7")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                        colors.white,
                        colors.HexColor("#F3F6F9"),
                    ]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(feature_table)
    else:
        story.append(
            Paragraph(
                "No warning or alert features were recorded in the latest batch.",
                body_style,
            )
        )

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Interpretation", heading_style))

    if overall_status == "ALERT":
        interpretation = (
            "The latest monitored batch contains one or more drift alerts. "
            "The data distribution differs materially from the reference "
            "distribution for at least some monitored features. Investigation "
            "is recommended before relying on downstream model outputs."
        )
    elif overall_status == "WARNING":
        interpretation = (
            "The latest monitored batch contains warning-level drift. "
            "Review the affected features and continue monitoring for "
            "persistent or increasing distribution changes."
        )
    elif overall_status == "STABLE":
        interpretation = (
            "The latest monitored batch is classified as stable by the "
            "configured drift checks. This does not guarantee model accuracy "
            "or the absence of operational risk."
        )
    else:
        interpretation = (
            "The report contains an unrecognized overall status. "
            "Review the monitoring output before interpreting this certificate."
        )

    story.append(Paragraph(interpretation, body_style))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Scope and Disclaimer", heading_style))
    story.append(
        Paragraph(
            "This document reports data-distribution drift checks only. "
            "It is not a model accuracy evaluation, security certification, "
            "or proof of intrusion detection performance. Drift can occur "
            "without a corresponding decrease in model performance, and "
            "model performance can degrade without detected drift. "
            "The certificate reflects the selected batch and the monitoring "
            "metrics recorded in the source report.",
            small_style,
        )
    )

    story.append(Spacer(1, 7 * mm))

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(
        Paragraph(
            f"Generated by GuardDog AI | Generated at: {generated_at}",
            small_style,
        )
    )

    document.build(story)


if __name__ == "__main__":
    build_certificate()
    print(f"Certificate generated: {OUTPUT_PATH}")