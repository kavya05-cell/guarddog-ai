# GuardDog AI
## Pre-Implementation Software Requirements and System Design Specification

**Project:** GuardDog AI — Continuous Model Integrity and Observability Pipeline  
**Document Type:** Pre-Implementation Specification  
**Version:** 1.0  
**Status:** Approved for implementation planning  
**Repository:** `kavya05-cell/guarddog-ai`

---

## 1. Document Purpose

This document defines the problem, scope, requirements, proposed solution, methodology, system architecture, data strategy, and implementation plan for GuardDog AI before detailed software implementation begins.

The purpose is to establish a common understanding of what the system is expected to do and why it is being built. It is intended to be understandable to both technical and non-technical readers and to serve as the reference point for subsequent development and testing.

This document deliberately separates **requirements and design decisions** from implementation details. Source code is developed only after the behaviour of the system and its expected outputs have been defined.

---

## 2. Executive Overview

Machine learning models are usually evaluated before deployment. That evaluation, however, describes the data and conditions available at the time of development. Once a model is used in the real world, the population it receives as input can change.

A customer population can change, financial behaviour can change, user preferences can change, and operating conditions can change. As a result, the data reaching a deployed model may no longer resemble the data on which the model was trained.

A model can therefore continue to run normally while its assumptions become less reliable.

GuardDog AI is proposed as a monitoring and validation layer around an ML system. It establishes a statistical reference from the training data, compares subsequent production-like data with that reference, detects distribution changes, audits selected fairness characteristics, and presents the results in a form that can be reviewed by technical and business stakeholders.

The system is not intended to replace the prediction model. Its role is to provide evidence about the condition of the data and model environment in which that model operates.

---

## 3. Background and Problem Statement

### 3.1 Why machine learning models need monitoring

A traditional software application is normally expected to behave according to a relatively stable set of rules. Machine learning systems are different because their behaviour depends on patterns learned from historical data.

When the environment changes, those learned patterns may become less representative of current conditions.

For example, suppose a customer-churn model was trained using a population whose average customer age was approximately 35 years. If the model later receives a population with a substantially different age distribution, the input population is no longer the same as the original training population.

The model may still produce predictions. The application may still be online. CPU and memory may still look normal. None of those operational signals proves that the model is still receiving data similar to what it learned from.

This creates a monitoring gap between **system availability** and **model reliability**.

### 3.2 Data drift

**Data drift** refers to a change in the distribution of input data between a reference population and a later population.

In simple terms:

> The model is seeing data that looks different from the data it was built with.

A change in a single observation is not necessarily drift. Drift concerns a change in the statistical distribution of a feature or population.

For example:

```text
Reference population
Age 25–34: 42%
Age 35–44: 31%
Age 45–54: 18%
Other:      9%

Production population
Age 25–34: 21%
Age 35–44: 29%
Age 45–54: 28%
Other:     22%
```

The production population has a different age distribution from the reference population. A monitoring system should make this change visible rather than relying on manual inspection.

### 3.3 Concept drift

Data drift and concept drift are related but not identical.

**Data drift** concerns a change in the input distribution. **Concept drift** concerns a change in the relationship between inputs and the outcome being predicted.

For example, customer behaviour can change so that the same customer characteristics no longer have the same relationship with churn as they did when the model was trained.

GuardDog AI's initial implementation focuses primarily on observable distribution drift and fairness monitoring. Full concept-drift and performance monitoring requiring reliable post-deployment labels is outside the first implementation scope.

### 3.4 The monitoring problem

Without a dedicated monitoring process, several issues can remain hidden:

- input distributions may change without an immediate operational failure;
- statistically significant changes may be mistaken for practically important changes;
- fairness characteristics may change without being reviewed regularly;
- monitoring results may exist only as ad-hoc analysis rather than repeatable evidence;
- stakeholders may receive statistical outputs without a clear operational interpretation;
- there may be no consistent historical record of model-health assessments.

The problem is therefore not simply detecting whether numbers changed. The problem is creating a repeatable process that determines **whether the change is statistically meaningful, practically relevant, and important enough to investigate**.

---

## 4. Proposed Solution

GuardDog AI will provide a continuous model-integrity and observability pipeline built around a reference-and-comparison workflow.

The proposed process is:

```text
Training / Reference Data
          |
          v
Reference Profiler
          |
          v
Statistical Baseline
          |
          v
Production or Simulated Production Data
          |
          v
Drift & Bias Engine
          |
          +-------------------+
          |                   |
          v                   v
   Drift Analysis       Fairness Audit
          |                   |
          +---------+---------+
                    |
                    v
          Model Health Results
             /            \
            v              v
     Dashboard          Report
```

The solution is divided into four major functional modules:

1. **Reference Profiler** — establishes the statistical baseline.
2. **Drift & Bias Engine** — evaluates new data against the baseline and performs fairness auditing.
3. **Interactive Observability Dashboard** — presents results in a stakeholder-readable form.
4. **Reporting Pipeline** — produces formal Model Health Certificates for record keeping and review.

---

## 5. Objectives

### 5.1 Primary objectives

GuardDog AI shall:

- establish a reproducible statistical baseline from reference data;
- detect changes in numerical and categorical feature distributions;
- distinguish statistical significance from practical magnitude where the selected methodology permits;
- audit demographic parity across the specified demographic attributes;
- provide understandable model-health status information;
- preserve the results of monitoring in a formal report;
- use modular components so that statistical methods and data sources can be extended later.

### 5.2 Quality objectives

The implementation should prioritize:

- reproducibility;
- statistical transparency;
- leakage-safe processing;
- explicit handling of missing values;
- testability;
- modularity;
- clear separation between computation and presentation;
- understandable outputs for non-specialist stakeholders.

---

## 6. Scope

### 6.1 In scope

The initial GuardDog AI implementation includes:

- tabular reference-data profiling;
- numerical feature statistics;
- categorical feature distributions;
- missing-value monitoring;
- reference demographic ratios;
- production-batch comparison;
- Kolmogorov–Smirnov testing for suitable numerical distributions;
- Population Stability Index calculation;
- categorical drift analysis where appropriate;
- Demographic Parity auditing for age, gender, and region;
- Streamlit-based visualization;
- PDF Model Health Certificates;
- automated unit tests;
- containerization as a later deployment milestone.

### 6.2 Out of scope for the initial version

The first version will not claim to provide:

- universal model-performance monitoring when ground-truth labels are unavailable;
- causal explanations for why drift occurred;
- automatic model retraining;
- automatic deployment approval without defined governance rules;
- complete concept-drift detection;
- protection against every possible form of algorithmic bias;
- a replacement for enterprise observability platforms.

These areas may be considered as future extensions.

---

## 7. Key Concepts

### 7.1 Reference baseline

The baseline represents the statistical characteristics of the population against which future observations are compared.

For GuardDog AI, the reference profile will contain feature-level information such as distributions, numerical summaries, missingness, and demographic ratios.

The baseline answers:

> What did the data look like when the reference was established?

### 7.2 Drift detection

Drift detection is the statistical comparison between the reference population and a later population.

The purpose is not to declare every difference a failure. The purpose is to identify changes that warrant attention.

### 7.3 Model observability

Model observability extends ordinary application monitoring to information relevant to machine learning systems, including:

- input distributions;
- missingness;
- prediction-related characteristics;
- drift measurements;
- fairness indicators;
- historical monitoring results.

GuardDog AI focuses on the data and statistical side of this observability problem.

### 7.4 Fairness

A model can be accurate overall while producing different outcome patterns across demographic groups. Fairness monitoring therefore needs to be considered separately from aggregate model performance.

The initial project specification selects **Demographic Parity** and focuses on age, gender, and region.

---

## 8. Functional Requirements

### FR-01 — Reference data ingestion

The system shall accept a validated tabular reference dataset.

### FR-02 — Reference profiling

The system shall generate a baseline profile containing relevant statistical characteristics for supported feature types.

### FR-03 — Numerical feature monitoring

The system shall calculate and retain numerical distribution statistics required for later drift comparison.

### FR-04 — Categorical feature monitoring

The system shall calculate category frequencies or proportions for supported categorical features.

### FR-05 — Missingness monitoring

The system shall record missing-value counts or proportions so that changes in data completeness can be detected.

### FR-06 — Production-batch ingestion

The Drift & Bias Engine shall accept a production or simulated-production batch with a schema compatible with the reference profile.

### FR-07 — KS testing

The system shall apply the Kolmogorov–Smirnov test to supported continuous numerical features.

### FR-08 — PSI calculation

The system shall calculate Population Stability Index values using consistent reference and comparison bins.

### FR-09 — Categorical drift

The system shall support categorical distribution comparison using an appropriate statistical method, including Chi-Squared testing where applicable.

### FR-10 — Fairness auditing

The system shall evaluate Demographic Parity across age, gender, and region using the available outcome or prediction information.

### FR-11 — Alert classification

The system shall translate statistical results into defined monitoring statuses according to the approved thresholds and decision rules.

### FR-12 — Dashboard

The system shall present drift, fairness, and model-health information through an interactive Streamlit interface.

### FR-13 — Reporting

The system shall generate a PDF Model Health Certificate containing the relevant monitoring findings.

### FR-14 — Reproducibility

The same reference data, configuration, and comparison data shall produce reproducible results, subject to the deterministic behaviour of the implemented statistical procedures.

### FR-15 — Validation

The system shall validate input schema and required fields before performing monitoring calculations.

---

## 9. Non-Functional Requirements

### NFR-01 — Modularity

Statistical methods, preprocessing, reporting, and presentation shall remain separated into maintainable modules.

### NFR-02 — Testability

Core statistical and preprocessing functions shall be independently testable.

### NFR-03 — Transparency

Every alert should be traceable to the feature, metric, threshold, and comparison that produced it.

### NFR-04 — Usability

Dashboard and report outputs shall provide plain-language interpretations in addition to statistical values.

### NFR-05 — Data integrity

The pipeline shall not silently discard observations or transform values without a documented reason.

### NFR-06 — Extensibility

The architecture shall permit additional drift metrics, datasets, fairness measures, and reporting formats to be added without rewriting the entire system.

### NFR-07 — Reliability

Invalid inputs and missing required fields shall result in explicit validation errors rather than misleading monitoring results.

---

## 10. Drift Detection Methodology

GuardDog AI uses more than one measurement because statistical significance and practical magnitude answer different questions.

### 10.1 Kolmogorov–Smirnov test

The KS test compares two distributions and is appropriate for supported continuous numerical features.

For GuardDog AI, the planned interpretation is:

| Result | Status |
|---|---|
| p-value >= 0.05 | No statistically significant drift detected by KS |
| p-value < 0.05 | Standard warning |
| p-value < 0.01 | Strict alert |

The KS test is sensitive to sample size. With very large samples, small differences can become statistically significant. For that reason, KS is not treated as the sole decision signal.

### 10.2 Population Stability Index

PSI provides a measure of the magnitude of distribution change using defined bins.

Planned operational interpretation:

| PSI | Status | Interpretation |
|---:|---|---|
| < 0.10 | Stable | Population is broadly consistent with the reference |
| 0.10–0.25 | Warning | Noticeable shift; increase monitoring |
| > 0.25 | Action Required | Major shift; investigate the model/data and consider remediation |

The exact numerical value is retained alongside the status so that users can inspect the evidence rather than seeing only a colour or label.

### 10.3 Zero-bin handling

PSI calculations can encounter zero frequencies. The implementation will use a small epsilon value of `1e-8` where required to avoid division-by-zero and logarithm-of-zero numerical errors.

This is a numerical safeguard, not an additional statistical threshold.

### 10.4 Categorical drift

Categorical variables cannot be treated as continuous distributions. Where appropriate, categorical frequency distributions will be compared using a categorical statistical test such as Chi-Squared.

The method and interpretation will be documented separately from the KS/PSI workflow rather than forcing all variables through one test.

### 10.5 Multiple comparisons

When many features are tested simultaneously, the probability of obtaining a statistically significant result by chance increases. The implementation should therefore retain the information needed for multiple-testing correction or explicitly document the chosen policy when the final drift engine is implemented.

---

## 11. Fairness Methodology

### 11.1 Demographic Parity

Demographic Parity examines whether the rate of a selected outcome or prediction is comparable across demographic groups.

For a binary outcome, the basic group rate is:

```text
Outcome Rate(group) = Positive Outcomes in Group / Total Observations in Group
```

GuardDog AI will compare these rates across the specified attributes:

- Age
- Gender
- Region

### 11.2 Fairness interpretation

A difference in group rates is a signal for investigation. It should not automatically be interpreted as proof that a model is discriminatory.

The dashboard and report should therefore distinguish between:

- observed disparity;
- statistical evidence, where applicable;
- operational severity;
- the need for further investigation.

### 11.3 Fairness limitations

Demographic Parity measures one aspect of fairness. It does not establish that a model is fair in every sense, nor does it explain the cause of an observed difference.

The initial implementation will therefore describe the metric precisely rather than presenting it as a universal fairness test.

---

## 12. Data Requirements and Dataset Strategy

### 12.1 Dataset characteristics

The primary dataset must contain:

- numerical variables;
- categorical variables;
- a target variable;
- demographic attributes suitable for fairness analysis;
- sufficient observations for statistical comparison.

### 12.2 Primary dataset

**IBM Telco Customer Churn** is selected as the primary end-to-end dataset because it provides mixed numerical and categorical customer data, a churn target, and demographic/location information suitable for the project's monitoring objectives.

The working merged dataset contains 7,043 customer records.

### 12.3 Additional datasets

The project may use additional datasets for focused validation rather than forcing one dataset to demonstrate every research objective.

The selected strategy is:

- **IBM Telco Customer Churn:** primary end-to-end demonstration;
- **UCI Adult:** fairness-focused benchmark;
- **South German Credit:** secondary credit-risk/PSI benchmark;
- **Synthetic data:** controlled drift and fairness experiments where known changes are useful for validation.

The purpose of using multiple datasets is methodological: different datasets are useful for demonstrating different behaviours.

---

## 13. Data Preparation Requirements

Before profiling, the reference data shall be validated and cleaned in a leakage-safe manner.

For the current Telco dataset:

- `Customer ID` shall not be used as a model feature;
- post-outcome fields shall not be used as model features;
- constant/redundant fields shall be removed where justified;
- structurally meaningful missingness shall be handled explicitly;
- `Offer` missingness shall be preserved because its missing state has not been established to mean a specific business category;
- `Internet Type` values corresponding to customers with no internet service shall be represented explicitly as `No Internet`;
- age, gender, region, and churn target shall remain available for monitoring and fairness analysis.

The cleaned dataset shall preserve the number of customer records unless an explicit, documented data-quality rule requires removal.

---

## 14. System Architecture

### 14.1 Logical architecture

```text
                         REFERENCE DATA
                              |
                              v
                   +----------------------+
                   |  Reference Profiler  |
                   +----------+-----------+
                              |
                              v
                     Statistical Baseline
                              |
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
     Production Batch                    Model Metadata
             |                                 |
             +----------------+----------------+
                              |
                              v
                   +----------------------+
                   | Drift & Bias Engine  |
                   +----------+-----------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
             KS              PSI        Categorical/Fairness
              |               |               |
              +---------------+---------------+
                              |
                              v
                    Monitoring Results
                         /          \
                        /            \
                       v              v
              +----------------+  +------------------+
              | Streamlit UI   |  | Reporting        |
              | Dashboard      |  | Pipeline         |
              +----------------+  +--------+---------+
                                            |
                                            v
                                  Model Health Certificate
```

### 14.2 Module responsibilities

#### Reference Profiler

Creates the reference representation of the data. It is responsible for describing the baseline, not for deciding whether production data has drifted.

#### Drift & Bias Engine

Consumes the baseline and comparison batch, performs statistical tests and fairness calculations, and returns structured monitoring results.

#### Dashboard

Presents the results to users. It should not contain the core statistical logic.

#### Reporting Pipeline

Converts structured monitoring results into a formal report. Reporting should not independently recalculate statistical metrics.

---

## 15. Data Flow

The expected data flow is:

```text
Raw Dataset
   |
   v
Validation and Preprocessing
   |
   v
Clean Reference Dataset
   |
   v
Reference Profiler
   |
   v
Reference Profile
   |
   +--------------------------+
                              |
                     Production Batch
                              |
                              v
                     Drift & Bias Engine
                              |
                +-------------+-------------+
                |                           |
                v                           v
          Drift Results              Fairness Results
                |                           |
                +-------------+-------------+
                              |
                              v
                       Model Health Data
                         /           \
                        v             v
                   Dashboard       PDF Report
```

---

## 16. Expected Reference Profile

The reference profile should be machine-readable and should contain enough information for the monitoring engine to perform later comparisons.

At minimum, it should support:

### Numerical features

- feature name;
- data type;
- observation count;
- missing count/rate;
- central tendency statistics;
- dispersion statistics;
- distribution or bin information needed by the selected drift methods.

### Categorical features

- feature name;
- data type;
- observation count;
- missing count/rate;
- category frequencies/proportions;
- known categories.

### Fairness attributes

- attribute name;
- group definitions;
- reference group counts;
- reference outcome/prediction rates where available.

### Configuration

- metric names;
- threshold configuration;
- version information;
- reference dataset metadata.

---

## 17. Expected Monitoring Output

The engine should return structured results rather than only console text.

A feature-level result should contain information such as:

```text
feature
feature_type
reference_size
current_size
missing_rate_reference
missing_rate_current
metric
metric_value
p_value (when applicable)
status
interpretation
```

Fairness results should similarly identify:

```text
attribute
group
group_size
reference_rate
current_rate
difference
status
```

This structure allows the same engine output to feed both the dashboard and the reporting pipeline.

---

## 18. Dashboard Requirements

The dashboard shall translate statistical results into information that can be understood without requiring the user to interpret raw formulas.

It should provide:

- overall model-health summary;
- feature-level drift status;
- KS values and p-values where applicable;
- PSI values;
- categorical drift results;
- fairness results by demographic attribute;
- distribution comparisons;
- clear warning/action states;
- enough context to identify the affected feature or group.

The dashboard should avoid presenting a single unexplained score as the complete definition of model health.

---

## 19. Reporting Requirements

The reporting pipeline shall generate a **Model Health Certificate** containing:

1. assessment metadata;
2. reference and comparison dataset information;
3. overall monitoring status;
4. feature-level drift findings;
5. fairness findings;
6. threshold interpretations;
7. important warnings or action-required findings;
8. summary and recommended investigation areas;
9. generation timestamp and report version.

The report is intended to provide a persistent record of the assessment for review, quality assurance, and audit purposes.

---

## 20. Error Handling and Validation

The system shall fail clearly when required information is unavailable.

Examples include:

- reference dataset does not exist;
- required column is missing;
- target contains invalid values;
- production batch does not match the expected schema;
- statistical test receives an unsupported feature type;
- required fairness attribute is absent;
- there is insufficient data to produce a meaningful result.

The system should distinguish **no evidence of drift** from **insufficient evidence to assess drift**. An inability to perform a valid test should not be silently classified as stable.

---

## 21. Security and Data Handling Considerations

The project should avoid storing unnecessary personally identifying information in monitoring artifacts.

Customer identifiers should not be used as model features or included in aggregated monitoring outputs unless required for a specific debugging workflow.

The system should prefer aggregate statistics over raw customer-level records in dashboards and reports.

Secrets, credentials, and environment-specific configuration shall not be committed to the repository.

---

## 22. Testing Strategy

Testing will occur at multiple levels.

### Unit tests

Individual preprocessing and statistical functions shall be tested with controlled inputs.

### Integration tests

The complete path from reference data through monitoring output shall be tested.

### Controlled drift tests

Synthetic or modified datasets shall be used to create known shifts. The engine should identify those shifts according to the configured methodology.

### Fairness tests

Controlled group-level outcome changes shall be used to verify that the fairness calculations respond as expected.

### Regression tests

Previously validated datasets and expected outputs shall be retained so that changes to the implementation do not silently alter established behaviour.

---

## 23. Implementation Plan

Development will proceed incrementally rather than implementing the entire system at once.

| Stage | Focus | Main Deliverable |
|---|---|---|
| 1 | Data and reference profiling | Clean data and reference profile |
| 2 | Engine core | Batch ingestion and monitoring result structure |
| 3 | Statistical refinement | KS, PSI and categorical drift logic |
| 4 | Observability | Streamlit dashboard |
| 5 | Reporting | PDF Model Health Certificate |
| 6 | Quality and deployment | Tests, Docker and final validation |

Each stage should be validated before dependent modules are built on top of it.

---

## 24. Acceptance Criteria

The initial GuardDog AI implementation will be considered functionally complete when:

- a valid reference dataset can be profiled reproducibly;
- a comparison batch can be processed without manual feature-by-feature intervention;
- numerical drift can be evaluated using the defined KS/PSI methodology;
- categorical drift can be evaluated using an appropriate categorical method;
- fairness results can be produced for the defined demographic attributes;
- monitoring results contain feature/group, metric, value, and status information;
- dashboard results correspond to engine results;
- the reporting pipeline produces a readable Model Health Certificate;
- preprocessing and core monitoring functions have automated tests;
- controlled drift tests demonstrate that known shifts can be detected;
- invalid inputs generate explicit errors;
- the project documentation matches the implemented behaviour.

---

## 25. Known Limitations

The following limitations are accepted for the initial version:

1. Distribution drift does not automatically mean model performance has degraded.
2. The KS test is sensitive to sample size.
3. PSI depends on binning decisions and threshold conventions.
4. Demographic Parity does not cover every definition of fairness.
5. Fairness interpretation depends on the meaning of the monitored outcome.
6. Without reliable production labels, direct performance degradation cannot be established solely from input drift.
7. Simulated production data can demonstrate monitoring behaviour but is not a substitute for real production evidence.
8. A statistical alert identifies a condition for investigation; it does not automatically identify its business cause.

These limitations should be visible in project documentation rather than hidden behind a simplified health score.

---

## 26. Future Extensions

Potential future work includes:

- additional drift metrics;
- concept-drift detection;
- model-performance monitoring when delayed labels become available;
- additional fairness metrics;
- multiple-testing correction strategies;
- automated alert delivery;
- model-version comparison;
- historical trend analysis;
- integration with external MLOps platforms;
- automated retraining recommendations;
- production data connectors;
- richer governance and audit controls.

These extensions are intentionally separated from the initial scope so that the first implementation remains testable and understandable.

---

## 27. Traceability Matrix

| Requirement | Planned Component | Validation |
|---|---|---|
| Reference profiling | Reference Profiler | Profile unit/integration tests |
| Missingness monitoring | Preprocessing + Profiler | Data validation tests |
| Numerical drift | Drift & Bias Engine | KS/PSI controlled tests |
| Categorical drift | Drift & Bias Engine | Categorical test cases |
| Fairness monitoring | Drift & Bias Engine | Controlled group tests |
| Stakeholder visualization | Streamlit Dashboard | UI/integration validation |
| Formal reporting | Reporting Pipeline | PDF generation test |
| Reproducibility | All core modules | Regression tests |
| Input validation | Preprocessing + Engine | Negative test cases |

---

## 28. Implementation Principles

The following principles will guide development:

### 28.1 Do not confuse statistical significance with business significance

A low p-value is evidence against a null hypothesis. It is not, by itself, evidence that the change is operationally important.

### 28.2 Do not hide missing data decisions

Every missing-value treatment should have a reason. Arbitrary imputation can alter the reference distribution and therefore alter what GuardDog later calls drift.

### 28.3 Do not introduce leakage

Fields containing information about the outcome after it occurred must not be used as predictive features merely because they improve apparent model performance.

### 28.4 Keep monitoring separate from presentation

The statistical engine should produce structured results. The dashboard and PDF report should consume those results rather than duplicate the statistical logic.

### 28.5 Make alerts explainable

A user should be able to answer:

- What changed?
- How much did it change?
- Which metric detected it?
- What threshold was crossed?
- Why was the result classified at that severity?
- What should be investigated next?

---

## 29. Final System Definition

GuardDog AI is defined as a **model-integrity and observability pipeline**, not as the prediction model itself.

Its central workflow is:

```text
Establish what normal looked like
              ↓
Measure what is happening now
              ↓
Compare the two statistically
              ↓
Check selected fairness characteristics
              ↓
Classify and explain the findings
              ↓
Present the results
              ↓
Preserve an auditable record
```

The central engineering question is therefore:

> **Has the environment in which the model operates changed enough that the model's health should be investigated?**

GuardDog AI provides the measurement and evidence needed to answer that question systematically. It does not assume that every change is harmful, nor does it claim that statistical drift alone proves model failure.

---

## 30. Document Status

**Status:** Pre-implementation specification completed.  
**Next development activity:** Validate the approved data-preprocessing pipeline, then implement the Reference Profiler against the cleaned reference dataset.

This document should be updated when a deliberate architectural or requirements decision changes. Implementation changes should not silently redefine the requirements.
