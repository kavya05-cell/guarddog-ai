"""UCI Adult ingestion helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ADULT_COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country",
    "income",
]

# Broad regions are an engineered GuardDog attribute derived from the Adult
# dataset's native-country field. Unknown/other values remain explicit.
COUNTRY_TO_REGION = {
    "United-States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Puerto-Rico": "Caribbean",
    "Cuba": "Caribbean",
    "Jamaica": "Caribbean",
    "Haiti": "Caribbean",
    "Dominican-Republic": "Caribbean",
    "Outlying-US(Guam-USVI-etc)": "Pacific",
    "Guatemala": "Central America",
    "El-Salvador": "Central America",
    "Honduras": "Central America",
    "Nicaragua": "Central America",
    "Costa-Rica": "Central America",
    "Trinadad&Tobago": "Caribbean",
    "Columbia": "South America",
    "Ecuador": "South America",
    "Peru": "South America",
    "Venezuela": "South America",
    "Brazil": "South America",
    "Argentina": "South America",
    "Germany": "Europe",
    "England": "Europe",
    "France": "Europe",
    "Italy": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Ireland": "Europe",
    "Scotland": "Europe",
    "Greece": "Europe",
    "Hungary": "Europe",
    "Holand-Netherlands": "Europe",
    "Yugoslavia": "Europe",
    "India": "Asia",
    "China": "Asia",
    "Japan": "Asia",
    "Taiwan": "Asia",
    "South": "Asia",
    "Philippines": "Asia",
    "Vietnam": "Asia",
    "Thailand": "Asia",
    "Iran": "Asia",
    "Cambodia": "Asia",
    "Laos": "Asia",
    "Hong": "Asia",
    "Pakistan": "Asia",
    "Afghanistan": "Asia",
}


def add_guarddog_region(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the engineered ``region`` column added."""
    if "native_country" not in df.columns:
        raise ValueError("Adult data must contain 'native_country' before region mapping.")

    result = df.copy()
    cleaned = result["native_country"].astype("string").str.strip().str.replace("?", pd.NA)
    result["native_country"] = cleaned
    result["region"] = cleaned.map(COUNTRY_TO_REGION).fillna("Other/Unknown")
    return result


def load_adult_csv(path: str | Path) -> pd.DataFrame:
    """Load an Adult-style CSV and normalize common whitespace markers."""
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
    missing = sorted(set(ADULT_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Adult CSV is missing expected columns: {missing}")
    return add_guarddog_region(df)
