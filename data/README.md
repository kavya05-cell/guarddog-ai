# GuardDog AI Dataset

## Selected benchmark

**UCI Adult Income (Census Income)** is the initial GuardDog benchmark dataset.

### Why this dataset

It satisfies the core GuardDog requirements with a real tabular classification problem containing:

- numerical features such as age, capital gain/loss, hours per week, and education number;
- categorical features such as workclass, education, occupation, marital status, relationship, race, sex, and native country;
- a binary target indicating whether annual income is above the specified threshold; and
- demographic attributes suitable for fairness auditing.

### Region mapping

The raw Adult dataset does not contain a column literally named `region`. It contains `native-country`. GuardDog will create a derived `region` feature by mapping native countries into broad geographic regions.

This transformation is intentional and must remain documented: `region` is an engineered attribute, not an original Adult dataset field.

### GuardDog schema

The ingestion layer should expose the following logical groups:

- **Numerical:** age, fnlwgt, education_num, capital_gain, capital_loss, hours_per_week
- **Categorical:** workclass, education, marital_status, occupation, relationship, race, sex, native_country, region
- **Target:** income
- **Fairness attributes:** age, sex, region

### Experimental use

The dataset is used as a benchmark for the GuardDog monitoring pipeline, not as a claim that the resulting income classifier is production-ready.

Production-like batches will be generated from the reference data through controlled transformations such as feature-distribution shifts and subgroup-representation changes. Each scenario should have a known ground truth so detector behavior can be evaluated.

### Data policy

Do not commit the raw dataset to this repository. Store downloaded/raw files locally under `data/raw/` and keep generated/processed files out of version control unless explicitly required.
