# GuardDog AI — Project Specification

## 1. Project Title

**GuardDog AI — Continuous Model Integrity and Observability Pipeline**

## 2. Problem Statement

Machine learning models can experience performance degradation as production data distributions evolve. A deployed model may continue producing predictions while the underlying data has shifted, resulting in silent performance decay and potential algorithmic bias.

GuardDog AI is intended to provide continuous validation and observability for these conditions.

The research review also makes an important scope distinction: **data drift, label shift, and concept drift are different phenomena**. The initial GuardDog implementation primarily targets observable input/marginal distribution drift, while label-shift, conditional/concept drift, and more advanced multivariate detection are documented as extensions rather than claimed capabilities of the MVP.

## 3. Objective

Build a continuous validation and observability pipeline that:

- detects data drift;
- identifies statistically significant distribution changes;
- distinguishes statistical significance from practical shift magnitude using complementary drift metrics;
- audits demographic fairness;
- accounts for statistical reliability issues such as sample size and multiple testing; and
- presents findings through an interactive observability dashboard and formal Model Health Certificates.

## 4. System Scope

The system is divided into four core modules.

### 4.1 Reference Profiler

Creates the statistical baseline from the training/reference dataset. The baseline is used as the comparison point for later simulated production data.

The reference profiling phase is expected to capture distributions, variances, and demographic ratios required by downstream drift and fairness analysis.

### 4.2 Drift & Bias Engine

Compares production-like data against the reference baseline.

### MVP statistical capabilities

The engine must support:

- **Kolmogorov–Smirnov (KS)** testing for numerical/univariate distribution comparisons;
- **Population Stability Index (PSI)** as a complementary measure of shift magnitude;
- **Chi-Squared goodness-of-fit testing** for categorical distributions;
- threshold-based severity classification;
- zero-frequency numerical safeguards;
- sample-size checks before interpreting statistical results;
- multiple-testing correction across repeated feature tests; and
- Demographic Parity auditing across the specified sensitive attributes.

### Research extensions

The research review identifies additional capabilities that are valuable but are **not required for the initial MVP**:

- multivariate drift detection such as MMD or classifier-based drift detection;
- adaptive thresholds using EWMA, CUSUM, or Page-Hinkley-style methods;
- label-delay handling;
- drift explainability/root-cause analysis;
- expanded fairness metrics and intersectional analysis;
- continual learning and automated retraining triggers; and
- causal drift detection.

These extensions must not be represented as implemented capabilities until they are actually built and tested.

### 4.3 Interactive Observability Dashboard

A Streamlit-based interface will present model-health telemetry and detected issues in an interactive form.

### 4.4 Reporting Pipeline

The system will generate PDF **Model Health Certificates** summarizing model-health findings for audit and quality oversight.

## 5. Drift Detection Specification

### 5.1 Kolmogorov–Smirnov Test

The KS test is used to identify statistically significant differences between two univariate continuous distributions.

| Condition | Classification |
|---|---|
| p-value < 0.05 | Standard Warning |
| p-value < 0.01 | Strict Alert |

The KS result must be interpreted with sample size in mind. Large samples can make extremely small practical differences statistically significant, so KS must not be treated as a standalone measure of operational severity.

### 5.2 Population Stability Index

PSI provides a complementary measure of distribution-shift magnitude.

| PSI | Classification |
|---:|---|
| < 0.10 | Stable |
| 0.10–0.25 | Warning |
| > 0.25 | Action Required |

PSI depends on meaningful, consistent binning and sufficient observations per bin. Small or sparse bins should be combined or handled cautiously rather than producing false confidence.

### 5.3 Chi-Squared Test for Categorical Drift

Categorical features such as region, occupation, or employment type should be evaluated using an appropriate categorical distribution test. The initial design uses Pearson's Chi-Squared goodness-of-fit test, subject to expected-count assumptions.

### 5.4 Multiple-Testing Control

When drift tests are run across many features, raw p-values can create false alarms. The implementation should therefore support a multiple-testing correction strategy such as:

- **Benjamini–Hochberg False Discovery Rate (FDR)** for a practical default; or
- **Bonferroni correction** when stricter family-wise error control is required.

The correction method used for a run must be recorded in its results.

### 5.5 Sample-Size Safeguards

Statistical results should include sufficient-sample checks before being classified as reliable. The research review gives practical guidance such as roughly 30+ observations per sample for basic KS use, adequate observations per PSI bin, and adequate subgroup counts for fairness metrics. These are **guidance rather than universal mathematical guarantees** and should be treated as configurable validation rules.

If sample size is insufficient, the system should report **Insufficient Evidence** rather than manufacture a drift/fairness conclusion.

### 5.6 Zero-Bin Mitigation

The PSI implementation must guard against zero-frequency bins using:

```text
ε = 1 × 10⁻⁸
```

This prevents numerical problems when calculating PSI for bins with zero observed or expected frequency.

## 6. Drift Taxonomy and Limitations

GuardDog documentation distinguishes:

- **Covariate shift:** P(X) changes while P(Y|X) is assumed stable.
- **Label shift:** P(Y) changes while P(X|Y) is assumed stable.
- **Concept/conditional drift:** P(Y|X) changes.

The MVP primarily detects changes in observed feature distributions. KS/PSI/Chi-Squared on individual features do **not** guarantee detection of every multivariate, conditional, or causal change.

The system should therefore avoid claiming that a stable marginal distribution proves the underlying ML model is fully healthy.

## 7. Fairness Specification

The fairness component must include Demographic Parity auditing across:

- Age
- Gender
- Region

The initial implementation may use demographic-parity differences as the primary fairness signal. The research review recommends considering additional metrics such as Equal Opportunity, Equalized Odds, Disparate Impact Ratio, calibration differences, and intersectional groups in later iterations.

Fairness measurements must also account for subgroup sample sizes. When subgroup evidence is insufficient, the result should be marked accordingly rather than treated as a definitive disparity conclusion.

## 8. Dataset Strategy

GuardDog uses a **primary dataset + benchmark datasets + controlled synthetic scenarios**.

### 8.1 Primary dataset — IBM Telco Customer Churn

The IBM Telco Customer Churn dataset is the primary end-to-end demonstration dataset. It is selected because the project needs a realistic tabular classification problem with numerical and categorical features, a churn target, demographic attributes, and geographic information suitable for the GuardDog monitoring workflow.

The primary dataset will be used for:

- ML model training;
- reference profiling;
- production-like drift simulation;
- KS/PSI/Chi-Squared monitoring;
- demographic fairness monitoring; and
- dashboard/report demonstrations.

The logical `region` field will be an explicitly documented engineered attribute derived from the source location information if the selected source files do not provide a native region field. The raw source schema must never be misrepresented.

### 8.2 Secondary benchmark — UCI Adult

UCI Adult is retained primarily as a fairness benchmark. It is not the primary end-to-end dataset. It can be used to validate demographic-parity behavior on an established classification benchmark.

### 8.3 Secondary benchmark — South German Credit

South German Credit is retained as a credit-risk-domain benchmark for validating the monitoring components on a second business domain.

### 8.4 Controlled validation — Synthetic data

Synthetic scenarios will be generated from the primary reference data to create known conditions including no drift, small drift, major drift, categorical drift, gradual drift, sudden drift, and controlled fairness deviations. This provides known ground truth for detector validation.

### 8.5 Dataset-agnostic architecture

Statistical engines must not contain dataset-specific logic. Loading, cleaning, feature mapping, target definitions, and engineered attributes belong in dataset adapters/configuration. See `docs/dataset-strategy.md`.

Raw datasets are not committed to Git. Local data storage is documented separately.

## 9. Expected Technical Stack

The project specification identifies:

- Python
- pandas
- NumPy
- SciPy
- scikit-learn
- Streamlit
- Plotly
- ReportLab

Exact package versions will be pinned during environment setup.

## 10. Planned Development Sequence

The project will be implemented incrementally:

1. Dataset selection and environment validation
2. Reference profiling
3. Drift detection engine (KS, PSI, Chi-Squared, safeguards)
4. Fairness analysis
5. Drift simulation and benchmark scenarios
6. Streamlit observability dashboard
7. PDF Model Health Certificates
8. Testing, validation, documentation, and final integration

Research extensions will be scheduled only after the MVP is stable.

## 11. Initial Acceptance Criteria

The initial implementation should ultimately demonstrate that:

- a reference baseline can be generated from the selected primary dataset;
- simulated production data can be compared with that baseline;
- KS and PSI results are calculated according to the defined thresholds;
- categorical drift can be evaluated with Chi-Squared testing;
- multiple-testing correction is applied when interpreting many feature-level p-values;
- insufficient sample sizes are surfaced rather than hidden;
- zero-frequency bins do not cause PSI calculation failures;
- demographic parity is audited for Age, Gender, and Region;
- benchmark datasets can be used without rewriting the statistical engines;
- findings are visible in an interactive dashboard; and
- a PDF Model Health Certificate can be generated from the analysis results.

## 12. Research-Grounded Limitations

The research review identifies several limitations that must remain explicit in the project documentation:

- KS is univariate and can become over-sensitive with large samples.
- PSI is heuristic and sensitive to binning and sparse bins.
- Univariate tests can miss changes in feature relationships or joint distributions.
- Fairness metrics can be unreliable with small subgroups and do not provide a universal definition of fairness.
- Delayed ground-truth labels limit immediate performance monitoring.
- Repeated testing requires false-discovery control.

These limitations are part of the engineering and evaluation scope, not reasons to claim the system is ineffective.

## 13. Source of Requirements

This document captures the supplied GuardDog AI project specification and incorporates findings from the supplied deep-research report. The original project thresholds and core modules remain the baseline requirements; research-derived additions are explicitly marked as MVP safeguards or extensions. Future changes to scope, thresholds, architecture, dataset requirements, or deliverables should be recorded explicitly rather than silently replacing these requirements.