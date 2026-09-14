# GuardDog AI

## Continuous Model Integrity and Observability Pipeline

Machine learning does not stop being a risk once a model has been trained and deployed.

A model learns patterns from historical data. After deployment, however, the real world keeps changing. Customer behaviour changes, populations change, products change, economic conditions change, and the way data is collected can change. As a result, the data reaching a model in production may gradually become different from the data on which the model was trained.

The model may continue to return predictions normally. Nothing may crash. The API may still respond with a prediction for every request. Yet the model can become less reliable because the environment it is operating in has changed.

This is one of the central problems GuardDog AI is designed to address.

---

## 1. The Problem: Models Can Degrade Silently

Consider a customer-churn model trained using historical customer information.

At training time, the model may learn from a population where:

- customer demographics follow a particular distribution;
- contract types occur at particular frequencies;
- internet-service usage follows a particular pattern; and
- customer behaviour is relatively stable.

Months later, the business may acquire a different customer population. New plans may be introduced. Customer behaviour may change. The distribution of important features can therefore shift.

The model still produces predictions, but those predictions are now being made in an environment that may no longer resemble the environment represented by its reference data.

Without monitoring, this degradation can remain invisible.

### Why this is difficult

Traditional machine-learning evaluation is usually performed before deployment using a fixed test set. Metrics such as accuracy, precision, recall, or F1 score tell us how the model performed on that historical evaluation data.

They do not, by themselves, continuously answer:

> **"Has the data arriving today changed enough that we should be concerned about the model?"**

That is an observability problem.

---

## 2. What Is Data Drift?

**Data drift** means that the statistical distribution of data has changed over time.

In simple terms:

> **The data the model sees today is different from the data it learned from or was originally validated on.**

For example, imagine that a model was trained when most customers were between 25 and 45 years old. If the production population later contains a much larger proportion of customers over 60, the distribution of the `Age` feature has changed.

The same idea applies to numerical and categorical variables.

### Reference data vs production data

GuardDog AI uses two concepts:

| Data | Meaning |
|---|---|
| **Reference data** | The trusted baseline used to represent the expected data distribution. |
| **Production data** | New or simulated incoming data that is compared against the reference baseline. |

The system asks whether the two distributions are sufficiently different to warrant attention.

---

## 3. Why Detecting Drift Is Not Enough

A statistical test can tell us that two distributions are different. But a difference is not automatically a business problem.

For example, with a sufficiently large dataset, a very small change can become statistically significant even though the practical impact is negligible.

This creates two different questions:

1. **Is there evidence that the distributions are different?**
2. **Is the observed change large enough to matter?**

GuardDog AI therefore uses complementary drift measures rather than relying on a single number.

---

## 4. GuardDog AI: The Solution

GuardDog AI is a **continuous model integrity and observability pipeline**.

Its purpose is to provide a structured way to compare a trusted reference baseline with new production-like data, identify meaningful distribution changes, audit demographic fairness, and communicate the results clearly.

The high-level workflow is:

```text
Reference / Training Data
          |
          v
   Reference Profiler
          |
          v
    Statistical Baseline
          |
          v
 Production-like Data
          |
          v
 Drift & Bias Engine
          |
     +----+----+
     |         |
     v         v
   Drift    Fairness
 Detection   Audit
     |         |
     +----+----+
          |
          v
 Observability Dashboard
          |
          v
 Model Health Certificate
```

The objective is not simply to say **"drift detected."**

The objective is to provide evidence about **what changed, how significant the change is, whether fairness indicators differ across groups, and what should receive attention.**

---

## 5. How GuardDog Detects Drift

GuardDog AI uses two complementary statistical methods for the initial drift engine:

- **Kolmogorov–Smirnov (KS) Test**
- **Population Stability Index (PSI)**

Using both methods helps separate statistical evidence of change from a measure of the magnitude of the distribution shift.

### 5.1 Kolmogorov–Smirnov Test

The **KS test** compares the distributions of two numerical samples.

Conceptually, it compares their cumulative distributions and measures the largest difference between them.

The result includes a **p-value**, which is used by GuardDog to classify the statistical evidence of distribution change.

| KS p-value | GuardDog classification |
|---:|---|
| `p >= 0.05` | No standard warning from the configured KS threshold |
| `p < 0.05` | Standard Warning |
| `p < 0.01` | Strict Alert |

A low p-value indicates evidence against the assumption that the reference and production samples come from the same distribution.

The KS test is primarily a statistical significance test. It should therefore be interpreted together with the magnitude-oriented PSI measure.

### 5.2 Population Stability Index

**Population Stability Index (PSI)** measures how the distribution of a variable has shifted between two populations using defined bins or categories.

In simple terms, PSI asks:

> **"How much has the population moved from the reference distribution to the current distribution?"**

GuardDog uses the following severity thresholds:

| PSI | Classification |
|---:|---|
| `< 0.10` | Stable |
| `0.10–0.25` | Warning |
| `> 0.25` | Action Required |

PSI thresholds are practical heuristics rather than universal laws, so the value must be interpreted in context.

### 5.3 Why GuardDog Uses KS + PSI

The two metrics answer related but different questions.

```text
KS  -> Is there statistical evidence of a distribution difference?
PSI -> How large is the observed distribution shift according to the binning scheme?
```

Together they provide a more useful monitoring signal than treating either metric as a complete answer by itself.

### 5.4 Zero-Frequency Protection

PSI calculations involve logarithmic terms. A bin with zero observed or expected frequency can create numerical problems.

GuardDog therefore uses a small epsilon value:

```text
ε = 1 × 10⁻⁸
```

This provides numerical protection when a frequency is zero.

---

## 6. Fairness: A Model Can Be Stable and Still Be Unfair

Model monitoring should not focus only on whether the overall data distribution has changed.

A model can appear statistically stable at the overall population level while behaving differently across demographic groups.

**Algorithmic fairness** concerns whether model behaviour or outcomes differ across relevant groups in ways that require investigation.

GuardDog AI includes **Demographic Parity auditing** across:

- Age
- Gender
- Region

The purpose is to make demographic differences visible rather than hiding them inside an overall model-health score.

Fairness metrics should be interpreted carefully because different fairness definitions answer different questions and may have important limitations. GuardDog's initial specification uses Demographic Parity as its defined fairness measure.

---

## 7. What GuardDog Actually Monitors

GuardDog combines several monitoring dimensions:

| Monitoring area | Question being asked |
|---|---|
| **Data drift** | Has the incoming data distribution changed? |
| **Statistical significance** | Is there evidence that the observed distribution difference is unlikely to be random variation? |
| **Shift magnitude** | Is the distribution change practically meaningful according to the configured PSI thresholds? |
| **Fairness** | Are demographic outcome rates different across monitored groups? |
| **Model health** | What is the overall evidence about the current state of the monitored system? |
| **Reporting** | Can the findings be communicated and audited clearly? |

---

## 8. GuardDog AI Architecture

The project is divided into four major modules.

### 8.1 Reference Profiler

The Reference Profiler creates the statistical baseline from trusted reference data.

It records the information required for later comparisons, including feature distributions, missingness-related information, and demographic characteristics needed by downstream monitoring.

The key idea is simple:

> **Before we can detect change, we need to define what "normal" looks like.**

### 8.2 Drift & Bias Engine

The Drift & Bias Engine compares new production-like data against the reference baseline.

It is responsible for:

- KS testing;
- PSI calculation;
- severity classification;
- numerical safeguards;
- fairness analysis; and
- structured monitoring results.

### 8.3 Interactive Observability Dashboard

A Streamlit dashboard will turn the statistical results into an interactive monitoring interface.

The dashboard is intended to make it possible to quickly identify:

- which features changed;
- how severe the detected shift is;
- which demographic groups require attention; and
- the current model-health picture.

### 8.4 Reporting Pipeline

GuardDog will generate a PDF **Model Health Certificate** containing the monitoring findings.

This creates an auditable output instead of leaving monitoring results trapped inside a notebook or application screen.

---

## 9. Dataset Strategy

The primary end-to-end dataset for the project is the **IBM Telco Customer Churn** dataset.

It is used because it provides a practical tabular setting containing numerical and categorical customer information, a churn target, and demographic/location attributes that support the project's monitoring and fairness objectives.

GuardDog is not designed around the assumption that one dataset can demonstrate every possible monitoring problem.

Additional datasets and synthetic data can be used for focused experiments, such as fairness benchmarking, credit-risk scenarios, and controlled drift where the expected change is known in advance.

This allows the system to be evaluated from multiple perspectives rather than overfitting the demonstration to one dataset.

---

## 10. Why a Reference Baseline Matters

Suppose we receive a new batch of 1,000 production records.

Looking at that batch alone does not tell us whether the data is normal.

We need something to compare it against.

GuardDog therefore follows this principle:

```text
Trusted historical data
        |
        v
Define expected behaviour
        |
        v
Reference baseline
        |
        v
Compare future batches
        |
        v
Detect meaningful change
```

The quality of the monitoring system therefore depends partly on the quality and representativeness of the reference baseline.

---

## 11. From Raw Data to Monitoring Results

The implementation begins with a validated and cleaned dataset.

The preprocessing stage removes identifiers and post-outcome leakage, preserves important monitoring attributes, and handles missing values according to their meaning rather than blindly replacing them.

The resulting flow is:

```text
Raw Dataset
    |
    v
Data Validation
    |
    v
Preprocessing
    |
    v
Clean Reference Dataset
    |
    v
Reference Profile
    |
    v
Production-like Batch
    |
    v
Drift + Fairness Analysis
    |
    v
Dashboard + Report
```

This separation is important because the same reference definition must be used consistently when future data is evaluated.

---

## 12. Severity Is Not the Same as a Model Failure

A GuardDog warning does **not** automatically mean that a model is broken.

For example:

- a feature may drift because customer behaviour genuinely changed;
- a statistically significant change may be too small to matter operationally;
- a large distribution shift may be expected after a business change; or
- a fairness signal may require investigation rather than proving discrimination by itself.

GuardDog is therefore an **observability and decision-support system**, not an automatic replacement for model validation, business investigation, or human governance.

The monitoring result should trigger investigation and appropriate action based on context.

---

## 13. Project Workflow

The intended implementation sequence is:

1. **Dataset acquisition and validation**
2. **Data preprocessing**
3. **Reference profiling**
4. **Drift detection engine**
5. **Fairness analysis**
6. **Controlled drift simulation**
7. **Interactive Streamlit dashboard**
8. **PDF Model Health Certificates**
9. **Testing and validation**
10. **Documentation and final integration**

---

## 14. Repository Structure

```text
guarddog-ai/
├── README.md
├── docs/
│   ├── project-specification.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── pre-implementation-specification.md
├── src/
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   └── pipeline.py
│   ├── profiler/
│   ├── drift/
│   ├── fairness/
│   ├── dashboard/
│   └── reporting/
├── tests/
├── data/
├── notebooks/
├── reports/
├── requirements.txt
└── .gitignore
```

---

## 15. Current Implementation Status

### Completed

- Project repository initialized
- Project requirements captured
- Dataset investigation completed
- IBM-style Telco customer data selected as the primary dataset
- Customer-level source tables validated
- Customer records merged using one-to-one validation
- Preprocessing design established

### In Progress

- Preprocessing implementation
- Clean reference dataset generation

### Upcoming

- Reference Profiler
- Drift & Bias Engine
- Controlled drift experiments
- Fairness auditing
- Streamlit observability dashboard
- PDF Model Health Certificate
- Automated testing and final integration

---

## 16. Initial Acceptance Criteria

The completed system should be able to demonstrate that:

- a reference baseline can be generated from the selected dataset;
- production-like data can be compared with that baseline;
- KS and PSI results are calculated according to the configured thresholds;
- zero-frequency bins do not cause PSI calculation failures;
- Demographic Parity is audited for Age, Gender, and Region;
- detected findings are presented through an interactive dashboard; and
- a PDF Model Health Certificate can be generated from the monitoring results.

---

## 17. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation language |
| pandas | Data loading and transformation |
| NumPy | Numerical computation |
| SciPy | Statistical testing |
| scikit-learn | Machine-learning utilities and experiments |
| Streamlit | Interactive observability dashboard |
| Plotly | Interactive visualizations |
| ReportLab | PDF reporting |
| pytest | Automated testing |

---

## 18. Project Philosophy

GuardDog AI follows a simple principle:

> **A model should not be considered healthy merely because it is still running.**

A healthy production ML system should be observable.

We need to know whether the data has changed, whether those changes are statistically and practically meaningful, whether monitored demographic groups show concerning differences, and whether the evidence can be communicated clearly enough for humans to investigate and act.

GuardDog AI is being built to make that monitoring process continuous, explainable, and auditable.

---

## Reference

This README is the user-facing overview of the GuardDog AI project. The detailed requirements are maintained in `docs/project-specification.md` and the associated project documentation.
