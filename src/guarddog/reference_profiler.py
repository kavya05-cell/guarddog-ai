"""Reference profiling for the GuardDog AI monitoring baseline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


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

    Dataset-specific feature lists, target names, and fairness attributes are
    supplied through configuration. The profiler itself contains no
    dataset-specific loading or transformation logic.
    """

    def __init__(
        self,
        numerical_features: list[str],
        categorical_features: list[str],
        fairness_attributes: list[str],
        target: str,
        dataset_name: str | None = None,
    ) -> None:
        self.numerical_features = list(numerical_features)
        self.categorical_features = list(categorical_features)
        self.fairness_attributes = list(fairness_attributes)
        self.target = target
        self.dataset_name = dataset_name

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
                        self._category_key(k): float(v) for k, v in proportions.items()
                    },
                )
            )

        fairness = self._profile_fairness(df)

        return {
            "schema_version": "1.0",
            "dataset": self.dataset_name,
            "row_count": int(len(df)),
            "target": self.target,
            "numerical": numeric,
            "categorical": categorical,
            "fairness": fairness,
        }

    def _profile_fairness(self, df: pd.DataFrame) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for attribute in self.fairness_attributes:
            series = df[attribute]
            if pd.api.types.is_numeric_dtype(series):
                numeric = pd.to_numeric(series, errors="coerce")
                result[attribute] = {
                    "type": "numeric",
                    "count": int(numeric.notna().sum()),
                    "missing": int(numeric.isna().sum()),
                    "mean": float(numeric.mean()) if numeric.notna().any() else None,
                    "min": float(numeric.min()) if numeric.notna().any() else None,
                    "max": float(numeric.max()) if numeric.notna().any() else None,
                }
            else:
                categorical = series.astype("string")
                counts = categorical.value_counts(normalize=True, dropna=False)
                result[attribute] = {
                    "type": "categorical",
                    "count": int(categorical.notna().sum()),
                    "missing": int(categorical.isna().sum()),
                    "proportions": {
                        self._category_key(k): float(v) for k, v in counts.items()
                    },
                }
        return result

    def _validate_columns(self, df: pd.DataFrame) -> None:
        required = set(
            self.numerical_features
            + self.categorical_features
            + self.fairness_attributes
            + [self.target]
        )
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
