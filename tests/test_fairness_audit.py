import pandas as pd

from src.fairness.audit import run_fairness_audit


def test_fairness_audit_returns_expected_groups():
    df = pd.DataFrame({
        "Gender": ["Male", "Male", "Female", "Female"],
        "Under 30": ["Yes", "No", "Yes", "No"],
        "Senior Citizen": ["No", "Yes", "No", "Yes"],
        "Churn Value": [0, 1, 1, 0]
    })

    results = run_fairness_audit(df)

    assert "Gender" in results
    assert "Age Group" in results
    assert "Senior Citizen" in results

    assert not results["Gender"]["group_metrics"].empty
    assert not results["Age Group"]["rate_ratios"].empty
