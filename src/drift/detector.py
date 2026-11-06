import math

import numpy as np
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
    "Count_status",
    "Churn Value"
}


def _status_from_p_value(p_value):
    if p_value < KS_ALERT_THRESHOLD:
        return "alert"
    if p_value < KS_WARNING_THRESHOLD:
        return "warning"
    return "stable"


def ks_test(reference, current):
    reference = pd.to_numeric(reference, errors="coerce").dropna()
    current = pd.to_numeric(current, errors="coerce").dropna()

    if len(reference) == 0 or len(current) == 0:
        return {
            "statistic": None,
            "p_value": None,
            "status": "unavailable"
        }

    statistic, p_value = ks_2samp(reference, current)

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "status": _status_from_p_value(p_value)
    }



def create_psi_bins(reference, bins=10):
    reference = pd.to_numeric(reference, errors="coerce").dropna()

    if reference.empty or reference.nunique() < 2:
        return None

    quantiles = reference.quantile(
        [i / bins for i in range(bins + 1)]
    ).drop_duplicates()

    if len(quantiles) < 2:
        return None

    bin_edges = quantiles.to_numpy(dtype=float, copy=True)

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return None

    return bin_edges.tolist()

def calculate_psi(reference, current, bins=10):
    reference = pd.to_numeric(reference, errors="coerce").dropna()
    current = pd.to_numeric(current, errors="coerce").dropna()

    if reference.empty or current.empty:
        return {
            "psi": None,
            "status": "unavailable"
        }

    bin_edges = create_psi_bins(reference, bins)

    if bin_edges is None:
        if reference.nunique() == 1 and current.nunique() == 1:
            if reference.iloc[0] == current.iloc[0]:
                return {
                    "psi": 0.0,
                    "status": "stable"
                }

        return {
            "psi": None,
            "status": "unavailable"
        }

    reference_bins = pd.cut(
        reference,
        bins=bin_edges,
        include_lowest=True
    )

    current_bins = pd.cut(
        current,
        bins=bin_edges,
        include_lowest=True
    )

    reference_distribution = reference_bins.value_counts(
        normalize=True,
        sort=False
    )

    current_distribution = current_bins.value_counts(
        normalize=True,
        sort=False
    )

    reference_distribution = reference_distribution + PSI_EPSILON
    current_distribution = current_distribution + PSI_EPSILON

    psi = (
        (current_distribution - reference_distribution)
        * np.log(current_distribution / reference_distribution)
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
    reference = reference.fillna("__MISSING__").astype(str)
    current = current.fillna("__MISSING__").astype(str)

    reference_counts = reference.value_counts()
    current_counts = current.value_counts()

    categories = sorted(
        set(reference_counts.index).union(current_counts.index),
        key=str
    )

    if len(categories) < 2 or len(reference) == 0 or len(current) == 0:
        return {
            "statistic": None,
            "p_value": None,
            "status": "unavailable"
        }

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

    if sum(reference_values) == 0 or sum(current_values) == 0:
        return {
            "statistic": None,
            "p_value": None,
            "status": "unavailable"
        }

    statistic, p_value, _, _ = chi2_contingency(table)

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "status": _status_from_p_value(p_value)
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
            results["numerical"][column] = {
                "ks": {
                    "statistic": None,
                    "p_value": None,
                    "status": "unavailable"
                },
                "psi": {
                    "psi": None,
                    "status": "unavailable"
                }
            }
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
            results["categorical"][column] = {
                "chi_square": {
                    "statistic": None,
                    "p_value": None,
                    "status": "unavailable"
                }
            }
            continue

        results["categorical"][column] = {
            "chi_square": chi_square_test(
                reference_df[column],
                current_df[column]
            )
        }

    return results