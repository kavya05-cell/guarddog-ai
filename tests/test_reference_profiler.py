import pandas as pd

from guarddog.adult import add_guarddog_region
from guarddog.reference_profiler import ReferenceProfiler


def sample_adult_frame():
    return pd.DataFrame(
        {
            "age": [25, 40, 55, 30],
            "fnlwgt": [100, 200, 300, 150],
            "education_num": [10, 12, 9, 13],
            "capital_gain": [0, 0, 5000, 0],
            "capital_loss": [0, 100, 0, 0],
            "hours_per_week": [40, 45, 50, 35],
            "workclass": ["Private", "Private", "Gov", "Private"],
            "education": ["Bachelors", "Masters", "HS-grad", "Bachelors"],
            "marital_status": ["Never", "Married", "Married", "Never"],
            "occupation": ["Tech", "Manager", "Admin", "Tech"],
            "relationship": ["Not-in-family", "Husband", "Husband", "Not-in-family"],
            "race": ["White"] * 4,
            "sex": ["Female", "Male", "Male", "Female"],
            "native_country": ["India", "United-States", "Germany", "United-States"],
            "income": ["<=50K", ">50K", ">50K", "<=50K"],
        }
    )


def test_region_mapping_is_explicit():
    result = add_guarddog_region(sample_adult_frame())
    assert list(result["region"]) == ["Asia", "North America", "Europe", "North America"]


def test_reference_profiler_creates_baseline():
    df = add_guarddog_region(sample_adult_frame())
    baseline = ReferenceProfiler().fit(df)

    assert baseline["row_count"] == 4
    assert baseline["numerical"]["age"]["count"] == 4
    assert baseline["categorical"]["sex"]["proportions"]["Female"] == 0.5
    assert baseline["fairness"]["region"]["proportions"]["North America"] == 0.5


def test_reference_profiler_rejects_missing_columns():
    df = sample_adult_frame().drop(columns=["region"], errors="ignore")
    profiler = ReferenceProfiler()
    try:
        profiler.fit(df)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("Expected missing-column validation error")
