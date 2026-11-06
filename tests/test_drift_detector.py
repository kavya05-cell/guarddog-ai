import numpy as np
import pandas as pd

from src.drift.detector import detect_drift


def test_identical_data_is_stable():
    reference = pd.DataFrame({
        "Age": np.arange(100),
        "Contract": ["Monthly", "Yearly"] * 50
    })

    current = reference.copy()

    results = detect_drift(reference, current)

    assert results["numerical"]["Age"]["ks"]["status"] == "stable"
    assert results["numerical"]["Age"]["psi"]["status"] == "stable"
    assert results["categorical"]["Contract"]["chi_square"]["status"] == "stable"


def test_numeric_shift_is_detected():
    reference = pd.DataFrame({
        "Monthly Charge": np.arange(100, dtype=float)
    })

    current = pd.DataFrame({
        "Monthly Charge": np.arange(100, dtype=float) + 100
    })

    results = detect_drift(reference, current)

    assert results["numerical"]["Monthly Charge"]["ks"]["status"] == "alert"
    assert results["numerical"]["Monthly Charge"]["psi"]["status"] == "alert"


def test_categorical_shift_is_detected():
    reference = pd.DataFrame({
        "Contract": ["Monthly"] * 80 + ["Yearly"] * 20
    })

    current = pd.DataFrame({
        "Contract": ["Monthly"] * 20 + ["Yearly"] * 80
    })

    results = detect_drift(reference, current)

    assert results["categorical"]["Contract"]["chi_square"]["status"] == "alert"


def test_constant_numeric_feature_is_stable():
    reference = pd.DataFrame({
        "Refunds": [0.0] * 100
    })

    current = reference.copy()

    results = detect_drift(reference, current)

    assert results["numerical"]["Refunds"]["ks"]["status"] == "stable"
    assert results["numerical"]["Refunds"]["psi"]["status"] == "stable"


def test_excluded_churn_value_is_not_analyzed():
    reference = pd.DataFrame({
        "Age": np.arange(100),
        "Churn Value": [0, 1] * 50
    })

    current = reference.copy()

    results = detect_drift(reference, current)

    assert "Churn Value" not in results["numerical"]
    assert "Churn Value" not in results["categorical"]