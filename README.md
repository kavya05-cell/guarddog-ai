# GuardDog AI

## Real-Time ML Data Drift Monitoring Pipeline

Machine-learning models are trained on historical data, but the data they receive after deployment can change. Customer behavior, service usage, demographics, and other feature distributions may shift over time.

The model can continue running without any software failure while its input data becomes different from the data used as its reference. This is **data drift**.

> **GuardDog AI compares trusted reference data with incoming streaming data and identifies distribution changes that require investigation.**

The internship version is intentionally focused: a small, modular, end-to-end drift monitoring system using **Apache Kafka** for real-time data ingestion, statistical drift detection, and a simple Streamlit dashboard.

---

## 1. The Problem

Traditional ML evaluation usually happens before deployment on a fixed test set. Accuracy, precision, recall, and F1 describe historical model performance, but they do not continuously answer:

> **Has the data arriving now changed compared with the reference data?**

For example, a model may have been trained when most customers had moderate monthly charges. Months later, customer behavior may change and incoming charges may become substantially higher.

The software can still run normally. The problem is that the **data distribution has changed**.

GuardDog addresses this problem by continuously consuming incoming data and comparing it with a trusted reference baseline.

---

## 2. What Is Data Drift?

**Data drift** is a change in the statistical distribution of input data over time.

It can affect numerical features such as `Age`, `Tenure in Months`, and `Monthly Charge`, or categorical features such as `Gender`, `Contract`, and `Internet Service`.

GuardDog does not treat every change as a model failure. It identifies statistically meaningful distribution changes so that they can be investigated.

---

## 3. Why Real-Time Monitoring?

A static comparison can tell us that two datasets are different, but deployed systems receive data continuously.

GuardDog therefore uses **Apache Kafka** as the streaming layer.

```text
Incoming Data
      ↓
Kafka Producer
      ↓
Kafka Topic
      ↓
Kafka Consumer
      ↓
Incoming Batch
      ↓
Drift Detector
```

The consumer collects incoming records into small batches and evaluates them against the reference baseline. This provides a practical real-time/streaming monitoring workflow without introducing a large distributed processing platform.

The project does not use Kafka for model training or automatic retraining. Kafka is used specifically to provide a continuous stream of incoming data to the monitoring pipeline.

---

## 4. Reference Baseline

Before drift can be detected, GuardDog needs to define what normal data looks like.

```text
Reference Dataset
       ↓
Reference Profiler
       ↓
Statistical Baseline
```

The reference profile stores information such as numerical statistics, categorical proportions, and missingness information.

Incoming Kafka data is compared against this trusted reference.

---

## 5. GuardDog AI Solution

The core system follows this flow:

```text
                    SOURCE DATA
                         ↓
                 Data Reconstruction
                         ↓
                   Preprocessing
                         ↓
                Clean Reference Data
                         ↓
                 Reference Profiler
                         ↓
                Reference Profile
                         │
                         │
                         ▼
                  ┌─────────────┐
                  │ Kafka Topic │
                  └──────┬──────┘
                         ↓
                  Kafka Consumer
                         ↓
                   Incoming Batch
                         ↓
                  Drift Detector
                  /      |       \
                KS      PSI     Chi-Square
                  \      |       /
                   \     |      /
                    Drift Results
                         ↓
                 Streamlit Dashboard
```

The system answers four simple questions:

1. What did the trusted reference data look like?
2. What data is arriving now?
3. Are the incoming distributions different?
4. Which features require attention?

---

## 6. Project Scope

The internship MVP contains only the components required to demonstrate real-time data drift monitoring.

### Core scope

```text
1. Dataset reconstruction and validation
2. Data preprocessing
3. Reference profiling
4. Kafka-based real-time data ingestion
5. Streaming batch construction
6. Statistical drift detection
7. Controlled drift simulation
8. Simple Streamlit dashboard
9. Automated tests and documentation
```

### Drift methods

| Method | Data | Purpose |
|---|---|---|
| **Kolmogorov-Smirnov (KS)** | Numerical | Detect statistical distribution differences |
| **Population Stability Index (PSI)** | Numerical / binned distributions | Measure distribution-shift magnitude |
| **Chi-Square** | Categorical | Detect differences in categorical distributions |

### Streaming technology

| Technology | Purpose |
|---|---|
| **Apache Kafka** | Real-time event/data streaming |
| **Kafka Producer** | Sends incoming customer records to a Kafka topic |
| **Kafka Consumer** | Receives records from the topic |
| **Batch Builder** | Groups incoming records before drift evaluation |

### Deliberately excluded from the MVP

To keep the project maintainable and achievable within the internship timeline, the MVP does not require:

- Online model learning
- Adaptive classifier ensembles
- Automatic model retraining
- Kafka Streams or complex distributed processing
- Spark or Flink
- Cloud deployment
- Kubernetes
- Large multi-dataset benchmarking
- Advanced multivariate drift detection
- Complex fairness frameworks
- Large reporting infrastructure

These are future-scope possibilities, not implementation requirements.

---

## 7. Drift Detection

### 7.1 Kolmogorov-Smirnov Test

The KS test compares two numerical distributions and produces a test statistic and p-value.

Initial thresholds:

| p-value | Classification |
|---:|---|
| `p >= 0.05` | Stable |
| `p < 0.05` | Warning |
| `p < 0.01` | Alert |

The p-value describes statistical evidence of a difference; it does not by itself describe practical importance.

### 7.2 Population Stability Index

PSI compares the proportions of observations in defined bins between reference and current data.

Initial thresholds:

| PSI | Classification |
|---:|---|
| `< 0.10` | Stable |
| `0.10–0.25` | Warning |
| `> 0.25` | Alert |

A small epsilon is used to protect calculations when a bin has zero frequency:

```text
ε = 1 × 10⁻⁸
```

### 7.3 Chi-Square Test

The Chi-Square test is used for categorical features. It determines whether the observed categorical distribution differs significantly from the reference distribution.

### Why three methods?

```text
KS          → statistical evidence for numerical drift
PSI         → practical magnitude of distribution movement
Chi-Square  → statistical evidence for categorical drift
```

Together, they provide a simple and complementary initial drift-monitoring layer.

---

## 8. Primary Dataset

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

## 9. Data Preprocessing

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

## 10. Real-Time Kafka Architecture

Kafka provides the connection between continuously arriving data and the GuardDog detection engine.

```text
┌─────────────────────┐
│   Data Source       │
│ Telco / Simulation  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Kafka Producer    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Kafka Topic       │
│    telco-data       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Kafka Consumer    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Batch Builder     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  GuardDog Drift     │
│      Detector       │
│                     │
│ KS | PSI | Chi²     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Drift Results     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Streamlit Dashboard │
└─────────────────────┘
```

### Streaming behavior

Incoming records are not evaluated one-by-one because individual observations are generally insufficient for reliable distribution comparison.

Instead, GuardDog collects a configurable number of records into a batch:

```text
Record → Record → Record → ... → Record
                         ↓
                    Batch of N
                         ↓
                  Drift Detection
                         ↓
                    New Batch
```

This allows the statistical methods to operate on meaningful samples while still providing continuous monitoring.

### Dynamic drift demonstration

The streaming experiment will demonstrate drift appearing over time:

```text
Batch 1 → Normal → Stable
Batch 2 → Normal → Stable
Batch 3 → Normal → Stable
Batch 4 → Shifted → Warning
Batch 5 → Shifted → Alert
```

The exact classification depends on the configured statistical thresholds and observed distributions.

---

## 11. Controlled Drift Simulation

A drift detector needs a controlled experiment where the expected change is known.

GuardDog creates production-like streaming data by modifying selected feature distributions before sending records through Kafka.

Example:

```text
Normal Records
      ↓
Kafka
      ↓
Stable batches
      ↓
Controlled distribution shift
      ↓
Kafka
      ↓
Drifted batches
      ↓
KS / PSI / Chi-Square
      ↓
Warning / Alert
```

The controlled experiment allows the implementation to be validated without requiring a real production environment.

The original reference dataset remains unchanged.

---

## 12. Full Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                         SOURCE DATA                           │
│  Demographics | Location | Population | Services | Status   │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                 DATASET RECONSTRUCTION                       │
│  Validate Customer IDs → Merge customer tables → Population  │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                       PREPROCESSING                           │
│  Validation → Leakage removal → Missing-value handling       │
└─────────────────────────────┬────────────────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │  CLEAN REFERENCE  │
                    │      DATASET      │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Reference Profiler│
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Reference Profile │
                    └─────────┬─────────┘
                              │
                              │
                              ↓
                    ┌───────────────────┐
                    │ Kafka Producer    │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Kafka Topic       │
                    │ telco-data       │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Kafka Consumer    │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Batch Builder     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Drift Detector    │
                    │ KS | PSI | χ²     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Drift Results     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Streamlit         │
                    │ Dashboard         │
                    └───────────────────┘
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| **Dataset Reconstruction** | Safely combines the Telco source tables |
| **Preprocessing** | Produces a clean and validated reference dataset |
| **Reference Profiler** | Defines the trusted baseline distribution |
| **Kafka Producer** | Publishes incoming records to the streaming topic |
| **Kafka Topic** | Buffers the incoming data stream |
| **Kafka Consumer** | Receives incoming records |
| **Batch Builder** | Groups records into statistically useful batches |
| **Drift Detector** | Compares incoming batches with the reference |
| **Dashboard** | Presents current drift status and feature-level results |
| **Tests** | Verify component and end-to-end behavior |

---

## 13. Repository Structure

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
│       ├── telco_clean.csv
│       ├── reference_profile.json
│       └── drift_report.json
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
│   ├── drift/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── report.py
│   │   └── simulator.py
│   │
│   └── streaming/
│       ├── __init__.py
│       ├── producer.py
│       ├── consumer.py
│       └── batch_builder.py
│
├── dashboard/
│   └── app.py
│
├── tests/
│   ├── test_preprocessing.py
│   ├── test_profiler.py
│   ├── test_drift.py
│   └── test_streaming.py
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
| `data/processed/` | Reconstructed, cleaned, and generated datasets |
| `src/data/` | Dataset reconstruction |
| `src/preprocessing/` | Data cleaning and validation |
| `src/profiler/` | Reference baseline creation |
| `src/drift/` | Statistical drift detection and controlled experiments |
| `src/streaming/` | Kafka producer, consumer, and batch handling |
| `dashboard/` | Streamlit presentation layer |
| `tests/` | Automated tests |
| `notebooks/` | Exploration and experiments |
| `reports/` | Experiment results |
| `docs/` | Project documentation |

Core logic remains in `src/`; notebooks are for experimentation only.

---

## 14. End-to-End Workflow

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
6. Start Kafka
             ↓
7. Publish incoming records
             ↓
8. Consume records from Kafka
             ↓
9. Build an incoming batch
             ↓
10. Run KS / PSI / Chi-Square
             ↓
11. Classify drift results
             ↓
12. Display results in Streamlit
             ↓
13. Continue processing the next batch
```

This keeps the project separated into five understandable stages:

```text
Data Preparation
      ↓
Baseline Creation
      ↓
Real-Time Ingestion
      ↓
Statistical Comparison
      ↓
Visualization
```

---

## 15. Dashboard

The dashboard is intentionally simple. Its purpose is to make streaming drift results understandable rather than to become a large analytics platform.

Example:

```text
GUARDDOG AI

Stream Status
ACTIVE

Current Status
DRIFT DETECTED

Batches Processed: 18

Feature             Method        Status
------------------------------------------
Monthly Charge      KS            Alert
Monthly Charge      PSI           Alert
Tenure in Months    KS            Alert
Tenure in Months    PSI           Alert
Contract            Chi-Square    Warning
Gender              Chi-Square    Stable
```

The dashboard should allow a user to identify the current stream status, number of processed batches, and features requiring attention.

---

## 16. Interpretation and Limitations

A drift alert does **not** automatically prove that the model is inaccurate.

It means that the monitored incoming data has changed according to the configured statistical method and threshold.

Likewise, statistical significance does not automatically mean business significance. A detected change may be expected because of a legitimate business or population change.

GuardDog is therefore a **data monitoring and decision-support system**, not an automatic model-retraining system.

Kafka provides the real-time ingestion layer, but the statistical detector still evaluates meaningful batches rather than individual records.

The statistical methods also have limitations. KS is primarily a univariate numerical test, PSI depends on its binning scheme, and Chi-Square requires appropriate categorical data and sufficient observations.

---

## 17. Current Project Status

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
- Reference profiler implemented
- Reference profile generated
- KS drift detection implemented
- PSI drift detection implemented
- Chi-Square drift detection implemented
- Drift report generation implemented
- Controlled numerical drift validated
- Controlled categorical drift validated

### Current

- Kafka streaming layer
- Feature-selection consistency cleanup

### Next

- Kafka producer
- Kafka consumer
- Streaming batch builder
- Dynamic drift monitoring
- Streamlit dashboard
- Automated tests
- Final integration and documentation

---

## 18. Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core implementation |
| **pandas** | Data loading and transformation |
| **NumPy** | Numerical operations |
| **SciPy** | Statistical tests |
| **scikit-learn** | Supporting ML utilities |
| **Apache Kafka** | Real-time data streaming |
| **Streamlit** | Dashboard |
| **pytest** | Automated testing |

The stack is intentionally small. Kafka is the only infrastructure component added for real-time ingestion because it directly supports the project's core monitoring objective.

---

## 19. Future Scope

Possible future extensions include:

- Additional fairness metrics
- Multivariate drift detection
- Concept-drift detection
- Online or continual learning
- Model-performance monitoring when labels become available
- Automated retraining workflows
- Additional benchmark datasets
- Advanced MLOps integrations
- Kafka Streams or distributed stream processing
- Cloud deployment
- PDF model-health reporting

These extensions are documented as future work so that the internship MVP remains focused and maintainable.

---

## 20. Project Philosophy

> **The goal is a complete working monitoring system, not the maximum number of features.**

GuardDog prioritizes:

- clear architecture;
- small independent modules;
- reproducible experiments;
- statistically grounded drift detection;
- real-time streaming ingestion;
- understandable results; and
- a maintainable implementation.

Kafka is used because real systems receive data continuously. The project deliberately avoids adding additional distributed infrastructure that is not required for the central objective.
