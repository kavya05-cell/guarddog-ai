# GuardDog AI — Research-Aligned Implementation Roadmap

## Project Window

**17 August 2026 – 6 November 2026**

The roadmap preserves the original project window while separating the **MVP requirements** from research-driven extensions. The goal is to finish a reliable core system before attempting advanced detectors.

## Sprint 1 — Dataset & Reference Profiling

**17–28 August 2026**

### Dataset decision

- **Primary:** IBM Telco Customer Churn
- **Fairness benchmark:** UCI Adult
- **Credit-risk benchmark:** South German Credit
- **Controlled validation:** synthetic scenarios generated from the primary reference data

Goal: validate the primary dataset schema and establish the statistical reference baseline.

Deliverables:

- selected primary dataset;
- documented benchmark strategy;
- numerical and categorical feature inventory;
- target and sensitive-attribute validation;
- documented region mapping/engineering where required;
- reference distributions;
- variance/statistical summaries; and
- demographic ratios required by downstream analysis.

## Sprint 2 — Core Drift Detection Engine

**31 August – 11 September 2026**

Goal: implement and test the core statistical detectors.

Deliverables:

- validated KS implementation;
- PSI implementation;
- Chi-Squared categorical drift implementation;
- threshold logic;
- zero-bin numerical mitigation; and
- sample-size validation.

## Sprint 3 — Fairness & Statistical Reliability

**14–25 September 2026**

Goal: implement fairness auditing and reduce false alerts from repeated testing.

Deliverables:

- Demographic Parity auditing;
- Age, Gender, and Region analysis;
- subgroup sample-size checks;
- multiple-testing correction using FDR and/or Bonferroni; and
- documented statistical decision logic.

## Sprint 4 — Drift Simulation & Benchmark Validation

**28 September – 9 October 2026**

Goal: create controlled production-like scenarios and validate detector behavior across the primary dataset and selected benchmarks.

Scenarios should include:

- stable/no-drift data;
- small drift;
- major drift;
- categorical distribution changes; and
- controlled fairness deviations.

Validation should measure false alarms, detection behavior, and threshold consistency.

## Sprint 5 — Streamlit Observability Dashboard

**12–23 October 2026**

Goal: integrate monitoring outputs into an interactive stakeholder-facing dashboard.

Dashboard scope:

- feature distributions;
- KS/PSI/Chi-Squared results;
- drift severity;
- fairness metrics;
- drift status over time; and
- insufficient-evidence warnings.

## Sprint 6 — PDF Model Health Certificates

**26 October – 30 October 2026**

Goal: generate formal PDF monitoring reports.

Certificate scope:

- run metadata;
- baseline/production summary;
- drift findings;
- fairness findings;
- statistical safeguards applied; and
- overall health status.

## Sprint 7 — Integration, Testing & Final Documentation

**31 October – 6 November 2026**

Goal:

- integrate all modules;
- run pytest unit/integration tests;
- validate controlled scenarios;
- finalize technical documentation;
- document limitations; and
- prepare the final mentor showcase.

## Research Extensions — After MVP

These are intentionally **not prerequisites for the initial MVP**.

### Short-term extensions

- Multivariate drift detection using MMD or classifier-based tests.
- Drift explainability/root-cause analysis.
- Improved dashboard diagnostics.

### Medium-term extensions

- Adaptive thresholds using EWMA/CUSUM/Page-Hinkley-style monitoring.
- Label-delay handling.
- Expanded fairness metrics such as Equal Opportunity, Equalized Odds, Disparate Impact, and intersectional analysis.
- API/integration layer and alert hooks.
- Continual learning/retraining triggers.

### Long-term research extensions

- Causal drift detection.
- Synthetic generative drift simulation.
- Advanced compliance/provenance artifacts.
- Large-scale distributed deployment.

## MVP Definition of Done

The MVP is complete only when the system can reproducibly:

1. profile the selected primary reference dataset;
2. validate the dataset schema and evidence size;
3. compare production-like data with the reference;
4. run KS/PSI for numerical features;
5. run Chi-Squared/PSI for categorical features where appropriate;
6. apply the configured multiple-testing correction;
7. audit Demographic Parity for Age, Gender, and Region;
8. run controlled drift/fairness scenarios;
9. validate benchmark datasets without rewriting statistical engines;
10. display results in Streamlit;
11. generate a Model Health Certificate; and
12. pass automated tests for the complete workflow.

## Immediate Next Step

The dataset strategy is now defined. The immediate engineering task is to **obtain and inspect the primary IBM Telco Customer Churn data**, record its exact source schema, define the logical GuardDog feature mapping, and then implement the Reference Profiler against that configuration.
