
from pathlib import Path

from src.preprocessing.cleaner import (
    clean_telco_data,
    load_raw_data,
)


RAW_DATA = Path(
    "data/processed/telco_merged_raw.csv"
)

OUTPUT_DATA = Path(
    "data/processed/telco_clean.csv"
)


def main() -> None:
    print("=" * 60)
    print("GuardDog AI - Telco Preprocessing")
    print("=" * 60)

    print("\n[1/4] Loading raw merged dataset...")

    df = load_raw_data(RAW_DATA)

    print(f"Input shape: {df.shape}")
    print(f"Input rows: {len(df):,}")
    print(f"Input columns: {len(df.columns):,}")

    print("\n[2/4] Applying preprocessing...")

    cleaned_df = clean_telco_data(df)

    print(f"Cleaned shape: {cleaned_df.shape}")

    print("\n[3/4] Validating output...")

    if len(cleaned_df) != len(df):
        raise ValueError(
            "Row count changed during preprocessing. "
            f"Input: {len(df)}, "
            f"Output: {len(cleaned_df)}"
        )

    if cleaned_df["Internet Type"].isna().any():
        raise ValueError(
            "Internet Type still contains missing values."
        )

    leakage_columns = [
        "Customer ID",
        "Customer Status",
        "Churn Label",
        "Churn Score",
        "Churn Category",
        "Churn Reason",
    ]

    remaining_leakage = [
        column
        for column in leakage_columns
        if column in cleaned_df.columns
    ]

    if remaining_leakage:
        raise ValueError(
            "Leakage columns remain in the cleaned dataset: "
            f"{remaining_leakage}"
        )

    required_columns = [
        "Age",
        "Gender",
        "Churn Value",
    ]

    missing_required = [
        column
        for column in required_columns
        if column not in cleaned_df.columns
    ]

    if missing_required:
        raise ValueError(
            "Required monitoring/fairness columns are missing: "
            f"{missing_required}"
        )

    print("\n[4/4] Saving cleaned dataset...")

    OUTPUT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_df.to_csv(
        OUTPUT_DATA,
        index=False,
    )

    print(
        f"\nSaved successfully to:\n"
        f"{OUTPUT_DATA}"
    )

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"\nFinal dataset: "
        f"{len(cleaned_df):,} rows × "
        f"{len(cleaned_df.columns):,} columns"
    )

    print(
        f"Offer missing values preserved: "
        f"{cleaned_df['Offer'].isna().sum():,}"
    )

    print(
        f"Internet Type missing values: "
        f"{cleaned_df['Internet Type'].isna().sum():,}"
    )


if __name__ == "__main__":
    main()

