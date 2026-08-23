# GuardDog AI — Dataset Strategy

## Primary dataset

**IBM Telco Customer Churn** is the primary end-to-end demonstration dataset.

It will be used for:
- ML model training;
- reference profiling;
- production-like drift simulation;
- KS, PSI, and Chi-Squared monitoring;
- demographic fairness monitoring; and
- dashboard/report demonstrations.

## Secondary benchmarks

- **UCI Adult** — fairness validation and cross-dataset robustness.
- **South German Credit** — credit-risk-domain validation.

## Controlled validation

Synthetic data will be generated from the primary reference data for known scenarios:

- no drift;
- small and major numerical drift;
- categorical drift;
- gradual and sudden drift; and
- controlled fairness deviations.

## Raw-data policy

Raw datasets must not be committed to Git. Store them locally under `data/raw/`. Generated/processed datasets belong under `data/processed/`. Both are gitignored.

## Logical schema

The primary dataset will be mapped to GuardDog's logical schema:

- numerical features;
- categorical features;
- target (`churn`);
- age;
- gender; and
- region.

If `region` is engineered from source location fields, the transformation must be explicitly documented in the dataset adapter and profiling metadata.

## Dataset-agnostic design

Statistical engines must not contain Telco-, Adult-, or German-Credit-specific logic. Dataset-specific loading, cleaning, feature mapping, and target definitions belong in adapters/configuration.
