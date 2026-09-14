# GuardDog AI

## Simple ML Data Drift Monitoring Pipeline

Machine-learning models are trained on historical data, but the data they receive after deployment can change. Customer behavior, service usage, demographics, and other feature distributions may shift over time.

The model can continue returning predictions without any software failure while its input data becomes different from the data used as its reference. This is **data drift**.

> **GuardDog AI compares new data with a trusted reference baseline and identifies distribution changes that require investigation.**

The internship version is intentionally kept simple: a small, modular, end-to-end monitoring pipeline rather than a large MLOps platform.

---

## 1. The Problem

Traditional ML evaluation usually happens before deployment on a fixed test set. Accuracy, precision, recall, and F1 describe historical model performance, but they do not continuously answer:

> **Has the data arriving now changed compared with the reference data?**

For example:

```text
Reference data
Age 25–35: 40%
Age 36–50: 45%
Age 51+:   15%

Production-like data
Age 25–35: 20%
Age 36–50: 40%
Age 51+:   40%
```

The incoming population has changed. GuardDog provides a statistical way to detect that change.

---

## 2. What Is Data Drift?

**Data drift** is a change in the statistical distribution of data over time.

It can affect numerical features such as `Age`, `Tenure in Months`, and `Monthly Charge`, or categorical features such as `Gender`, `Contract`, and `Internet Service`.

GuardDog does not treat every change as a model failure. It identifies statistically meaningful changes so that they can be investigated.

---

## 3. Reference Baseline

Before drift can be detected, GuardDog needs to define what normal data looks like.

```text
Reference Dataset
       ↓
Reference Profiler
       ↓
Statistical Baseline
```

The baseline stores information such as numerical statistics, categorical proportions, and missingness information.

Future production-like data is compared against this baseline.

---

## 4. GuardDog AI Solution

The core system follows this flow:

```text
                RAW DATA
                    ↓
            +----------------+
            |  Preprocessing |
            +--------+-------+
                     ↓
              Clean Dataset
                     ↓
            +----------------+
            | Reference      |
            | Profiler       |
            +--------+-------+
                     ↓
             Reference Profile
                     ↓
        +------------+------------+
        ↓                         ↓
 Reference Data            Production-like Data
        |                         |
        +------------+------------+
                     ↓
            +----------------+
            | Drift Detector |
            |                |
            | KS             |
            | PSI            |
            | Chi-Square     |
            +--------+-------+
                     ↓
               Drift Results
                     ↓
            +----------------+
            | Streamlit      |
            | Dashboard      |
            +----------------+
```

The system answers four simple questions:

1. What did the reference data look like?
2. What does the new data look like?
3. Are the distributions different?
4. Which features require attention?

---

## 5. Project Scope

The internship MVP contains only the components required to demonstrate the central drift-monitoring objective.

### Core scope

```text
1. Dataset reconstruction and validation
2. Data preprocessing
3. Reference profiling
4. Drift detection
5. Controlled drift simulation
6. Simple Streamlit dashboard
7. Automated tests and documentation
```

### Drift methods

| Method | Data | Purpose |
|---|---|---|
| **Kolmogorov-Smirnov (KS)** | Numerical | Detect statistical distribution differences |
| **Population Stability Index (PSI)** | Numerical / binned distributions | Measure distribution-shift magnitude |
| **Chi-Square** | Categorical | Detect differences in categorical distributions |

### Deliberately excluded from the MVP

To keep the project maintainable and achievable within the internship timeline, the MVP does not require:

- Online learning
- Adaptive classifier ensembles
- Automatic model retraining
- Complex MLOps infrastructure
- Cloud deployment
- Large multi-dataset benchmarking
- Advanced multivariate drift detection
- Complex fairness frameworks
- Large reporting infrastructure

These are future-scope possibilities, not implementation requirements.

---

## 6. Drift Detection

### 6.1 Kolmogorov-Smirnov Test

The KS test compares two numerical distributions and produces a test statistic and p-value.

Initial thresholds:

| p-value | Classification |
|---:|---|
| `p >= 0.05` | No warning |
| `p < 0.05` | Warning |
| `p < 0.01` | Strict Alert |

The p-value describes statistical evidence of a difference; it does not by itself describe practical importance.

### 6.2 Population Stability Index

PSI compares the proportions of observations in defined bins or categories between reference and current data.

Initial thresholds:

| PSI | Classification |
|---:|---|
| `< 0.10` | Stable |
| `0.10–0.25` | Warning |
| `> 0.25` | Action Required |

A small epsilon is used to protect calculations when a bin has zero frequency:

```text
ε = 1 × 10⁻⁸
```

### 6.3 Chi-Square Test

The Chi-Square test is used for categorical features. It determines whether the observed categorical distribution differs significantly from the reference distribution.

### Why three methods?

```text
KS          → statistical evidence for numerical drift
PSI         → practical magnitude of distribution movement
Chi-Square  → statistical evidence for categorical drift
```

Together, they provide a simple but useful initial drift-monitoring layer.

---

## 7. Primary Dataset

GuardDog uses the **IBM Telco Customer Churn** dataset as its primary end-to-end dataset.

The enhanced dataset is organized into five source tables:

- Demographics
- Location
- Population
- Services
- Status

The source tables are reconstructed before preprocessing.

```text
Demographics ─┐
Location ─────┤
Services ─────┼── Customer ID ──→ Customer Dataset
Status ───────┘

Population ── Zip Code ──→ Customer Dataset
```

Customer-level tables are validated using one-to-one `Customer ID` relationships. Population data is joined using a many-to-one `Zip Code` relationship.

The reconstructed dataset contains **7,043 customers** and is saved as:

```text
data/processed/telco_merged_raw.csv
```

---

## 8. Data Preprocessing

The preprocessing stage converts the reconstructed data into a validated monitoring dataset.

The pipeline:

1. Loads the merged dataset.
2. Normalizes common missing-value representations.
3. Validates the churn target.
4. Validates required monitoring fields.
5. Removes identifiers and post-outcome leakage fields.
6. Removes redundant constant fields.
7. Resolves structurally missing `Internet Type` values for customers without internet service.
8. Preserves `Offer` missingness because its meaning has not been established.
9. Saves the cleaned dataset.

Current output:

```text
data/processed/telco_clean.csv

7,043 rows × 54 columns
```

---

## 9. Full Architecture

GuardDog follows a simple sequential architecture:

```text
┌──────────────────────────────────────────────────────────────┐
│                         SOURCE DATA                           │
│  Demographics | Location | Population | Services | Status   │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                 DATASET RECONSTRUCTION                       │
│  Validate Customer IDs → Merge customer tables → Add Census  │
│  population using Zip Code                                   │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                       PREPROCESSING                           │
│  Validation → Leakage removal → Missing-value handling       │
│  → Clean monitoring dataset                                  │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │  CLEAN REFERENCE  │
                    │      DATASET      │
                    └─────────┬─────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                     REFERENCE PROFILER                        │
│  Numerical statistics | Category proportions | Missingness  │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │ REFERENCE PROFILE │
                    │       JSON        │
                    └─────────┬─────────┘
                              │
                ┌─────────────┴─────────────┐
                ↓                           ↓
        REFERENCE DATA              PRODUCTION-LIKE DATA
                │                           │
                └─────────────┬─────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                       DRIFT DETECTOR                         │
│               KS | PSI | Chi-Square                          │
│               ↓                                               │
│          Drift score + p-value + status                      │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │  DRIFT RESULTS    │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ STREAMLIT         │
                    │ DASHBOARD         │
                    └───────────────────┘
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| **Dataset Reconstruction** | Safely combines the Telco source tables |
| **Preprocessing** | Produces a clean and validated dataset |
| **Reference Profiler** | Defines the baseline distribution |
| **Drift Detector** | Compares reference and production-like data |
| **Dashboard** | Presents results in an understandable form |
| **Tests** | Verify that each component behaves correctly |

---

## 10. Repository Structure

```text
guarddog-ai/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── telco/
│   │       ├── demographics.csv
│   │       ├── location.csv
│   │       ├── population.csv
│   │       ├── services.csv
│   │       └── status.csv
│   │
│   └── processed/
│       ├── telco_merged_raw.csv
│       └── telco_clean.csv
│
├── src/
│   ├── data/
│   │   └── merge_telco.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   └── pipeline.py
│   │
│   ├── profiler/
│   │   ├── __init__.py
│   │   └── profiler.py
│   │
│   └── drift/
│       ├── __init__.py
│       └── detector.py
│
├── dashboard/
│   └── app.py
│
├── tests/
│   ├── test_preprocessing.py
│   ├── test_profiler.py
│   └── test_drift.py
│
├── notebooks/
│   └── experiments/
│
├── reports/
│   └── results/
│
└── docs/
    ├── project-specification.md
    ├── architecture.md
    └── roadmap.md
```

### Folder responsibilities

| Path | Purpose |
|---|---|
| `data/raw/` | Original source datasets |
| `data/processed/` | Reconstructed and cleaned datasets |
| `src/data/` | Dataset reconstruction |
| `src/preprocessing/` | Data cleaning and validation |
| `src/profiler/` | Reference baseline creation |
| `src/drift/` | Drift detection logic |
| `dashboard/` | Streamlit presentation layer |
| `tests/` | Automated tests |
| `notebooks/` | Exploration and controlled experiments |
| `reports/` | Experiment results |
| `docs/` | Project documentation |

Core logic remains in `src/`; notebooks are for experimentation only.

---

## 11. End-to-End Workflow

```text
1. Load Telco source tables
             ↓
2. Validate IDs and relationships
             ↓
3. Reconstruct customer-level dataset
             ↓
4. Preprocess and validate data
             ↓
5. Generate reference profile
             ↓
6. Create production-like batch
             ↓
7. Run KS / PSI / Chi-Square
             ↓
8. Classify drift results
             ↓
9. Display results in Streamlit
```

This keeps the project separated into four understandable stages:

```text
Data Preparation
      ↓
Baseline Creation
      ↓
Statistical Comparison
      ↓
Visualization
```

---

## 12. Controlled Drift Simulation

A drift detector needs a controlled experiment where the expected change is known.

GuardDog will create production-like batches by modifying selected feature distributions.

Example:

```text
Reference batch
Age follows the reference distribution

Production-like batch
Age distribution shifted toward older customers

Expected result
Age is flagged by the drift detector
```

Controlled experiments allow the implementation to be validated without requiring a real production environment.

---

## 13. Dashboard

The dashboard is intentionally simple. Its purpose is to make statistical results understandable rather than to become a large analytics platform.

Example:

```text
GUARDDOG AI

Overall Status
DRIFT DETECTED

Feature             Method        Status
------------------------------------------
Age                 KS            Alert
Age                 PSI           Warning
Monthly Charge      KS            Stable
Contract            Chi-Square    Warning
Gender              Chi-Square    Stable
```

The user should be able to identify which features changed and why they were flagged without reading raw Python output.

---

## 14. Interpretation and Limitations

A drift alert does **not** automatically prove that the model is inaccurate.

It means that the monitored data has changed according to the configured statistical method and threshold.

Likewise, statistical significance does not automatically mean business significance. A detected change may be expected because of a legitimate business or population change.

GuardDog is therefore a **monitoring and decision-support system**, not an automatic model-retraining system.

The statistical methods also have limitations. KS is primarily a univariate numerical test, PSI depends on its binning scheme, and Chi-Square requires appropriate categorical data and sufficient observations.

---

## 15. Current Project Status

### Completed

- GitHub repository created
- Project scope documented
- Primary dataset selected
- Telco source tables obtained
- Source schemas inspected
- Customer IDs validated
- Population relationship validated
- Dataset reconstructed successfully
- `telco_merged_raw.csv` generated
- Preprocessing pipeline implemented
- Leakage and redundant fields removed
- `telco_clean.csv` generated successfully

### Current

- Reference Profiler

### Next

- Minimal Reference Profiler
- Drift Detector
- Controlled drift simulation
- Simple Streamlit dashboard
- Automated tests
- Final integration and documentation

---

## 16. Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core implementation |
| **pandas** | Data loading and transformation |
| **NumPy** | Numerical operations |
| **SciPy** | Statistical tests |
| **scikit-learn** | Supporting ML utilities |
| **Streamlit** | Dashboard |
| **pytest** | Automated testing |

The stack is intentionally small. New infrastructure should only be added when it directly supports the core objective.

---

## 17. Future Scope

Possible future extensions include:

- Additional fairness metrics
- Multivariate drift detection
- Concept-drift detection for streaming data
- Online or continual learning
- Model-performance monitoring when labels become available
- Automated retraining workflows
- Additional benchmark datasets
- Advanced MLOps integrations
- PDF model-health reporting
- Cloud deployment

These extensions are documented as future work so that the internship MVP remains focused and maintainable.

---

## 18. Project Philosophy

> **The goal is a complete working monitoring system, not the maximum number of features.**

GuardDog prioritizes:

- clear architecture;
- small independent modules;
- reproducible experiments;
- statistically grounded drift detection;
- understandable results; and
- maintainable code.

The central idea is simple:

```text
Trusted Data
     ↓
Reference Baseline
     ↓
New Data
     ↓
Drift Detection
     ↓
Understandable Results
```

**GuardDog AI is a focused ML observability project designed to detect data drift clearly, simply, and reproducibly.**
