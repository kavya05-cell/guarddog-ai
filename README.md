# GuardDog AI

**Continuous Model Integrity and Observability Pipeline**

## Why Does GuardDog AI Exist?

Machine learning models are often treated as if their work is finished once they are trained and deployed.

In reality, deployment is only the beginning.

A model learns patterns from historical training data. After deployment, the world around that model can change. Customers can change, user behavior can change, geographic populations can change, and the distribution of the data entering the model can shift over time.

A model can therefore continue running successfully from a software perspective while becoming less reliable from a machine-learning perspective.

This creates a dangerous problem: **model degradation can be silent**.

A traditional monitoring system may tell an engineering team that the API is running, the server is healthy, and predictions are being generated. It does not automatically tell them that the data reaching the model has become substantially different from the data on which the model was developed.

GuardDog AI is designed to act as an additional validation and observability layer for this problem.

---

## The Core Problem

There are four closely related problems that GuardDog AI addresses.

### 1. Data Changes After Deployment

Suppose a model was trained when the average customer age was around 35 years old.

Later, the incoming population has an average age of 48.

Or suppose the training population was approximately:

```text
Delhi       30%
Mumbai      25%
Bangalore   20%
Other       25%
```

but the production population becomes substantially different.

The model is now receiving data that does not look like the data it originally learned from.

This is called **data drift**.

### 2. Statistical Change Does Not Always Mean Practical Risk

With enough production observations, even a very small distribution difference can become statistically significant.

If a monitoring system reacts to every statistically detectable difference, it can generate too many alerts. Engineers may start ignoring alerts altogether.

This is known as **alert fatigue**.

GuardDog therefore combines statistical significance with a measure of the practical magnitude of the change.

### 3. Fairness Can Change Over Time

A model may behave differently across demographic groups as the underlying population changes.

For example, the distribution of outcomes across gender, age, or region can shift between the reference data and later data.

Monitoring only overall drift can miss this type of issue.

GuardDog therefore includes a fairness-auditing component based on **Demographic Parity** across the project-defined attributes of age, gender, and region.

### 4. Raw Statistics Are Difficult to Interpret

A monitoring system can produce numbers such as:

```text
KS statistic = 0.21
p-value      = 0.003
PSI          = 0.31
```

Those values are useful to a data scientist, but they are not immediately meaningful to every stakeholder.

GuardDog therefore translates the statistical results into model-health information through a dashboard and formal reports.

---

## What Is Data Drift?

**Data drift is a change in the statistical distribution of data over time.**

The simplest way to understand it is:

> **The model was trained on one population, but it is now seeing a different population.**

For example:

```text
Training data
Average age = 35

Production data
Average age = 48
```

A change like this does not automatically prove that the model is failing. It tells us that the input environment has changed and that the model should be investigated.

Drift can be sudden, gradual, or incremental. GuardDog's initial implementation focuses on detecting distributional changes between a reference dataset and incoming production-like batches.

---

## What Is Concept Drift?

Data drift concerns changes in the input distribution.

**Concept drift** is different: it occurs when the relationship between the input variables and the outcome changes.

For example, customer behavior may change so that the same observable characteristics that previously predicted churn no longer have the same relationship with churn.

This distinction matters because detecting input drift does not by itself prove that the model's predictive relationship has changed.

GuardDog's initial drift layer focuses primarily on measurable distribution shifts and fairness signals. More advanced concept-drift and performance monitoring can be added as the system evolves.

---

## What Is ML Observability?

Traditional software monitoring asks questions such as:

- Is the application running?
- Is the server available?
- Is the API responding?
- Is latency acceptable?

Machine-learning systems require additional visibility.

ML observability asks questions such as:

- Has the incoming data changed?
- Are important feature distributions shifting?
- Are demographic distributions changing?
- Are fairness indicators changing?
- Is there evidence that the model's operating environment is becoming unstable?

GuardDog AI is designed as an **MLOps observability and validation pipeline** rather than simply a model-training script.

---

## The GuardDog AI Solution

GuardDog creates a statistical picture of the data used as the reference point and compares future production-like data against it.

The high-level idea is:

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
      +---+---+
      |       |
      v       v
    Drift   Fairness
      |       |
      +---+---+
          |
          v
   Health / Risk Results
       /           \
      v             v
 Dashboard       Report
```

The system is intended to provide a **pre-emptive validation layer and local quality gate** so that model behavior and its data environment can be examined before problems are allowed to remain unnoticed.

---

## How GuardDog Works

### Step 1 — Establish a Reference Baseline

The system first examines a trusted reference dataset.

The **Reference Profiler** records statistical characteristics such as:

- feature distributions
- numerical summaries
- categorical distributions
- missingness information
- demographic ratios

This becomes the baseline for later comparisons.

In simple terms:

> **The baseline describes what normal looked like when the reference data was collected.**

---

### Step 2 — Receive Production-like Data

The system then evaluates batches representing data that the deployed model could encounter.

For this project, production behavior can be simulated so that controlled changes can be introduced and tested.

This makes it possible to test whether GuardDog correctly identifies known distribution shifts.

---

### Step 3 — Detect Drift

The Drift & Bias Engine compares the production-like data with the reference baseline.

GuardDog initially uses two complementary drift measures:

1. **Kolmogorov–Smirnov (KS) Test**
2. **Population Stability Index (PSI)**

The two methods answer related but different questions.

---

## Method 1 — Kolmogorov–Smirnov Test

The **KS test** is a non-parametric statistical test used to compare distributions.

In GuardDog, it is used primarily for numerical feature distributions.

The basic question is:

> **Is the observed difference between the reference and production distributions statistically significant?**

GuardDog uses the following initial thresholds:

| p-value | Interpretation |
|---|---|
| `p < 0.05` | Standard warning |
| `p < 0.01` | Strict alert |

### Why is KS not enough?

A large sample can make the KS test extremely sensitive. With enough observations, even a very small change can produce a very small p-value.

Therefore:

> **Statistically significant does not automatically mean practically important.**

This is why GuardDog pairs KS with PSI.

---

## Method 2 — Population Stability Index

The **Population Stability Index (PSI)** measures the magnitude of a distribution shift using predefined bins.

It provides a practical view of how much the population has moved away from the reference distribution.

GuardDog uses the following traffic-light interpretation:

| PSI | Status | Meaning |
|---:|---|---|
| `< 0.10` | Stable | Very little change |
| `0.10–0.25` | Warning | Minor shift; monitor more closely |
| `> 0.25` | Action Required | Major shift; investigate or consider retraining |

### Why combine KS and PSI?

Consider two results:

```text
KS: significant
PSI: 0.03
```

This suggests a statistically detectable difference with a small practical shift.

Now consider:

```text
KS: significant
PSI: 0.31
```

This indicates both statistical evidence of a difference and a large measured distribution shift.

The combination helps GuardDog distinguish potentially meaningful changes from changes that may be statistically detectable but operationally minor.

---

## PSI Numerical Stability

PSI calculations compare frequencies across bins. A bin can have zero observations, which can create numerical problems involving division or logarithms.

GuardDog uses a small epsilon value:

```text
1e-8
```

to mitigate zero-frequency numerical issues and keep the calculation numerically stable.

---

## Fairness Auditing

Drift is not the only concern.

An ML system can also create or amplify unequal outcomes across demographic groups.

GuardDog therefore includes a fairness-auditing component.

The initial fairness methodology is **Demographic Parity**.

The project-defined demographic attributes are:

- Age
- Gender
- Region

The objective is to monitor whether outcome distributions differ across demographic groups and whether those patterns change relative to the reference context.

Fairness metrics should be interpreted carefully: a detected difference is a signal for investigation, not by itself proof of intentional discrimination or causal bias.

---

## Why the System Needs Both Drift and Fairness Monitoring

These checks answer different questions.

| Check | Main Question |
|---|---|
| Data drift | Has the incoming population changed? |
| KS test | Is a distributional difference statistically detectable? |
| PSI | How large is the measured distribution shift? |
| Fairness audit | Are outcome distributions changing across demographic groups? |

Together, these measurements provide a broader picture of model integrity than a single accuracy score.

---

## GuardDog AI Architecture

The project is divided into four major modules.

### 1. Reference Profiler

Creates the statistical baseline from the reference dataset.

### 2. Drift & Bias Engine

Compares incoming production-like batches against the baseline and performs drift and fairness analysis.

### 3. Interactive Observability Dashboard

Uses Streamlit to present drift, distribution, fairness, and model-health information in a form that is easier for stakeholders to understand.

### 4. Reporting Pipeline

Converts engine results into **Model Health Certificates** in PDF form, creating an auditable record of monitoring results.

The resulting flow is:

```text
Reference Data
      |
      v
Reference Profiler
      |
      v
Baseline
      |
      v
Drift & Bias Engine
      |
      +----------------+
      |                |
      v                v
Dashboard         Reporting
                      |
                      v
              Model Health
                Certificate
```

---

## Primary Dataset

The project's primary end-to-end dataset is the **IBM Telco Customer Churn dataset**.

It is suitable for the initial system because it provides a mixture of numerical and categorical information, a target variable, and demographic/context attributes relevant to the project's monitoring and fairness objectives.

Additional datasets and controlled synthetic data are planned for focused validation, including fairness benchmarking, credit-risk/PSI experiments, and controlled drift experiments.

The project therefore does not assume that one dataset is sufficient for every research question.

---

## Why Use Simulated Production Data?

A real production system changes over time, but a research project needs controlled experiments.

With simulated production data, we can deliberately introduce changes such as:

```text
Reference
Age distribution = normal

Simulated production
Age distribution = shifted
```

We can then test whether GuardDog detects the change.

This provides a controlled way to evaluate the monitoring pipeline because the expected change is known in advance.

---

## Example of GuardDog in Action

Imagine a churn prediction model was developed using a reference population.

Months later, the incoming customer population changes.

GuardDog evaluates the new batch and produces results such as:

```text
Age
KS: significant
PSI: 0.18
Status: WARNING

Internet Type
KS: significant
PSI: 0.07
Status: STABLE

Region
Distribution shift detected
Status: WARNING

Fairness
Demographic parity deviation detected
Status: INVESTIGATE
```

Instead of simply saying **"the model is broken,"** GuardDog provides evidence that tells the engineering or data-science team **where the environment changed and what should be investigated**.

---

## Important Limitations

GuardDog's initial implementation is intentionally focused.

### Drift is not the same as model failure

A feature can drift without causing prediction quality to decrease. Drift is an important warning signal, not definitive proof of performance degradation.

### KS is mainly univariate

The initial KS implementation evaluates features individually. It may not capture complex multivariate interactions between features.

### PSI depends on binning

Different binning strategies can produce different PSI values, so binning choices must be documented and evaluated carefully.

### Statistical significance depends on sample size

Large samples can make small differences statistically significant. This is one reason GuardDog uses both KS and PSI.

### Fairness metrics require context

Demographic differences alone do not establish the cause of a disparity. Fairness results should be treated as monitoring signals that require investigation.

These limitations are part of the reason the system is designed as an extensible observability pipeline rather than a single drift score.

---

## Planned Extensions

The research work identifies several possible future extensions, including:

- multivariate drift detection
- additional fairness metrics
- explainability
- causal drift analysis
- handling delayed labels
- continual learning
- synthetic drift simulations
- stronger governance and compliance artifacts

These are extensions to the initial GuardDog system rather than prerequisites for the first working implementation.

---

## Repository Structure

```text
guarddog-ai/
├── README.md
├── docs/
├── src/
│   └── preprocessing/
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── reports/
├── requirements.txt
└── .gitignore
```

---

## Current Development Stage

The project is being implemented incrementally.

```text
Dataset Investigation
        ↓
Data Preprocessing
        ↓
Reference Profiler
        ↓
Drift & Bias Engine
        ↓
Dashboard
        ↓
Reporting Pipeline
        ↓
Testing & Showcase
```

The current implementation work is focused on **data preprocessing and preparation for reference profiling**.

---

## Project Objective

GuardDog AI aims to move ML monitoring away from a simple **"the model is running"** mindset toward a more meaningful question:

> **Is the model still operating in an environment that resembles the one it was developed for, and are there measurable signals that require investigation?**

By combining baseline profiling, statistical drift detection, fairness auditing, visualization, and auditable reporting, GuardDog AI provides a structured foundation for continuous model integrity monitoring.

---

## References

This project is based on the supplied GuardDog AI technical specification, project report, and research/deep-research report. The repository implementation follows the methodologies and scope defined in those project sources.
