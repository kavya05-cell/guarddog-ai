# GuardDog AI — Research-Aligned Architecture

## 1. High-Level Flow

```text
Reference / Training Data
        │
        ▼
┌──────────────────────┐
│ Reference Profiler   │
└──────────┬───────────┘
           │ baseline profile
           ▼
┌────────────────────────────────────────────┐
│          Drift & Bias Engine               │
│                                            │
│ Numerical features                         │
│   ├── KS Test                              │
│   └── PSI                                  │
│                                            │
│ Categorical features                       │
│   ├── Chi-Squared                          │
│   └── PSI                                  │
│                                            │
│ Statistical safeguards                     │
│   ├── Sample-size validation               │
│   └── Multiple-testing correction          │
│                                            │
│ Fairness                                   │
│   └── Demographic Parity                   │
└──────────────────┬─────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
   Observability        Reporting
      Layer              Pipeline
   ┌───────────┐        ┌───────────┐
   │ Streamlit │        │ ReportLab │
   └─────┬─────┘        └─────┬─────┘
         │                    │
         ▼                    ▼
    Dashboard          Model Health
                         Certificate
```

## 2. Data Flow

1. The **Reference Profiler** summarizes the selected training/reference dataset.
2. A production-like batch is supplied to the engine.
3. The engine validates schema and sample-size conditions.
4. Numerical features are evaluated with KS and PSI.
5. Categorical features are evaluated with Chi-Squared and PSI where appropriate.
6. Feature-level p-values are corrected when multiple hypothesis tests are performed.
7. Fairness analysis evaluates demographic parity across Age, Gender, and Region.
8. Results are classified into operational statuses and passed to the dashboard and reporting pipeline.

## 3. Components

### Reference Profiler

Responsible for establishing the reference state from the selected training dataset.

Expected outputs include:

- numerical feature summaries;
- categorical frequency profiles;
- variance/statistical summaries; and
- demographic ratios.

### Drift & Bias Engine

Responsible for statistical comparison between the reference state and production-like data, plus fairness auditing.

The engine is intentionally modular so individual detectors can be tested independently.

### Observability Dashboard

Responsible for presenting analysis results and model-health telemetry interactively through Streamlit.

### Reporting Pipeline

Responsible for producing a formal PDF Model Health Certificate from monitoring results.

## 4. Statistical Decision Layer

The project separates **statistical significance** from **operational magnitude**.

```text
Feature comparison
       │
       ├── KS p-value ──────────► Statistical evidence
       │
       ├── PSI ─────────────────► Practical magnitude
       │
       └── Chi-Squared p-value ─► Categorical evidence
                    │
                    ▼
          Multiple-test correction
                    │
                    ▼
             Health classification
```

KS must not be used alone because very large samples can make tiny differences statistically significant. PSI provides a complementary magnitude signal but depends on stable, meaningful binning.

## 5. Statistical Safeguards

### Sample size

The engine should validate minimum evidence conditions before reporting a definitive result. Insufficient samples should produce an explicit **Insufficient Evidence** status.

### Multiple testing

When multiple feature-level hypothesis tests are performed, the engine should support Benjamini–Hochberg FDR and/or Bonferroni correction.

### Zero-frequency bins

PSI calculations use `ε = 1e-8` to avoid division-by-zero and `log(0)` numerical failures.

## 6. Research Extensions

The architecture leaves explicit extension points for:

- multivariate drift detection (e.g. MMD or classifier-based drift);
- adaptive thresholding (EWMA, CUSUM, Page-Hinkley-style methods);
- label-delay handling;
- drift explainability/root-cause analysis;
- expanded and intersectional fairness metrics;
- continual learning and retraining triggers; and
- causal drift analysis.

These are future capabilities, not MVP claims.

## 7. Design Principle

Components remain modular so profiling, statistical detection, fairness auditing, visualization, and reporting can be tested independently and integrated later into a continuous workflow.

## 8. Architecture Status

This is the **research-aligned architecture baseline**. Dataset selection and implementation details can refine the design, but changes should be documented explicitly in the repository.
