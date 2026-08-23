# GuardDog AI

**Continuous Model Integrity and Observability Pipeline**

GuardDog AI is an MLOps validation and observability system designed to detect meaningful distribution shifts, monitor algorithmic fairness, and provide an auditable view of model health.

The project is deliberately designed as a **modular MVP plus research-extension roadmap**. The MVP focuses on robust univariate and categorical drift detection, fairness auditing, statistical safeguards, simulation, visualization, and reporting. Advanced multivariate, causal, adaptive, and continual-learning capabilities are documented as extensions rather than assumed to be implemented.

## Project Status

**Phase:** Dataset selection and Reference Profiling setup  
**Implementation window:** 17 August 2026 – 6 November 2026

## Core Modules

1. **Reference Profiler** — establishes statistical baselines from training/reference data.
2. **Drift & Bias Engine** — compares production-like data with the reference baseline using statistical drift detection and fairness auditing.
3. **Interactive Observability Dashboard** — presents model-health telemetry through Streamlit.
4. **Reporting Pipeline** — generates PDF Model Health Certificates for audit and quality oversight.

## MVP Drift Detection

### Numerical features

- **Kolmogorov–Smirnov (KS) Test**
  - p-value < 0.05 → Standard Warning
  - p-value < 0.01 → Strict Alert
- **Population Stability Index (PSI)**
  - < 0.10 → Stable
  - 0.10–0.25 → Warning
  - > 0.25 → Action Required

### Categorical features

- **Pearson Chi-Squared** testing for categorical distribution changes.
- PSI may also be used where the categorical representation and binning are appropriate.

### Statistical safeguards

- PSI zero-frequency protection uses `epsilon = 1e-8`.
- Sample-size checks prevent weak evidence from being presented as a definitive conclusion.
- Multiple-testing correction is applied when many feature-level hypothesis tests are evaluated; Benjamini–Hochberg FDR is the practical default candidate, with Bonferroni available for stricter control.

## Fairness Auditing

The MVP includes **Demographic Parity** auditing across:

- Age
- Gender
- Region

Fairness results must be interpreted with subgroup sample size in mind. Additional fairness criteria such as Equal Opportunity, Equalized Odds, Disparate Impact, calibration, and intersectional analysis are planned extensions.

## Dataset Strategy

GuardDog uses a **primary dataset + benchmark datasets + controlled synthetic scenarios** rather than forcing every experiment into one dataset.

### Primary dataset — IBM Telco Customer Churn

The Telco Customer Churn dataset is the primary end-to-end demonstration dataset. It supports a customer-churn prediction use case and provides numerical, categorical, demographic, service, and location information suitable for the GuardDog requirements.

The primary dataset will be used for:

- ML model training;
- reference profiling;
- production-like drift simulation;
- KS/PSI/Chi-Squared monitoring;
- demographic fairness monitoring; and
- dashboard/report demonstrations.

`region` will be an explicitly documented engineered attribute derived from the dataset's available geographic information. The raw source schema will not be misrepresented as already containing a native `region` field.

### Secondary benchmark — UCI Adult

Adult is retained as a **fairness benchmark**, not the primary project dataset. It is useful for validating demographic-parity behavior on an established classification dataset.

### Secondary benchmark — South German Credit

South German Credit is retained as a **credit-risk benchmark** to test the monitoring components on a second business domain.

### Controlled validation — Synthetic data

Synthetic scenarios will be used to inject known changes into the reference distribution, including stable data, small drift, major drift, categorical drift, and controlled fairness deviations. This gives the project a known ground truth for detector validation.

### Dataset architecture principle

The Reference Profiler and future monitoring components must be **dataset-agnostic**. Dataset-specific loading, cleaning, and feature mapping belongs in dataset adapters/configuration rather than inside the statistical engines.

Raw datasets are not committed to Git. See `data/README.md` for the local data policy.

## Drift Scope & Limitations

GuardDog distinguishes among:

- **Covariate shift:** change in `P(X)`;
- **Label shift:** change in `P(Y)`; and
- **Concept/conditional drift:** change in `P(Y|X)`.

The MVP primarily detects observable feature-distribution drift. KS, PSI, and Chi-Squared are not sufficient to guarantee detection of every multivariate or conditional change. Large samples can also make very small differences statistically significant, which is why KS is paired with magnitude-oriented PSI and statistical safeguards.

## Research Extensions

The research roadmap includes:

- multivariate drift detection such as MMD or classifier-based drift;
- adaptive thresholds using EWMA/CUSUM/Page-Hinkley-style methods;
- drift explainability and root-cause analysis;
- label-delay handling;
- expanded and intersectional fairness metrics;
- continual learning and retraining triggers;
- causal drift analysis; and
- richer compliance/provenance artifacts.

These are **not MVP claims** unless implemented and tested.

## Repository Structure

```text
guarddog-ai/
├── README.md
├── docs/
│   ├── project-specification.md
│   ├── architecture.md
│   └── roadmap.md
├── src/
│   └── guarddog/
├── tests/
├── data/
│   ├── README.md
│   ├── raw/          # local, gitignored
│   └── processed/    # local, gitignored
├── notebooks/
├── reports/
├── requirements.txt
└── .gitignore
```

## Development Principle

Build and validate the MVP before adding advanced research extensions. Every capability claimed in the README must have corresponding implementation and tests.

## Reference

The repository is being developed from the supplied GuardDog AI technical project specification and deep-research report. See `docs/project-specification.md` for the working requirements baseline and `docs/architecture.md` for the research-aligned system design.