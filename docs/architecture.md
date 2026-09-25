# GuardDog AI — Initial Architecture

## High-Level Flow

```text
Reference / Training Data
        │
        ▼
┌──────────────────────┐
│ Reference Profiler   │
└──────────┬───────────┘
           │ baseline statistics
           ▼
┌──────────────────────┐
│ Drift & Bias Engine  │◄──── Simulated Production Data
└──────────┬───────────┘
           │
           ├── KS Test
           ├── PSI
           └── Demographic Parity
           │
           ▼
┌──────────────────────┐
│ Observability Layer  │
│     Streamlit        │
└──────────┬───────────┘
           │
           ├──────────────► Interactive telemetry
           │
           ▼
┌──────────────────────┐
│ Reporting Pipeline   │
│      ReportLab       │
└──────────┬───────────┘
           │
           ▼
    Model Health Certificate
```

## Components

### Reference Profiler

Responsible for establishing the reference state from the selected training dataset.

### Drift & Bias Engine

Responsible for statistical comparison between the reference state and production-like data, plus fairness auditing.

### Observability Dashboard

Responsible for presenting analysis results and model-health telemetry interactively through Streamlit.

### Reporting Pipeline

Responsible for producing a formal PDF Model Health Certificate from the monitoring results.

## Design Principle

The components should remain modular so that profiling, statistical detection, fairness auditing, visualization, and reporting can be tested independently and later integrated into a continuous workflow.

## Architecture Status

This is the **initial architecture baseline**. Implementation details may be refined after dataset selection and during the individual development sprints, but changes should be documented.