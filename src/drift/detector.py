import math

import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp


PSI_EPSILON = 1e-8

KS_WARNING_THRESHOLD = 0.05
KS_ALERT_THRESHOLD = 0.01

PSI_WARNING_THRESHOLD = 0.10
PSI_ALERT_THRESHOLD = 0.25

EXCLUDED_COLUMNS = {
    "Customer ID",
    "Location ID",
    "Service ID",
    "Status ID",
    "ID",
    "Count",
    "Count_location",
    "Count_services",
    "Count_status"
}


def ks_test(reference, current):
    reference = reference.dropna()
    current = current.dropna()

    statistic, p_value = ks_2samp(reference, current)

    if p_value < KS_ALERT_THRESHOLD:
        status = "alert"
    elif p_value < KS_WARNING_THRESHOLD:
        status = "warning"
    else:
        status = "stable"

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "status": status
    }


def create_psi_bins(reference, bins=10):
    quantiles = reference.quantile(
        [i / bins for i in range(bins + 1)]
    ).drop_duplicates()

    if len(quantiles) < 3:
        return None

    return quantiles.tolist()


def calculate_psi(reference, current, bins=10):
    reference = reference.dropna()
    current = current.dropna()

    bin_edges = create_psi_bins(reference, bins)

    if bin_edges is None:
        return {
            "psi": 0.0,
            "status": "stable"
        }

    reference_distribution = pd.cut(
        reference,
        bins=bin_edges,
        include_lowest=True
    ).value_counts(normalize=True, sort=False)

    current_distribution = pd.cut(
        current,
        bins=bin_edges,
        include_lowest=True
    ).value_counts(normalize=True, sort=False)

    reference_distribution = reference_distribution + PSI_EPSILON
    current_distribution = current_distribution + PSI_EPSILON

    psi = (
        (current_distribution - reference_distribution)
        * (
            current_distribution / reference_distribution
        ).apply(math.log)
    ).sum()

    if psi > PSI_ALERT_THRESHOLD:
        status = "alert"
    elif psi >= PSI_WARNING_THRESHOLD:
        status = "warning"
    else:
        status = "stable"

    return {
        "psi": float(psi),
        "status": status
    }


def chi_square_test(reference, current):
    reference_counts = reference.fillna("__MISSING__").value_counts()
    current_counts = current.fillna("__MISSING__").value_counts()

    categories = sorted(
        set(reference_counts.index).union(current_counts.index),
        key=str
    )

    reference_values = [
        reference_counts.get(category, 0)
        for category in categories
    ]

    current_values = [
        current_counts.get(category, 0)
        for category in categories
    ]

    table = [
        reference_values,
        current_values
    ]

    statistic, p_value, _, _ = chi2_contingency(table)

    if p_value < KS_ALERT_THRESHOLD:
        status = "alert"
    elif p_value < KS_WARNING_THRESHOLD:
        status = "warning"
    else:
        status = "stable"

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "status": status
    }


def detect_drift(reference_df, current_df):
    results = {
        "numerical": {},
        "categorical": {}
    }

    numerical_columns = [
        column
        for column in reference_df.select_dtypes(include="number").columns
        if column not in EXCLUDED_COLUMNS
    ]

    categorical_columns = [
        column
        for column in reference_df.select_dtypes(exclude="number").columns
        if column not in EXCLUDED_COLUMNS
    ]

    for column in numerical_columns:
        if column not in current_df.columns:
            continue

        results["numerical"][column] = {
            "ks": ks_test(
                reference_df[column],
                current_df[column]
            ),
            "psi": calculate_psi(
                reference_df[column],
                current_df[column]
            )
        }

    for column in categorical_columns:
        if column not in current_df.columns:
            continue

        results["categorical"][column] = {
            "chi_square": chi_square_test(
                reference_df[column],
                current_df[column]
            )
        }

    return results