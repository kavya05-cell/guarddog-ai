"""Reference profiling for the GuardDog AI monitoring baseline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_NUMERICAL_FEATURES = [
    "age",
    "fnlwgt",
    "education_num",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
]

DEFAULT_CATEGORICAL_FEATURES = [
    "workclass",
    "education",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native_country",
    "region",
]

DEFAULT_FAIRNESS_ATTRIBUTES = ["age", "sex", "region"]


@dataclass(frozen=True)
class NumericProfile:
    count: int
    missing: int
    mean: float
    variance: float
    std: float
    min: float
    max: float


@dataclass(frozen=True)
class CategoricalProfile:
    count: int
    missing: int
    unique: int
    proportions: dict[str, float]


class ReferenceProfiler:
    """Create a statistical baseline from a reference/training dataframe.

    The profiler deliberately stores descriptive statistics rather than model
    parameters. Drift detectors can consume this baseline without depending
    on a specific predictive model implementation.
    """

    def __init__(
        self,
        numerical_features: list[str] | None = None,
        categorical_features: list[str] | None = None,
        fairness_attributes: list[str] | None = None,
        target: str = "income",
    ) -> None:
        self.numerical_features = numerical_features or DEFAULT_NUMERICAL_FEATURES.copy()
        self.categorical_features = categorical_features or DEFAULT_CATEGORICAL_FEATURES.copy()
        self.fairness_attributes = fairness_attributes or DEFAULT_FAIRNESS_ATTRIBUTES.copy()
        self.target = target

    def fit(self, df: pd.DataFrame) -> dict[str, Any]:
        """Profile ``df`` and return a JSON-serializable baseline."""
        self._validate_columns(df)

        numeric: dict[str, dict[str, Any]] = {}
        for feature in self.numerical_features:
            series = pd.to_numeric(df[feature], errors="coerce")
            valid = series.dropna()
            numeric[feature] = asdict(
                NumericProfile(
                    count=int(valid.size),
                    missing=int(series.isna().sum()),
                    mean=float(valid.mean()) if not valid.empty else float("nan"),
                    variance=float(valid.var(ddof=1)) if valid.size > 1 else 0.0,
                    std=float(valid.std(ddof=1)) if valid.size > 1 else 0.0,
                    min=float(valid.min()) if not valid.empty else float("nan"),
                    max=float(valid.max()) if not valid.empty else float("nan"),
                )
            )

        categorical: dict[str, dict[str, Any]] = {}
        for feature in self.categorical_features:
            series = df[feature].astype("string")
            proportions = series.value_counts(normalize=True, dropna=False)
            categorical[feature] = asdict(
                CategoricalProfile(
                    count=int(series.notna().sum()),
                    missing=int(series.isna().sum()),
                    unique=int(series.nunique(dropna=True)),
                    proportions={
                        self._category_key(k): float(v)
                        for k, v in proportions.items()
                    },
                )
            )

        fairness = self._profile_fairness(df)

        return {
            "schema_version": "1.0",
            "row_count": int(len(df)),
            "target": self.target,
            "numerical": numeric,
            "categorical": categorical,
            "fairness": fairness,
        }

    def _profile_fairness(self, df: pd.DataFrame) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for attribute in self.fairness_attributes:
            if attribute == "age":
                # Age is continuous in the source dataset. Store summary stats
                # and leave demographic bucketing to the fairness configuration.
                series = pd.to_numeric(df[attribute], errors="coerce")
                result[attribute] = {
                    "type": "numeric",
                    "count": int(series.notna().sum()),
                    "missing": int(series.isna().sum()),
                    "mean": float(series.mean()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                }
            else:
                series = df[attribute].astype("string")
                counts = series.value_counts(normalize=True, dropna=False)
                result[attribute] = {
                    "type": "categorical",
                    "count": int(series.notna().sum()),
                    "missing": int(series.isna().sum()),
                    "proportions": {
                        self._category_key(k): float(v) for k, v in counts.items()
                    },
                }
        return result

    def _validate_columns(self, df: pd.DataFrame) -> None:
        required = set(self.numerical_features + self.categorical_features + self.fairness_attributes + [self.target])
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"Reference data is missing required columns: {missing}")

    @staticmethod
    def _category_key(value: Any) -> str:
        if pd.isna(value):
            return "<MISSING>"
        if isinstance(value, np.generic):
            value = value.item()
        return str(value)
