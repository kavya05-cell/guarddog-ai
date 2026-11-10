# GuardDog AI 🛡️
### Real-Time Data Drift Monitoring, Network Anomaly Detection & Model Observability

GuardDog AI is a monitoring and observability system designed to identify changes in incoming data distributions and detect unusual network traffic patterns.

It combines statistical drift detection, machine learning-based anomaly detection, real-time data streaming, and interactive visualization in a unified monitoring platform.

The system contains two monitoring pipelines:

- **Data Drift Monitoring:** Monitors changes in structured datasets using statistical techniques.
- **Network Monitoring:** Processes live network traffic, identifies anomalous flows, and monitors changes in network traffic distributions.

---

## 1. The Problem

Machine learning models are generally trained and evaluated using historical datasets.

However, real-world data is not static.

Customer behaviour changes, application usage evolves, and network traffic patterns fluctuate over time.

A model that performs adequately during development may encounter significantly different input data after deployment.

Traditional model evaluation metrics such as accuracy, precision, recall, and F1-score describe performance on evaluated datasets. They do not continuously identify changes in incoming data distributions.

GuardDog AI addresses this monitoring problem by comparing incoming data against a reference baseline and identifying unusual distribution changes.

For network traffic, it additionally applies unsupervised anomaly detection to identify flows that differ from learned traffic patterns.

---

## 2. System Overview

GuardDog AI consists of two independent but integrated monitoring pipelines.

### Pipeline A: Data Drift Monitoring

This pipeline uses the IBM Telco Customer Churn dataset to demonstrate statistical monitoring of structured data.

It performs:

- Dataset reconstruction and preprocessing.
- Reference profiling.
- Kafka-based data ingestion.
- Batch-based drift detection.
- Numerical and categorical distribution analysis.
- Outcome disparity auditing.
- Interactive dashboard visualization.

### Pipeline B: Real-Time Network Monitoring

This pipeline captures live network traffic and analyzes network flows.

It performs:

- Network packet capture using Scapy.
- Network flow aggregation.
- Kafka-based streaming.
- Isolation Forest anomaly scoring.
- Statistical drift detection on network features.
- Network anomaly alert generation.
- Live traffic visualization.

The two pipelines share the monitoring platform but maintain separate reference datasets, processing logic, and output reports.

---

## 3. Architecture

### 3.1 Overall Architecture

```text
                    GUARDDOG AI
                         |
             +-----------+-----------+
             |                       |
             v                       v
       DATA DRIFT              NETWORK MONITORING
       MONITORING                    |
             |                       v
             v                 SCAPY CAPTURE
       TELCO DATA                     |
             |                       v
             v                 FLOW AGGREGATION
       PREPROCESSING                  |
             |                       v
             v                 KAFKA STREAMING
       REFERENCE PROFILE               |
             |                       v
             v                 KAFKA CONSUMER
       KAFKA STREAMING                 |
             |                 +-----+------+
             v                 |            |
       KAFKA CONSUMER           v            v
             |             ISOLATION     DRIFT
             v             FOREST        MONITOR
       DRIFT DETECTOR           |            |
             |                 v            v
       KS / PSI / CHI-SQUARE  ANOMALY    KS / PSI /
             |               SCORING     CHI-SQUARE
             |                 |            |
             v                 v            v
       DRIFT REPORTS       ALERT LOGS    DRIFT REPORTS
             |                 |            |
             +-----------------+------------+
                               |
                               v
                      STREAMLIT DASHBOARD
```

### 3.2 Data Drift Monitoring Architecture

```text
Telco Source Tables
        |
        v
Dataset Reconstruction
        |
        v
Data Preprocessing
        |
        v
Clean Reference Dataset
        |
        v
Reference Profiler
        |
        v
Reference Baseline
        |
        v
Kafka Producer
        |
        v
Kafka Topic
        |
        v
Kafka Consumer
        |
        v
Incoming Data Batches
        |
        v
Drift Detector
   /     |      \
  KS    PSI   Chi-Square
   \     |      /
        |
        v
Drift Report
        |
        v
Dashboard
```

### 3.3 Network Monitoring Architecture

```text
Live Network Traffic
        |
        v
Scapy Packet Capture
        |
        v
Network Flow Aggregation
        |
        v
Kafka Producer
        |
        v
Kafka Topic
        |
        v
Kafka Consumer
        |
        +-------------------+
        |                   |
        v                   v
 Isolation Forest       Drift Monitor
        |                   |
        v                   v
 Anomaly Scoring       KS / PSI / Chi-Square
        |                   |
        v                   v
 Anomaly Alerts        Drift Reports
        |                   |
        +---------+---------+
                  |
                  v
           Streamlit Dashboard
```

---

## 4. Drift Detection Methods

GuardDog AI uses three statistical methods to monitor distribution changes.

### 4.1 Kolmogorov-Smirnov Test (KS)

The KS test compares two numerical distributions.

It measures the maximum difference between their empirical cumulative distribution functions.

It produces:

- KS statistic
- p-value
- Drift status

Configured thresholds:

| p-value | Status |
|---|---|
| p ≥ 0.05 | Stable |
| 0.01 ≤ p < 0.05 | Warning |
| p < 0.01 | Alert |

### 4.2 Population Stability Index (PSI)

PSI measures the magnitude of distribution changes by comparing the proportions of observations across reference-defined bins.

Configured thresholds:

| PSI | Status |
|---|---|
| < 0.10 | Stable |
| 0.10–0.25 | Warning |
| > 0.25 | Alert |

A small epsilon is used to prevent numerical errors when a bin has zero frequency.

### 4.3 Chi-Square Test

The Chi-Square test is used for categorical features.

It compares categorical frequency distributions between reference and incoming data.

It produces:

- Chi-square statistic
- p-value
- Drift status

The same significance thresholds used by the KS test are applied.

### Why use all three?

| Method | Feature type | Purpose |
|---|---|---|
| KS | Numerical | Statistical evidence of distribution differences |
| PSI | Numerical | Magnitude of distribution movement |
| Chi-Square | Categorical | Statistical evidence of categorical distribution differences |

Combining these methods provides complementary perspectives on distribution changes.

---

## 5. Network Anomaly Detection

GuardDog AI uses an Isolation Forest model to identify unusual network flows.

### 5.1 Packet Capture

Scapy captures network packets from the selected network interface.

The current implementation supports:

- TCP
- UDP
- ICMP
- IPv4 and IPv6 traffic

### 5.2 Network Flow Aggregation

Packets are grouped into network flows using flow identifiers.

The flow aggregator extracts features including:

- Flow duration
- Total packets
- Total bytes
- Packets per second
- Bytes per second
- Forward packets
- Backward packets
- Forward bytes
- Backward bytes

### 5.3 Isolation Forest

Isolation Forest is an unsupervised anomaly detection algorithm.

It identifies observations that are relatively easy to isolate from the rest of the dataset.

GuardDog AI uses the trained Isolation Forest model to assign predictions:

| Prediction | Meaning |
|---|---|
| Normal | Flow is not classified as anomalous |
| Anomaly | Flow is classified as unusual relative to learned patterns |

The model also produces an anomaly score using its decision function.

A negative decision score indicates an anomaly under the current prediction configuration.

**Important:** An anomalous flow is not automatically a confirmed cyberattack. Unusual but legitimate network activity can also receive anomaly predictions.

---

## 6. Network Drift Monitoring

In addition to detecting individual anomalous flows, GuardDog AI monitors changes in network traffic distributions.

A separate network reference dataset is generated from historical network flows.

Incoming network flows are accumulated into batches of 100.

Each batch is compared against the reference dataset using:

- KS test
- PSI
- Chi-Square test

The system generates a network drift report containing:

- Batch number
- Timestamp
- Reference dataset size
- Current batch size
- Numerical feature results
- Categorical feature results
- Overall drift status

Network drift and anomaly detection serve different purposes:

| Anomaly Detection | Drift Detection |
|---|---|
| Examines individual network flows | Examines distributions across batches |
| Uses Isolation Forest | Uses statistical tests |
| Identifies unusual observations | Identifies changes in traffic patterns |
| Produces anomaly alerts | Produces drift reports |

---

## 7. Reference Baselines

GuardDog AI maintains separate reference datasets.

### Telco Reference

Generated from the cleaned Telco dataset.

Used for monitoring customer-level numerical and categorical features.

### Network Reference

Generated from historical network flow records.

Used for monitoring network traffic features.

The network reference is stored separately to prevent changes to the original Telco monitoring baseline.

---

## 8. Dashboard

The Streamlit dashboard provides a unified interface for both monitoring pipelines.

### Model Monitoring

Displays:

- Overall drift status.
- Records processed.
- Batches processed.
- Stable and alert counts.
- Drift status over time.
- Numerical KS and PSI results.
- Categorical Chi-Square results.
- Batch-level analysis.
- Telco outcome disparity audit.

### Network Monitoring

Displays:

- Total network flows.
- Normal and anomalous flows.
- Anomaly rate.
- Total packets and traffic volume.
- Protocol distribution.
- Top source IP addresses.
- Top destination ports.
- Numerical feature drift.
- PSI feature comparison chart.
- KS test results.
- Chi-Square results.
- Historical network drift.
- Recent network flows.
- Anomaly alerts.

The dashboard refreshes periodically and reads monitoring outputs generated by the streaming consumers.

---

## 9. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Pandas | Data processing |
| NumPy | Numerical operations |
| SciPy | Statistical testing |
| Scikit-learn | Isolation Forest |
| Scapy | Network packet capture |
| Apache Kafka | Real-time streaming |
| Docker | Kafka container execution |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Joblib | Model serialization |
| Pytest | Automated testing |

---

## 10. Repository Structure

```text
guarddog-ai/
│
├── data/
│   ├── raw/
│   │   └── telco/
│   │
│   └── processed/
│
├── models/
│   └── network/
│       └── isolation_forest_baseline.joblib
│
├── src/
│   ├── data/
│   │   └── merge_telco.py
│   │
│   ├── preprocessing/
│   │   ├── cleaner.py
│   │   └── pipeline.py
│   │
│   ├── profiler/
│   │   └── profiler.py
│   │
│   ├── drift/
│   │   ├── detector.py
│   │   ├── report.py
│   │   └── simulator.py
│   │
│   ├── fairness/
│   │   └── audit.py
│   │
│   ├── streaming/
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   │
│   │   └── network/
│   │       ├── build_network_reference.py
│   │       ├── flow_aggregator.py
│   │       ├── network_anomaly_detector.py
│   │       ├── network_consumer.py
│   │       ├── network_drift.py
│   │       ├── network_producer.py
│   │       ├── packet_capture.py
│   │       └── train_network_baseline.py
│   │
│   └── dashboard/
│       ├── app.py
│       └── network_app.py
│
├── tests/
│
├── scripts/
│
├── docs/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 11. Installation and Setup

### Prerequisites

- Python 3.11
- Docker Desktop
- Git
- Windows or Linux
- A compatible network interface for packet capture

### Clone the repository

```bash
git clone https://github.com/kavya05-cell/guarddog-ai.git
cd guarddog-ai
```

### Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

The project also requires a configured Kafka broker and the network Isolation Forest model.

---

## 12. Running Network Monitoring

The following commands reflect the current Windows development setup.

### Step 1: Start Kafka

```powershell
docker start guarddog-kafka
```

### Step 2: Build the network reference

This command uses previously collected network flow records.

```powershell
python -m src.streaming.network.build_network_reference
```

### Step 3: Start the network consumer

```powershell
python -m src.streaming.network.network_consumer
```

### Step 4: Start the network producer

Open another terminal:

```powershell
python -m src.streaming.network.network_producer --interface "Wi-Fi"
```

Replace `Wi-Fi` with the appropriate network interface name if necessary.

### Step 5: Start the dashboard

Open another terminal:

```powershell
python -m streamlit run src/dashboard/app.py
```

The dashboard will be available locally through Streamlit.

---

## 13. Output Files

The network pipeline generates the following files under `data/processed/`:

| File | Purpose |
|---|---|
| `network_reference.csv` | Historical network reference dataset |
| `network_flows.jsonl` | Processed network flows and predictions |
| `network_traffic_summary.json` | Live network traffic statistics |
| `network_anomaly_alerts.jsonl` | Generated anomaly alerts |
| `network_drift_report.json` | Latest network drift report |
| `network_drift_history.jsonl` | Historical network drift evaluations |

The Telco pipeline maintains its own reference profiles and drift reports.

---

## 14. Limitations

GuardDog AI is a monitoring and decision-support system. Its outputs must be interpreted within the limitations of the implemented methods.

### Statistical limitations

- KS is a univariate numerical distribution test.
- PSI depends on the reference binning scheme.
- Chi-Square requires appropriate categorical observations and sufficient expected frequencies.
- Repeated batch testing can increase false-positive risk.
- A statistically significant change does not necessarily have practical importance.

### Network monitoring limitations

- Isolation Forest identifies unusual flows, not confirmed attacks.
- Network drift does not establish malicious activity.
- The current network monitoring pipeline does not establish whether model detection performance has degraded.
-
