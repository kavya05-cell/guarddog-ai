import pandas as pd


def calculate_group_metrics(
    df,
    group_column,
    outcome_column="Churn Value"
):
    overall_rate = df[outcome_column].mean()

    grouped = (
        df.groupby(group_column, dropna=False)[outcome_column]
        .agg(["count", "mean"])
        .reset_index()
    )

    grouped = grouped.rename(
        columns={
            group_column: "Group",
            "count": "Records",
            "mean": "Churn Rate"
        }
    )

    grouped["Churn Rate"] = grouped["Churn Rate"] * 100
    grouped["Overall Churn Rate"] = overall_rate * 100
    grouped["Difference from Overall (pp)"] = (
        grouped["Churn Rate"] - grouped["Overall Churn Rate"]
    )

    return grouped


def calculate_rate_ratio(
    df,
    group_column,
    outcome_column="Churn Value",
    reference_group=None
):
    rates = df.groupby(group_column)[outcome_column].mean()

    if reference_group is None:
        reference_group = rates.index[0]

    if reference_group not in rates.index:
        raise ValueError(
            f"Reference group '{reference_group}' not found."
        )

    reference_rate = rates[reference_group]

    results = []

    for group, rate in rates.items():
        ratio = (
            rate / reference_rate
            if reference_rate != 0
            else None
        )

        results.append({
            "Group": group,
            "Churn Rate (%)": rate * 100,
            "Reference Group": reference_group,
            "Rate Ratio": ratio
        })

    return pd.DataFrame(results)


def run_fairness_audit(df):
    audit_columns = {
        "Gender": "Gender",
        "Age Group": "Under 30",
        "Senior Citizen": "Senior Citizen"
    }

    results = {}

    for audit_name, column in audit_columns.items():
        results[audit_name] = {
            "group_metrics": calculate_group_metrics(df, column),
            "rate_ratios": calculate_rate_ratio(df, column)
        }

    return results
