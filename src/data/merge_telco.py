

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw/telco")
OUTPUT_PATH = Path("data/processed/telco_merged_raw.csv")


FILES = {
    "demographics": RAW_DIR / "demographics.csv",
    "location": RAW_DIR / "location.csv",
    "services": RAW_DIR / "services.csv",
    "status": RAW_DIR / "status.csv",
    "population": RAW_DIR / "population.csv",
}


def load_tables() -> dict[str, pd.DataFrame]:
    tables = {}

    for name, path in FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

        tables[name] = pd.read_csv(path)

    return tables


def validate_customer_table(
    df: pd.DataFrame,
    name: str,
) -> None:
    if "Customer ID" not in df.columns:
        raise ValueError(
            f"{name} does not contain Customer ID."
        )

    duplicate_count = df["Customer ID"].duplicated().sum()

    if duplicate_count:
        raise ValueError(
            f"{name} contains "
            f"{duplicate_count:,} duplicate Customer ID values."
        )


def validate_customer_ids(
    tables: dict[str, pd.DataFrame],
) -> None:
    customer_tables = [
        "demographics",
        "location",
        "services",
        "status",
    ]

    for name in customer_tables:
        validate_customer_table(
            tables[name],
            name,
        )

    reference_ids = set(
        tables["demographics"]["Customer ID"]
    )

    for name in customer_tables[1:]:
        current_ids = set(
            tables[name]["Customer ID"]
        )

        if current_ids != reference_ids:
            raise ValueError(
                f"Customer ID mismatch between "
                f"demographics and {name}."
            )


def merge_customer_tables(
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    merged = tables["demographics"].copy()

    for name in [
        "location",
        "services",
        "status",
    ]:
        merged = merged.merge(
            tables[name],
            on="Customer ID",
            how="inner",
            validate="one_to_one",
            suffixes=("", f"_{name}"),
        )

    return merged


def merge_population(
    customer_df: pd.DataFrame,
    population_df: pd.DataFrame,
) -> pd.DataFrame:
    if "Zip Code" not in customer_df.columns:
        raise ValueError(
            "Customer dataset does not contain Zip Code."
        )

    if "Zip Code" not in population_df.columns:
        raise ValueError(
            "Population dataset does not contain Zip Code."
        )

    population = population_df.copy()

    duplicate_zip_codes = population[
        "Zip Code"
    ].duplicated().sum()

    if duplicate_zip_codes:
        raise ValueError(
            "Population contains duplicate Zip Code values: "
            f"{duplicate_zip_codes:,}"
        )

    return customer_df.merge(
        population,
        on="Zip Code",
        how="left",
        validate="many_to_one",
        suffixes=("", "_population"),
    )


def validate_merged_data(
    df: pd.DataFrame,
) -> None:
    if len(df) != 7043:
        raise ValueError(
            "Unexpected row count. "
            f"Expected 7,043, found {len(df):,}."
        )

    if df["Customer ID"].nunique() != 7043:
        raise ValueError(
            "Customer ID uniqueness validation failed."
        )

    if df["Customer ID"].isna().any():
        raise ValueError(
            "Customer ID contains missing values."
        )


def save_dataset(
    df: pd.DataFrame,
) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


def main() -> None:
    print("=" * 60)
    print("GuardDog AI - Telco Dataset Reconstruction")
    print("=" * 60)

    print("\n[1/5] Loading source tables...")

    tables = load_tables()

    for name, df in tables.items():
        print(
            f"{name}: "
            f"{len(df):,} rows × "
            f"{len(df.columns):,} columns"
        )

    print("\n[2/5] Validating customer-level tables...")

    validate_customer_ids(tables)

    print("Customer ID validation passed.")

    print("\n[3/5] Merging customer-level tables...")

    merged = merge_customer_tables(tables)

    print(
        f"Customer-level dataset: "
        f"{len(merged):,} rows × "
        f"{len(merged.columns):,} columns"
    )

    print("\n[4/5] Adding population data...")

    merged = merge_population(
        merged,
        tables["population"],
    )

    print(
        f"Final merged dataset: "
        f"{len(merged):,} rows × "
        f"{len(merged.columns):,} columns"
    )

    print("\n[5/5] Validating and saving...")

    validate_merged_data(merged)

    save_dataset(merged)

    print(
        f"\nSaved successfully to:\n"
        f"{OUTPUT_PATH}"
    )

    print("\n" + "=" * 60)
    print("DATASET RECONSTRUCTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()

