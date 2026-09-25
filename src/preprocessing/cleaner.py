from pathlib import Path

import pandas as pd

TARGET_COLUMN = "Churn Value"

LEAKAGE_COLUMNS = [
    "Customer ID",
    "Customer Status",
    "Churn Label",
    "Churn Score",
    "Churn Category",
    "Churn Reason",
]
REDUNDANT_COLUMNS = [
    "Quarter_services",
    "Quarter_status",
]


def load_raw_data(path: str | Path) -> pd.DataFrame:
   
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


def normalize_missing_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    missing_tokens = [
        "",
        " ",
        "NA",
        "N/A",
        "null",
        "NULL",
        "None",
    ]

    result = result.replace(
        missing_tokens,
        pd.NA,
    )

    return result


def validate_target(
    df: pd.DataFrame,
) -> None:
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Required target column "
            f"'{TARGET_COLUMN}' is missing."
        )

    valid_values = set(
        df[TARGET_COLUMN]
        .dropna()
        .unique()
    )

    if not valid_values.issubset({0, 1}):
        raise ValueError(
            f"'{TARGET_COLUMN}' must contain "
            f"only 0 and 1. Found: {valid_values}"
        )


def validate_required_monitoring_columns(
    df: pd.DataFrame,
) -> None:
    required_columns = [
        "Age",
        "Gender",
        TARGET_COLUMN,
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Required monitoring/fairness columns "
            f"are missing: {missing}"
        )


def remove_leakage_and_redundant_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    columns_to_remove = [
        column
        for column in (
            LEAKAGE_COLUMNS
            + REDUNDANT_COLUMNS
        )
        if column in result.columns
    ]

    return result.drop(
        columns=columns_to_remove
    )


def handle_internet_type(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    if (
        "Internet Type" in result.columns
        and "Internet Service" in result.columns
    ):
        mask = (
            result["Internet Service"].eq("No")
            & result["Internet Type"].isna()
        )

        result.loc[
            mask,
            "Internet Type",
        ] = "No Internet"

    return result


def clean_telco_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()
    result = normalize_missing_values(result)
    validate_target(result)

  
    validate_required_monitoring_columns(result)

    result = remove_leakage_and_redundant_columns(
        result
    )

    result = handle_internet_type(result)

    return result