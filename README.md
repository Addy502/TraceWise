# TraceWise

**Intelligent Data Reliability & Risk Platform**

TraceWise is a Python and Streamlit application that helps identify data quality issues, validate data contracts, diagnose simulated pipeline failures, explore downstream dependencies, assess potential impact, and perform controlled recovery with revalidation and audit records.

## Table of Contents

- [Overview](#overview)
- [Problem](#problem)
- [Key Capabilities](#key-capabilities)
- [Application Workflow](#application-workflow)
- [Architecture and Data Flow](#architecture-and-data-flow)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Run Locally](#run-locally)
- [Demo Dataset](#demo-dataset)
- [Understanding the Demo](#understanding-the-demo)
- [Limitations](#limitations)
- [Future Scope](#future-scope)

## Overview

Data quality problems can affect more than the dataset in which they originate. Missing values, duplicate identifiers, invalid numeric values, and schema violations can undermine reports, dashboards, and analytical workflows that depend on the data.

TraceWise brings several data reliability activities together in one interface. It provides data profiling and validation, contract checks, a simulated pipeline diagnosis and repair workflow, a dependency view for downstream impact, and controlled recovery with an audit trail.

## Problem

Data issues are often discovered after they have already affected downstream consumers. Teams need a way to identify unreliable records, understand which checks have failed, reason about possible downstream exposure, and validate a repair before relying on the data again.

TraceWise demonstrates an integrated workflow for these activities using a sample transaction dataset and a predefined dependency model.

## Key Capabilities

### 1. Reliability Overview

- Summarises the loaded dataset, including row and column counts.
- Presents data quality indicators and findings.
- Provides column-level profiling and a dataset preview.

### 2. Data Contracts

- Checks expected transaction data structure and required fields.
- Identifies missing required values and other configured rule violations.
- Presents contract-related findings for review.

### 3. Pipeline Lab

- Simulates data validation failures and repair workflows.
- Shows detected issues and suggested repair actions.
- Supports replaying validation against the working data after a repair.
- Displays validation and replay results.

### 4. Risk & Lineage

- Displays a predefined dependency graph connecting transaction data to downstream components.
- Illustrates which downstream components could be affected by an issue.
- Provides a RiskLens score using a heuristic calculation to demonstrate potential risk prioritisation.

### 5. Recovery & Audit

- Supports controlled quarantine of records associated with selected findings.
- Allows revalidation after recovery actions.
- Displays an audit trail and provides downloadable outputs where available.

## Application Workflow

1. **Load data:** Open the transaction dataset in the Streamlit application.
2. **Profile and inspect:** Review dataset dimensions, column profiles, and quality findings.
3. **Validate contracts:** Inspect required-field and configured data-rule violations.
4. **Diagnose:** Use Pipeline Lab to review a simulated failure and its suggested repair.
5. **Assess impact:** Explore the predefined lineage graph and heuristic RiskLens score.
6. **Recover and verify:** Quarantine selected problematic records, revalidate the working data, and review the audit information.

## Architecture and Data Flow

At a high level, the application is organised around a Streamlit user interface, a validation module, and a sample data directory.

```text
                 +---------------------------+
                 |       Streamlit UI        |
                 |          app.py           |
                 +-------------+-------------+
                               |
             +-----------------+------------------+
             |                 |                  |
             v                 v                  v
     +---------------+  +--------------+  +------------------+
     | Data profiling|  | Data contract|  | Pipeline Lab     |
     | and findings  |  | validation   |  | simulation       |
     +---------------+  +------+-------+  +--------+---------+
                               |                    |
                               v                    v
                     +-------------------------------+
                     | tracewise/validation.py       |
                     +-------------------------------+
                               |
                               v
                     +-------------------------------+
                     | Working data, revalidation,  |
                     | recovery and audit results   |
                     +-------------------------------+

     Risk & Lineage uses a predefined dependency model to
     illustrate possible downstream impact.
```

The lineage view demonstrates these example dependencies:

- Transaction Data → Daily Summary
- Transaction Data → Fraud Risk Model
- Daily Summary → Risk Dashboard
- Daily Summary → Finance Report
- Fraud Risk Model → Risk Dashboard
- Fraud Risk Model → Fraud Alert Queue

## Technology Stack

- **Language:** Python
- **Application framework:** Streamlit
- **Data processing:** Pandas and NumPy
- **Visualisation:** Plotly
- **Version control:** Git and GitHub

The exact installed package versions and dependencies are listed in [`requirements.txt`](requirements.txt).

## Repository Structure

```text
TraceWise/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   └── tracewise_logo.png
├── data/
│   ├── demo_transactions.csv
│   └── generate_data.py
└── tracewise/
    └── validation.py
```

## Run Locally

### Prerequisites

- Python 3.10 or a compatible Python version supported by the packages in `requirements.txt`
- Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/Addy502/TraceWise.git
cd TraceWise
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

## Demo Dataset

The repository includes `data/demo_transactions.csv`, a sample transaction dataset containing 1,000 rows and 7 columns. The demo data is designed to illustrate validation and recovery workflows.

The sample includes examples of:

- Duplicate transaction identifiers
- Missing required values
- Negative transaction amounts

`data/generate_data.py` contains the data-generation script used for the demo dataset.

## Understanding the Demo

TraceWise is a demonstration application. Its outputs should be interpreted in that context:

- **Findings** are produced by the validation rules implemented in the project.
- **Pipeline Lab** demonstrates a simulated failure, repair, and revalidation workflow.
- **Lineage** is represented by a predefined example dependency graph, not automatically discovered from a live production environment.
- **RiskLens** is a heuristic prioritisation score. It is not a measured financial loss, a calibrated probability, or a guarantee of actual downstream impact.
- **Recovery** operates on application working data. The original CSV file is not overwritten by the demonstrated recovery workflow.

## Limitations

- The included dataset and dependency graph are demonstration inputs, not a connection to a live enterprise data platform.
- Pipeline failure and repair behaviour is simulated within the application.
- RiskLens is heuristic and should not be treated as a production risk model.
- The application does not claim to automatically discover every upstream or downstream dependency in an external environment.

## Future Scope

Potential directions for further development include:

- Connectors for external databases, warehouses, and data pipelines.
- Configurable data contracts and reusable validation rule sets.
- Automated lineage discovery from pipeline metadata.
- More extensive recovery controls, approval workflows, and persistent audit storage.
- Calibrated risk models using operational evidence and historical incidents.

---

**TraceWise — making data reliability issues visible, understandable, and actionable.**
