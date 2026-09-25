import json
from pathlib import Path

import pandas as pd


TARGET_COLUMN = "Churn Value"

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


def load_clean_data(input_path):
    return pd.read_csv(input_path)


def identify_features(df):
    feature_columns = [
        column for column in df.columns
        if column not in EXCLUDED_COLUMNS
    ]

    numerical_features = [
        column
        for column in feature_columns
        if pd.api.types.is_numeric_dtype(df[column])
        and column != TARGET_COLUMN
    ]

    categorical_features = [
        column
        for column in feature_columns
        if not pd.api.types.is_numeric_dtype(df[column])
        and column != TARGET_COLUMN
    ]

    return numerical_features, categorical_features


def profile_numerical_feature(series):
    return {
        "dtype": str(series.dtype),
        "count": int(series.count()),
        "missing_count": int(series.isna().sum()),
        "missing_rate": float(series.isna().mean()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "quantiles": {
            "0.25": float(series.quantile(0.25)),
            "0.50": float(series.quantile(0.50)),
            "0.75": float(series.quantile(0.75))
        }
    }


def profile_categorical_feature(series):
    value_counts = series.fillna("__MISSING__").value_counts()
    proportions = series.fillna("__MISSING__").value_counts(normalize=True)

    categories = {}

    for category in value_counts.index:
        categories[str(category)] = {
            "count": int(value_counts[category]),
            "proportion": float(proportions[category])
        }

    return {
        "dtype": str(series.dtype),
        "count": int(series.count()),
        "missing_count": int(series.isna().sum()),
        "missing_rate": float(series.isna().mean()),
        "unique_count": int(series.nunique(dropna=True)),
        "categories": categories
    }


def profile_target(series):
    value_counts = series.value_counts()
    proportions = series.value_counts(normalize=True)

    distribution = {}

    for value in value_counts.index:
        distribution[str(value)] = {
            "count": int(value_counts[value]),
            "proportion": float(proportions[value])
        }

    return {
        "dtype": str(series.dtype),
        "count": int(series.count()),
        "missing_count": int(series.isna().sum()),
        "missing_rate": float(series.isna().mean()),
        "distribution": distribution
    }


def create_reference_profile(df):
    numerical_features, categorical_features = identify_features(df)

    numerical_profile = {
        column: profile_numerical_feature(df[column])
        for column in numerical_features
    }

    categorical_profile = {
        column: profile_categorical_feature(df[column])
        for column in categorical_features
    }

    return {
        "metadata": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "target_column": TARGET_COLUMN,
            "numerical_feature_count": len(numerical_features),
            "categorical_feature_count": len(categorical_features)
        },
        "numerical_features": numerical_profile,
        "categorical_features": categorical_profile,
        "target": profile_target(df[TARGET_COLUMN])
    }


def save_profile(profile, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)


def main():
    input_path = "data/processed/telco_clean.csv"
    output_path = "data/processed/reference_profile.json"

    df = load_clean_data(input_path)
    profile = create_reference_profile(df)
    save_profile(profile, output_path)

    print(f"Dataset shape: {df.shape}")
    print(
        f"Numerical features: "
        f"{profile['metadata']['numerical_feature_count']}"
    )
    print(
        f"Categorical features: "
        f"{profile['metadata']['categorical_feature_count']}"
    )
    print(f"Reference profile saved to: {output_path}")


if __name__ == "__main__":
    main()