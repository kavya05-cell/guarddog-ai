# GuardDog AI

**Continuous Model Integrity and Observability Pipeline**

GuardDog AI is an MLOps validation and observability system designed to detect meaningful distribution shifts, monitor algorithmic fairness, and provide an auditable view of model health.

## Project Status

**Phase:** Project initialization and specification capture  
**Implementation window:** 17 August 2026 – 6 November 2026

## Core Modules

1. **Reference Profiler** — establishes statistical baselines from training data.
2. **Drift & Bias Engine** — compares simulated production data with the reference baseline using drift detection and fairness auditing.
3. **Interactive Observability Dashboard** — presents model-health telemetry through Streamlit.
4. **Reporting Pipeline** — generates PDF Model Health Certificates for audit and quality oversight.

## Drift Detection

GuardDog AI uses a dual-metric strategy:

- **Kolmogorov–Smirnov (KS) Test**
  - p-value < 0.05 → Standard Warning
  - p-value < 0.01 → Strict Alert
- **Population Stability Index (PSI)**
  - < 0.10 → Stable
  - 0.10–0.25 → Warning
  - > 0.25 → Action Required

The PSI implementation uses an epsilon value of `1e-8` to mitigate zero-frequency numerical issues.

## Fairness Auditing

The project includes Demographic Parity auditing across the sensitive attributes specified in the project specification:

- Age
- Gender
- Region

## Initial Dataset Requirements

The selected tabular dataset must contain:

- numerical features
- categorical features
- a target variable
- age, gender, and region attributes suitable for fairness auditing

Candidate domains in the project specification include financial credit scoring and customer churn.

## Repository Structure

```text
guarddog-ai/
├── README.md
├── docs/
│   ├── project-specification.md
│   ├── architecture.md
│   └── roadmap.md
├── src/
├── tests/
├── data/
├── notebooks/
├── reports/
├── requirements.txt
└── .gitignore
```

## Reference

The repository is being developed from the supplied GuardDog AI technical project specification. See `docs/project-specification.md` for the captured requirements.