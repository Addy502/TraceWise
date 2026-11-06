import hashlib
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tracewise.validation import validate_transactions


# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="TraceWise | Data Reliability",
    page_icon="🔎",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).parent
DATA_FILE = PROJECT_ROOT / "data" / "demo_transactions.csv"

REQUIRED_TRANSACTION_COLUMNS = {
    "transaction_id",
    "account_id",
    "transaction_date",
    "amount",
}

# -------------------------
# Sidebar branding and navigation
# -------------------------
LOGO_FILE = PROJECT_ROOT / "assets" / "tracewise_logo.png"

if LOGO_FILE.is_file():
    st.sidebar.image(str(LOGO_FILE), width=190)
else:
    st.sidebar.title("TraceWise")

st.sidebar.caption("Data Reliability & Risk Platform")

page = st.sidebar.radio(
    "Navigate",
    [
        "Reliability Overview",
        "Data Contracts",
        "Pipeline Lab",
        "Risk & Lineage",
        "Recovery & Audit",
    ],
)

# -------------------------
# Unified visual identity — Arctic Blue
# The same palette is applied consistently across all five pages.
# -------------------------
palette = {
    "name": "Refined Arctic",
    # Warm, high-contrast light palette
    "background": "#F3F2EE",
    "surface": "#FFFEFC",
    "soft": "#E5E8E5",
    "accent": "#287F91",
    "deep": "#203447",
}

st.markdown(
    f"""
    <style>
    :root {{
      color-scheme: light dark;
      --tw-bg: {palette['background']};
      --tw-surface: {palette['surface']};
      --tw-soft: {palette['soft']};
      --tw-accent: {palette['accent']};
      --tw-deep: {palette['deep']};
      --tw-muted: #63717C;
      --tw-border: #D9DFDF;
      --tw-shadow: 0 5px 20px rgba(32, 52, 71, .055);
    }}

    /* Respect the visitor's system appearance preference. */
    @media (prefers-color-scheme: dark) {{
      :root {{
        --tw-bg: #111D29;
        --tw-surface: #1B2B3A;
        --tw-soft: #263B4B;
        --tw-accent: #63B5C2;
        --tw-deep: #E8F0F3;
        --tw-muted: #B2C0C8;
        --tw-border: #344958;
        --tw-shadow: 0 6px 22px rgba(0, 0, 0, .18);
      }}
    }}

    .stApp {{ background: var(--tw-bg); color: var(--tw-deep); }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{
      background: var(--tw-surface);
      border-right: 1px solid var(--tw-border);
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
      color: var(--tw-muted);
    }}
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {{ color: var(--tw-muted); }}
    h1, h2, h3, h4, label {{ color: var(--tw-deep); letter-spacing: -.02em; }}

    [data-testid="stMetric"] {{
      background: var(--tw-surface);
      border: 1px solid var(--tw-border);
      border-radius: 16px;
      padding: 18px 20px;
      box-shadow: var(--tw-shadow);
    }}
    [data-testid="stMetricLabel"] {{ color: var(--tw-muted); font-size: .86rem; }}
    [data-testid="stMetricValue"] {{ color: var(--tw-deep); font-weight: 700; }}
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
      border: 1px solid var(--tw-border);
      border-radius: 14px;
      overflow: hidden;
    }}
    [data-testid="stExpander"] {{
      border: 1px solid var(--tw-border);
      border-radius: 14px;
      background: var(--tw-surface);
    }}
    [data-testid="stAlert"] {{ border-radius: 12px; }}

    .stButton > button, .stDownloadButton > button {{
      border-radius: 10px;
      font-weight: 600;
      border-color: var(--tw-border);
      transition: all .15s ease;
    }}
    .stButton > button[kind="primary"] {{
      background: var(--tw-accent);
      border-color: var(--tw-accent);
      color: #FFFFFF;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
      border-color: var(--tw-accent);
      color: var(--tw-accent);
    }}
    [data-testid="stRadio"] [role="radiogroup"] {{ gap: .35rem; }}
    [data-testid="stRadio"] label {{ border-radius: 10px; padding: .35rem .55rem; }}
    hr {{ border-color: var(--tw-border); }}

    /* Keep form controls legible in both appearances. */
    [data-baseweb="input"], [data-baseweb="select"],
    [data-baseweb="textarea"], [data-testid="stFileUploader"] {{
      border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("TraceWise")
st.subheader(page)
st.caption(
    "Detect unreliable data. Trace downstream impact. "
    "Understand business risk. Verify recovery."
)

# -------------------------
# Load dataset
# -------------------------
st.header("Data Quality")
uploaded_file = st.file_uploader(
    "Upload your own CSV dataset",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        source_df = pd.read_csv(uploaded_file)
        dataset_name = uploaded_file.name
        source_bytes = uploaded_file.getvalue()
        st.success(f"Uploaded {uploaded_file.name} successfully.")
    except Exception as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
else:
    if not DATA_FILE.exists():
        st.error(f"Demo dataset not found: {DATA_FILE}")
        st.stop()

    try:
        source_df = pd.read_csv(DATA_FILE)
        source_bytes = DATA_FILE.read_bytes()
    except Exception as exc:
        st.error(f"Could not read the demo dataset: {exc}")
        st.stop()

    dataset_name = DATA_FILE.name
    st.caption("Currently analysing the built-in demo dataset.")

if source_df.empty:
    st.error("This CSV contains no data rows.")
    st.stop()

dataset_signature = hashlib.sha256(
    (dataset_name + ":").encode("utf-8") + source_bytes
).hexdigest()

# Keep remediation changes in a session-only working copy. The uploaded/demo
# source is never overwritten; changing datasets resets the working copy.
if st.session_state.get("dataset_signature") != dataset_signature:
    st.session_state["dataset_signature"] = dataset_signature
    st.session_state["source_df"] = source_df.copy(deep=True)
    st.session_state["working_df"] = source_df.copy(deep=True)
    st.session_state["quarantine_records"] = pd.DataFrame()
    st.session_state["remediation_audit"] = []

df = st.session_state["working_df"].copy(deep=True)

st.info(
    f"Analysing {len(df):,} rows across {len(df.columns)} columns "
    f"in {dataset_name}."
)

# -------------------------
# Shared calculations
# Keep these outside page conditions because multiple pages use them.
# -------------------------
normalised_columns = {
    str(column).strip().lower()
    for column in df.columns
}
missing_columns = REQUIRED_TRANSACTION_COLUMNS - normalised_columns
is_transaction_dataset = not missing_columns

# Generic data-quality findings are calculated for every dataset.
generic_findings = []
for column in df.columns:
    missing_count = int(df[column].isna().sum())
    if missing_count:
        generic_findings.append(
            {
                "Severity": "Medium",
                "Issue": "MISSING_VALUES",
                "Column": str(column),
                "Count": missing_count,
                "Details": (
                    f"{missing_count} rows have missing values "
                    f"in '{column}'."
                ),
            }
        )

duplicate_rows = int(df.duplicated().sum())
if duplicate_rows:
    generic_findings.append(
        {
            "Severity": "Medium",
            "Issue": "DUPLICATE_ROWS",
            "Column": "(entire row)",
            "Count": duplicate_rows,
            "Details": f"{duplicate_rows} fully duplicated rows found.",
        }
    )

# Check negative values in numeric columns whose names commonly
# represent non-negative business measures. This is intentionally
# semantic rather than universal: negative temperatures, for example,
# can be valid and should not be flagged automatically.
NON_NEGATIVE_COLUMN_TERMS = (
    "amount",
    "price",
    "quantity",
    "balance",
    "salary",
    "wage",
    "pay",
    "compensation",
    "income",
    "revenue",
    "cost",
    "fee",
    "charge",
    "count",
    "stock",
    "inventory",
)

for column in df.select_dtypes(include="number").columns:
    column_name = str(column).strip().lower().replace("-", "_").replace(" ", "_")
    name_parts = set(column_name.split("_"))

    if any(
        term in column_name or term in name_parts
        for term in NON_NEGATIVE_COLUMN_TERMS
    ):
        negative_count = int((df[column] < 0).sum())
        if negative_count:
            generic_findings.append(
                {
                    "Severity": "High",
                    "Issue": "NEGATIVE_VALUE",
                    "Column": str(column),
                    "Count": negative_count,
                    "Details": (
                        f"{negative_count} negative values found in "
                        f"'{column}'. This column appears to represent "
                        "a non-negative business measure; review whether "
                        "these values are valid."
                    ),
                }
            )

# Calculate transaction findings for all pages; display them only on Data Contracts.
findings = []
high_findings = 0
critical_findings = 0
actual_names = {
    str(column).strip().lower(): column
    for column in df.columns
}

if is_transaction_dataset:
    transaction_df = df.rename(
        columns={
            actual_names[name]: name
            for name in REQUIRED_TRANSACTION_COLUMNS
            if actual_names[name] != name
        }
    )
    findings = validate_transactions(transaction_df)
    high_findings = sum(finding.get("severity") == "High" for finding in findings)
    critical_findings = sum(
        finding.get("severity") == "Critical" for finding in findings
    )

# Shared demo dependency graph. The graph itself is available to RiskLens,
# while the visualisation is displayed only on Risk & Lineage.
dependencies = {
    "Transaction Data": ["Daily Summary", "Fraud Risk Model"],
    "Daily Summary": ["Risk Dashboard", "Finance Report"],
    "Fraud Risk Model": ["Risk Dashboard", "Fraud Alert Queue"],
    "Risk Dashboard": [],
    "Finance Report": [],
    "Fraud Alert Queue": [],
}

graph = nx.DiGraph()
for upstream, downstream_list in dependencies.items():
    graph.add_node(upstream)
    for downstream in downstream_list:
        graph.add_edge(upstream, downstream)

# -------------------------
# Reliability Overview
# -------------------------
if page == "Reliability Overview":
    st.divider()
    st.subheader("Dataset Overview")

    total_cells = len(df) * len(df.columns)
    missing_cells = int(df.isna().sum().sum())
    completeness_pct = (
        100 * (total_cells - missing_cells) / total_cells if total_cells else 0
    )

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Rows", f"{len(df):,}")
    metric2.metric("Columns", len(df.columns))
    metric3.metric("Missing cells", f"{missing_cells:,}")
    metric4.metric("Duplicate rows", f"{duplicate_rows:,}")

    st.caption(f"Overall cell completeness: {completeness_pct:.2f}%")

    profile_rows = []
    for column in df.columns:
        series = df[column]
        profile_rows.append(
            {
                "Column": str(column),
                "Detected type": str(series.dtype),
                "Non-null values": int(series.notna().sum()),
                "Missing values": int(series.isna().sum()),
                "Distinct values": int(series.nunique()),
                "Completeness (%)": round(100 * series.notna().mean(), 2),
            }
        )

    st.subheader("Column Profiling")
    st.dataframe(pd.DataFrame(profile_rows), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Generic Data Quality Findings")
    if generic_findings:
        st.dataframe(
            pd.DataFrame(generic_findings),
            width="stretch",
            hide_index=True,
        )
    else:
        st.success("No issues detected by the generic profiling checks.")

    st.divider()
    st.subheader("Dataset Preview")
    with st.expander("View records", expanded=False):
        st.dataframe(df.head(20), width="stretch")

    active_finding_count = len(findings) if is_transaction_dataset else len(generic_findings)
    st.divider()
    st.subheader("Reliability Snapshot")
    snapshot1, snapshot2, snapshot3 = st.columns(3)
    snapshot1.metric("Active validation findings", active_finding_count)
    snapshot2.metric("Cell completeness", f"{completeness_pct:.2f}%")
    snapshot3.metric(
        "Working-copy rows removed to quarantine",
        len(st.session_state.get("quarantine_records", pd.DataFrame())),
    )

# -------------------------
# Data Contracts
# -------------------------
elif page == "Data Contracts":
    st.divider()
    st.header("Data Contracts")
    st.markdown(
        "A data contract describes the structure and basic expectations "
        "a dataset should satisfy before downstream use."
    )

    st.subheader("Required transaction schema")
    contract_rows = [
        {
            "Column": "transaction_id",
            "Expectation": "Present; transaction identifier should be unique",
            "Status": "Present" if "transaction_id" in normalised_columns else "Missing",
        },
        {
            "Column": "account_id",
            "Expectation": "Present; required account reference",
            "Status": "Present" if "account_id" in normalised_columns else "Missing",
        },
        {
            "Column": "transaction_date",
            "Expectation": "Present; should contain a valid date",
            "Status": "Present" if "transaction_date" in normalised_columns else "Missing",
        },
        {
            "Column": "amount",
            "Expectation": "Present; should be numeric and reviewed for invalid values",
            "Status": "Present" if "amount" in normalised_columns else "Missing",
        },
    ]
    st.dataframe(pd.DataFrame(contract_rows), width="stretch", hide_index=True)

    if is_transaction_dataset:
        st.success("The dataset contains all required transaction columns.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Transaction findings", len(findings))
        col2.metric("High-severity rules", high_findings)
        col3.metric("Critical rules", critical_findings)

        if findings:
            st.subheader("Transaction Validation Findings")
            st.dataframe(pd.DataFrame(findings), width="stretch", hide_index=True)
        else:
            st.success("No issues detected by transaction validation rules.")
    else:
        st.warning(
            "This CSV does not match the transaction schema. "
            "Transaction-specific validation was skipped."
        )
        st.write("Missing transaction columns:", sorted(missing_columns))
        st.write("Available columns:", list(df.columns))

    st.divider()
    st.subheader("Generic contract signals")
    if generic_findings:
        st.dataframe(pd.DataFrame(generic_findings), width="stretch", hide_index=True)
    else:
        st.success("No generic missing-value, duplicate-row, or negative-value findings.")

    st.caption(
        "Current checks are rule-based. Date parsing, configurable freshness "
        "thresholds, and user-defined contracts can be added in a later iteration."
    )

# -------------------------
# Pipeline Lab
# -------------------------
elif page == "Pipeline Lab":
    st.divider()
    st.header("Pipeline Lab")
    st.markdown(
        "Inject a controlled data-quality failure into an isolated lab copy, "
        "inspect the diagnosis, then apply a suggested repair and replay validation. "
        "Your main working copy and source CSV are not changed by this lab."
    )

    # The lab is isolated from Recovery & Audit. Seed it from the current working
    # copy when first opened for this source dataset; users can reset it at any time.
    lab_signature_key = "pipeline_lab_dataset_signature"
    if (
        st.session_state.get(lab_signature_key) != dataset_signature
        or "pipeline_lab_base_df" not in st.session_state
        or "pipeline_lab_df" not in st.session_state
    ):
        st.session_state[lab_signature_key] = dataset_signature
        st.session_state["pipeline_lab_base_df"] = df.copy(deep=True)
        st.session_state["pipeline_lab_df"] = df.copy(deep=True)
        st.session_state["pipeline_lab_failure"] = "None"
        st.session_state["pipeline_lab_injected"] = False
        st.session_state["pipeline_lab_injected_column"] = None
        st.session_state["pipeline_lab_injected_index"] = None
        st.session_state["pipeline_lab_audit"] = []

    lab_base_df = st.session_state["pipeline_lab_base_df"].copy(deep=True)
    lab_df = st.session_state["pipeline_lab_df"].copy(deep=True)
    lab_actual_names = {str(c).strip().lower(): c for c in lab_df.columns}
    lab_is_transaction = REQUIRED_TRANSACTION_COLUMNS.issubset(lab_actual_names)

    st.subheader("1. Choose a failure to simulate")
    if lab_is_transaction:
        failure_options = [
            "None",
            "Missing required value",
            "Duplicate transaction ID",
            "Negative transaction amount",
            "Schema violation (remove account_id column)",
        ]
    else:
        failure_options = [
            "None",
            "Missing value",
            "Duplicate full row",
            "Schema violation (remove first column)",
        ]
        numeric_candidates = list(lab_df.select_dtypes(include="number").columns)
        if numeric_candidates:
            failure_options.append("Negative numeric value")

    selected_failure = st.selectbox(
        "Failure type",
        failure_options,
        key="pipeline_lab_failure_selector",
        help="Each simulation changes only the isolated Pipeline Lab copy.",
    )
    inject_col, reset_col = st.columns(2)
    with inject_col:
        inject_clicked = st.button("Inject failure", type="primary")
    with reset_col:
        reset_lab_clicked = st.button("Reset lab to baseline")

    if reset_lab_clicked:
        st.session_state["pipeline_lab_df"] = lab_base_df.copy(deep=True)
        st.session_state["pipeline_lab_failure"] = "None"
        st.session_state["pipeline_lab_injected"] = False
        st.session_state["pipeline_lab_injected_column"] = None
        st.session_state["pipeline_lab_injected_index"] = None
        st.session_state["pipeline_lab_audit"] = []
        st.rerun()

    if inject_clicked:
        lab_df = lab_base_df.copy(deep=True)
        lab_actual_names = {str(c).strip().lower(): c for c in lab_df.columns}
        st.session_state["pipeline_lab_injected_column"] = None
        st.session_state["pipeline_lab_injected_index"] = None
        if selected_failure == "None":
            st.session_state["pipeline_lab_failure"] = "None"
            st.session_state["pipeline_lab_injected"] = False
        elif selected_failure in ("Missing required value", "Missing value"):
            target = lab_actual_names.get("account_id") if lab_is_transaction else lab_df.columns[0]
            if len(lab_df) > 0:
                candidate_rows = lab_df.index[lab_df[target].notna()]
                target_index = candidate_rows[0] if len(candidate_rows) else lab_df.index[0]
                lab_df.loc[target_index, target] = pd.NA
                st.session_state["pipeline_lab_injected_column"] = target
                st.session_state["pipeline_lab_injected_index"] = target_index
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        elif selected_failure == "Duplicate transaction ID":
            target = lab_actual_names["transaction_id"]
            if len(lab_df) > 1:
                lab_df.loc[lab_df.index[1], target] = lab_df.iloc[0][target]
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        elif selected_failure == "Negative transaction amount":
            target = lab_actual_names["amount"]
            if len(lab_df) > 0:
                target_index = lab_df.index[0]
                original_value = pd.to_numeric(pd.Series([lab_df.loc[target_index, target]]), errors="coerce").iloc[0]
                lab_df.loc[target_index, target] = -abs(float(original_value)) if pd.notna(original_value) else -1.0
                st.session_state["pipeline_lab_injected_column"] = target
                st.session_state["pipeline_lab_injected_index"] = target_index
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        elif selected_failure == "Duplicate full row":
            if len(lab_df) > 1:
                lab_df.loc[lab_df.index[1], :] = lab_df.iloc[0].values
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        elif selected_failure == "Negative numeric value":
            target = lab_df.select_dtypes(include="number").columns[0]
            if len(lab_df) > 0:
                target_index = lab_df.index[0]
                value = pd.to_numeric(pd.Series([lab_df.loc[target_index, target]]), errors="coerce").iloc[0]
                lab_df.loc[target_index, target] = -abs(float(value)) if pd.notna(value) else -1.0
                st.session_state["pipeline_lab_injected_column"] = target
                st.session_state["pipeline_lab_injected_index"] = target_index
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        elif selected_failure.startswith("Schema violation"):
            target = lab_actual_names.get("account_id") if lab_is_transaction else lab_df.columns[0]
            if target in lab_df.columns:
                lab_df = lab_df.drop(columns=[target])
            st.session_state["pipeline_lab_failure"] = selected_failure
            st.session_state["pipeline_lab_injected"] = True
        st.session_state["pipeline_lab_df"] = lab_df.copy(deep=True)
        st.rerun()

    lab_df = st.session_state["pipeline_lab_df"].copy(deep=True)
    active_failure = st.session_state.get("pipeline_lab_failure", "None")
    lab_actual_names = {str(c).strip().lower(): c for c in lab_df.columns}
    lab_is_transaction = REQUIRED_TRANSACTION_COLUMNS.issubset(lab_actual_names)

    st.divider()
    st.subheader("2. Diagnosis")
    lab_total_cells = len(lab_df) * len(lab_df.columns)
    lab_missing_cells = int(lab_df.isna().sum().sum())
    lab_duplicate_rows = int(lab_df.duplicated().sum())
    lab_generic_findings = []
    for column in lab_df.columns:
        count = int(lab_df[column].isna().sum())
        if count:
            lab_generic_findings.append({
                "Severity": "Medium", "Issue": "MISSING_VALUES",
                "Column": str(column), "Count": count,
                "Details": f"{count} missing value(s) in '{column}'."
            })
    if lab_duplicate_rows:
        lab_generic_findings.append({
            "Severity": "Medium", "Issue": "DUPLICATE_ROWS",
            "Column": "(entire row)", "Count": lab_duplicate_rows,
            "Details": f"{lab_duplicate_rows} fully duplicated row(s) found."
        })
    for column in lab_df.select_dtypes(include="number").columns:
        if any(term in str(column).strip().lower() for term in ("amount", "price", "quantity", "balance")):
            count = int((lab_df[column] < 0).sum())
            if count:
                lab_generic_findings.append({
                    "Severity": "High", "Issue": "NEGATIVE_VALUE",
                    "Column": str(column), "Count": count,
                    "Details": f"{count} negative value(s) in '{column}'."
                })

    lab_transaction_findings = []
    if lab_is_transaction:
        normalized_lab_df = lab_df.rename(columns={
            lab_actual_names[name]: name
            for name in REQUIRED_TRANSACTION_COLUMNS
            if lab_actual_names[name] != name
        })
        lab_transaction_findings = validate_transactions(normalized_lab_df)

    diagnosis_col1, diagnosis_col2, diagnosis_col3 = st.columns(3)
    diagnosis_col1.metric("Rows in lab copy", f"{len(lab_df):,}")
    diagnosis_col2.metric("Generic signals", len(lab_generic_findings))
    diagnosis_col3.metric(
        "Transaction rules failed" if lab_is_transaction else "Schema status",
        len(lab_transaction_findings) if lab_is_transaction else ("Valid" if lab_is_transaction else "Not transaction schema"),
    )

    active_rule_names = {str(item.get("rule", "")) for item in lab_transaction_findings}
    active_generic_names = {str(item.get("Issue", "")) for item in lab_generic_findings}
    if active_failure == "None":
        st.info("No simulated failure is active. Choose a failure above and click Inject failure.")
    elif active_failure.startswith("Schema violation"):
        missing_contract_columns = sorted(REQUIRED_TRANSACTION_COLUMNS - set(lab_actual_names))
        if missing_contract_columns:
            st.warning(
                f"Active diagnosis: the transaction schema is incomplete. Missing required column(s): {', '.join(missing_contract_columns)}."
            )
        else:
            st.success("The schema violation has been resolved. All required transaction columns are present again.")
    elif active_failure == "Duplicate transaction ID":
        if "DUPLICATE_TRANSACTION_IDS" in active_rule_names:
            duplicate_count = sum(
                int(item.get("count", 0)) for item in lab_transaction_findings
                if item.get("rule") == "DUPLICATE_TRANSACTION_IDS"
            )
            st.warning(
                f"Active diagnosis: duplicate transaction IDs remain ({duplicate_count} affected row(s)). "
                "This can cause double-counting or ambiguous record matching downstream."
            )
        else:
            st.success(
                "Resolved: duplicate transaction IDs are no longer detected. "
                f"{len(lab_transaction_findings)} transaction validation finding(s) remain; review them below."
            )
    elif "Missing" in active_failure:
        injected_column = st.session_state.get("pipeline_lab_injected_column")
        injected_index = st.session_state.get("pipeline_lab_injected_index")
        injected_cell_missing = (
            injected_column in lab_df.columns
            and injected_index in lab_df.index
            and pd.isna(lab_df.loc[injected_index, injected_column])
        )
        if injected_cell_missing:
            st.warning(
                f"Active diagnosis: the injected missing value remains in "
                f"'{injected_column}'. Other missing values are reported separately."
            )
        else:
            st.success(
                "Resolved: the injected missing value is no longer present. "
                "Any unrelated missing-value findings remain listed below."
            )
    elif "Negative" in active_failure:
        injected_column = st.session_state.get("pipeline_lab_injected_column")
        injected_index = st.session_state.get("pipeline_lab_injected_index")
        injected_value = None
        if injected_column in lab_df.columns and injected_index in lab_df.index:
            injected_value = pd.to_numeric(
                pd.Series([lab_df.loc[injected_index, injected_column]]),
                errors="coerce",
            ).iloc[0]
        if pd.notna(injected_value) and injected_value < 0:
            st.warning(
                f"Active diagnosis: the injected negative value remains in "
                f"'{injected_column}'. Confirm whether negative values are permitted."
            )
        else:
            st.success(
                "Resolved: the injected negative value is no longer present. "
                "Other negative-value findings remain listed separately."
            )
    elif active_failure == "Duplicate full row":
        if "DUPLICATE_ROWS" in active_generic_names:
            st.warning("Active diagnosis: fully duplicated records remain, which may inflate counts or totals.")
        else:
            st.success("Resolved: no fully duplicated rows are currently detected.")

    if lab_transaction_findings:
        st.markdown("**Transaction validation output**")
        st.dataframe(pd.DataFrame(lab_transaction_findings), width="stretch", hide_index=True)
    if lab_generic_findings:
        st.markdown("**Generic data-quality signals**")
        st.dataframe(pd.DataFrame(lab_generic_findings), width="stretch", hide_index=True)
    if not lab_transaction_findings and not lab_generic_findings and active_failure != "None":
        st.info("The current validation rules did not detect this injected failure. This is useful evidence of a contract gap.")

    with st.expander("Preview lab records", expanded=False):
        st.dataframe(lab_df.head(20), width="stretch", hide_index=True)

    st.divider()
    st.subheader("3. Suggested repair and replay")
    if active_failure == "None":
        st.caption("Inject a failure first to enable the suggested repair workflow.")
    else:
        repair_descriptions = {
            "Missing required value": "Remove rows with missing required transaction values from the lab copy.",
            "Missing value": "Remove rows containing missing values from the lab copy.",
            "Duplicate transaction ID": "Keep the first occurrence of each non-null transaction ID.",
            "Negative transaction amount": "Remove rows with negative transaction amounts from the lab copy.",
            "Negative numeric value": "Remove rows with negative values in the selected numeric column from the lab copy.",
            "Duplicate full row": "Keep the first occurrence of each fully duplicated row.",
            "Schema violation (remove account_id column)": "Restore the missing account_id column from the lab baseline.",
            "Schema violation (remove first column)": "Restore the removed column from the lab baseline.",
        }
        st.write("**Proposed action:**", repair_descriptions.get(active_failure, "Restore the lab copy to its baseline and replay validation."))
        if st.button("Apply suggested repair and replay", type="primary"):
            before_rows = len(lab_df)
            before_transaction_findings = validate_transactions(
                lab_df.rename(columns={
                    {str(c).strip().lower(): c for c in lab_df.columns}[name]: name
                    for name in REQUIRED_TRANSACTION_COLUMNS
                    if {str(c).strip().lower(): c for c in lab_df.columns}.get(name) != name
                })
            ) if REQUIRED_TRANSACTION_COLUMNS.issubset({str(c).strip().lower() for c in lab_df.columns}) else []
            before_rule_names = sorted({str(item.get("rule", "")) for item in before_transaction_findings})
            repaired = lab_df.copy(deep=True)
            repaired_names = {str(c).strip().lower(): c for c in repaired.columns}
            if active_failure in ("Duplicate transaction ID",) and "transaction_id" in repaired_names:
                col = repaired_names["transaction_id"]
                repaired = repaired.loc[repaired[col].isna() | ~repaired[col].duplicated(keep="first")].copy()
            elif active_failure == "Missing required value":
                cols = [repaired_names[name] for name in REQUIRED_TRANSACTION_COLUMNS if name in repaired_names]
                if cols:
                    repaired = repaired.dropna(subset=cols).copy()
            elif active_failure == "Missing value":
                repaired = repaired.dropna().copy()
            elif active_failure == "Negative transaction amount" and "amount" in repaired_names:
                col = repaired_names["amount"]
                repaired = repaired.loc[pd.to_numeric(repaired[col], errors="coerce").fillna(0) >= 0].copy()
            elif active_failure == "Negative numeric value":
                col = repaired.select_dtypes(include="number").columns[0]
                repaired = repaired.loc[repaired[col] >= 0].copy()
            elif active_failure == "Duplicate full row":
                repaired = repaired.drop_duplicates(keep="first").copy()
            elif active_failure.startswith("Schema violation"):
                baseline = st.session_state["pipeline_lab_base_df"].copy(deep=True)
                for col in baseline.columns:
                    if col not in repaired.columns:
                        repaired[col] = baseline[col]
                repaired = repaired[baseline.columns].copy()
            after_rows = len(repaired)
            repaired_names = {str(c).strip().lower(): c for c in repaired.columns}
            after_is_transaction = REQUIRED_TRANSACTION_COLUMNS.issubset(repaired_names)
            if after_is_transaction:
                normalized_repaired = repaired.rename(columns={
                    repaired_names[name]: name for name in REQUIRED_TRANSACTION_COLUMNS
                    if repaired_names[name] != name
                })
                after_transaction_findings = validate_transactions(normalized_repaired)
            else:
                after_transaction_findings = []
            after_rule_names = sorted({str(item.get("rule", "")) for item in after_transaction_findings})
            resolved_rules = sorted(set(before_rule_names) - set(after_rule_names))
            st.session_state["pipeline_lab_df"] = repaired.copy(deep=True)
            st.session_state["pipeline_lab_audit"].append({
                "Failure simulated": active_failure,
                "Repair applied": repair_descriptions.get(active_failure, "Baseline restoration"),
                "Rows before": before_rows,
                "Rows after": after_rows,
                "Rows removed": before_rows - after_rows,
                "Transaction rules before": "; ".join(before_rule_names) or "None",
                "Transaction rules after": "; ".join(after_rule_names) or "None",
                "Rules resolved": "; ".join(resolved_rules) or "None",
            })
            st.success(f"Replay complete. Lab copy now contains {after_rows:,} rows (before: {before_rows:,}).")
            st.rerun()

    if st.session_state.get("pipeline_lab_audit"):
        st.subheader("Pipeline replay history")
        st.dataframe(pd.DataFrame(st.session_state["pipeline_lab_audit"]), width="stretch", hide_index=True)
        audit_csv = pd.DataFrame(st.session_state["pipeline_lab_audit"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Pipeline Lab audit CSV",
            data=audit_csv,
            file_name="tracewise_pipeline_lab_audit.csv",
            mime="text/csv",
        )

    st.caption(
        "Scope note: this is a controlled demonstration using local CSV data and a predefined lineage graph. "
        "It does not execute a real production pipeline or establish actual downstream loss."
    )

# -------------------------
# Risk & Lineage: BlastRadius + RiskLens
# -------------------------
elif page == "Risk & Lineage":
    st.divider()
    st.header("BlastRadius")
    st.markdown(
        "Trace which downstream data products could be affected "
        "when an upstream dataset has a quality issue."
    )

    source_node = st.selectbox(
        "Investigate an upstream component",
        options=list(dependencies.keys()),
        index=0,
    )

    downstream_nodes = nx.descendants(graph, source_node)
    visible_nodes = {source_node} | downstream_nodes
    visible_edges = [
        (source, target)
        for source, target in graph.edges()
        if source in visible_nodes and target in visible_nodes
    ]

    impact_col1, impact_col2 = st.columns(2)
    impact_col1.metric("Downstream components", len(downstream_nodes))
    impact_col2.metric("Dependency links", len(visible_edges))

    if downstream_nodes:
        st.write(
            "Potentially affected components:",
            ", ".join(sorted(downstream_nodes)),
        )
    else:
        st.info("No downstream components depend on this component.")

    positions = {
        "Transaction Data": (0, 2),
        "Daily Summary": (1, 3),
        "Fraud Risk Model": (1, 1),
        "Risk Dashboard": (2, 2),
        "Finance Report": (2, 3),
        "Fraud Alert Queue": (2, 1),
    }

    fig = go.Figure()
    for upstream, downstream in visible_edges:
        x0, y0 = positions[upstream]
        x1, y1 = positions[downstream]
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=palette["accent"], width=2),
                hoverinfo="text",
                text=[f"{upstream} → {downstream}"] * 2,
                showlegend=False,
            )
        )

    node_x, node_y, node_labels, node_colors, node_hover = [], [], [], [], []
    for node in visible_nodes:
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(node)
        if node == source_node:
            node_colors.append(palette["deep"])
            node_hover.append(f"{node} (selected source)")
        else:
            node_colors.append(palette["accent"])
            node_hover.append(f"{node} (potentially affected)")

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_labels,
            textposition="bottom center",
            hovertext=node_hover,
            hoverinfo="text",
            marker=dict(
                size=28,
                color=node_colors,
                line=dict(color=palette["soft"], width=2),
            ),
            showlegend=False,
        )
    )
    fig.update_layout(
        height=440,
        margin=dict(l=20, r=20, t=20, b=50),
        xaxis=dict(visible=False, range=[-0.3, 2.6]),
        yaxis=dict(visible=False, range=[0.4, 3.6]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "This is a predefined demonstration lineage graph. Highlighted nodes "
        "indicate potential impact, not confirmed data corruption."
    )

    st.divider()
    st.header("RiskLens")
    st.markdown(
        "A transparent heuristic that combines finding severity, potential "
        "downstream reach, affected-row proportion, and business criticality. "
        "This is a decision-support score, not a measured financial loss."
    )

    risk_findings = findings if is_transaction_dataset else generic_findings

    def finding_value(finding, *keys, default=None):
        for key in keys:
            if key in finding:
                return finding[key]
        return default

    severity_weights = {"Critical": 100, "High": 75, "Medium": 45, "Low": 20}
    max_severity = max(
        (
            severity_weights.get(
                str(finding_value(item, "severity", "Severity", default="Low")),
                20,
            )
            for item in risk_findings
        ),
        default=0,
    )
    max_affected_count = max(
        (
            int(finding_value(item, "count", "Count", default=0) or 0)
            for item in risk_findings
        ),
        default=0,
    )
    affected_pct = min(100.0, 100.0 * max_affected_count / max(len(df), 1))
    blast_radius_pct = (
        100.0 * len(downstream_nodes) / max(graph.number_of_nodes() - 1, 1)
    )

    criticality = st.slider(
        "Business criticality of the selected upstream component",
        min_value=0,
        max_value=100,
        value=80,
        help="Set this using your team's context. It is metadata/input, not inferred from the CSV.",
    )

    risk_score = round(
        0.35 * max_severity
        + 0.30 * blast_radius_pct
        + 0.20 * affected_pct
        + 0.15 * criticality
    )
    risk_score = max(0, min(100, risk_score))

    if risk_score >= 80:
        risk_band = "Critical"
    elif risk_score >= 60:
        risk_band = "High"
    elif risk_score >= 30:
        risk_band = "Medium"
    else:
        risk_band = "Low"

    risk_col1, risk_col2, risk_col3 = st.columns(3)
    risk_col1.metric("Explainable risk score", f"{risk_score}/100", risk_band)
    risk_col2.metric("Highest finding severity", f"{max_severity}/100")
    risk_col3.metric(
        "Rows implicated by largest finding",
        f"{max_affected_count:,} ({affected_pct:.2f}%)",
    )

    risk_factors = pd.DataFrame(
        [
            {
                "Factor": "Finding severity",
                "Value (0–100)": max_severity,
                "Weight": "35%",
                "Contribution": round(0.35 * max_severity, 1),
            },
            {
                "Factor": "Potential downstream reach",
                "Value (0–100)": round(blast_radius_pct, 1),
                "Weight": "30%",
                "Contribution": round(0.30 * blast_radius_pct, 1),
            },
            {
                "Factor": "Affected-row proportion",
                "Value (0–100)": round(affected_pct, 2),
                "Weight": "20%",
                "Contribution": round(0.20 * affected_pct, 1),
            },
            {
                "Factor": "Business criticality (user-set)",
                "Value (0–100)": criticality,
                "Weight": "15%",
                "Contribution": round(0.15 * criticality, 1),
            },
        ]
    )
    st.dataframe(risk_factors, width="stretch", hide_index=True)
    st.caption(
        "Formula: 0.35 × severity + 0.30 × downstream reach + "
        "0.20 × affected-row proportion + 0.15 × business criticality. "
        "The largest finding count is used for affected-row proportion to reduce "
        "double-counting overlapping findings. Reach describes potential impact, "
        "not confirmed damage."
    )

    if not risk_findings:
        st.success("No configured data-quality findings are currently active.")
    else:
        st.write("**Evidence contributing to this assessment**")
        evidence_rows = []
        for item in risk_findings:
            evidence_rows.append(
                {
                    "Rule / issue": finding_value(item, "rule", "Issue", default="Unknown"),
                    "Severity": finding_value(item, "severity", "Severity", default="Unknown"),
                    "Column": finding_value(item, "column", "Column", default="—"),
                    "Affected rows": finding_value(item, "count", "Count", default=0),
                    "Evidence": finding_value(item, "message", "Details", default=""),
                }
            )
        st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)

# -------------------------
# Recovery & Audit
# -------------------------
elif page == "Recovery & Audit":
    st.divider()
    st.header("Recovery & revalidation")
    st.caption(
        "Choose a deterministic action. Affected rows are moved to a quarantine "
        "table for review; the original uploaded/demo file remains unchanged."
    )

    if is_transaction_dataset:
        actual_names_for_fix = {
            str(column).strip().lower(): column
            for column in df.columns
        }

        action_options = [
            "Quarantine duplicate transaction IDs (keep first occurrence)",
            "Quarantine rows missing required transaction values",
            "Quarantine rows with negative transaction amounts",
        ]
        chosen_action = st.selectbox(
            "Select a remediation action",
            action_options,
        )

        current_working_df = st.session_state["working_df"].copy(deep=True)
        selected_mask = pd.Series(False, index=current_working_df.index)
        reason = chosen_action

        if chosen_action.startswith("Quarantine duplicate"):
            column = actual_names_for_fix.get("transaction_id")
            if column is not None:
                selected_mask = (
                    current_working_df[column].notna()
                    & current_working_df[column].duplicated(keep="first")
                )

        elif chosen_action.startswith("Quarantine rows missing"):
            required_present = [
                actual_names_for_fix[name]
                for name in (
                    "transaction_id",
                    "account_id",
                    "transaction_date",
                    "amount",
                )
                if name in actual_names_for_fix
            ]
            if required_present:
                selected_mask = current_working_df[required_present].isna().any(axis=1)

        elif chosen_action.startswith("Quarantine rows with negative"):
            column = actual_names_for_fix.get("amount")
            if column is not None:
                numeric_amounts = pd.to_numeric(
                    current_working_df[column],
                    errors="coerce",
                )
                selected_mask = numeric_amounts < 0

        preview_count = int(selected_mask.sum())
        st.write(f"Rows that would be quarantined: **{preview_count:,}**")

        action_col, reset_col = st.columns(2)
        with action_col:
            apply_remediation = st.button(
                "Apply to working copy & revalidate",
                type="primary",
                disabled=(preview_count == 0),
            )
        with reset_col:
            reset_working_copy = st.button("Reset working copy")

        if apply_remediation:
            before_validation_df = current_working_df.rename(
                columns={
                    actual_names_for_fix[name]: name
                    for name in REQUIRED_TRANSACTION_COLUMNS
                    if name in actual_names_for_fix
                    and actual_names_for_fix[name] != name
                }
            )
            before_findings = validate_transactions(before_validation_df)

            quarantined = current_working_df.loc[selected_mask].copy()
            quarantined["quarantine_reason"] = reason
            existing_quarantine = st.session_state.get(
                "quarantine_records",
                pd.DataFrame(),
            )
            st.session_state["quarantine_records"] = pd.concat(
                [existing_quarantine, quarantined],
                ignore_index=True,
            )

            updated_df = current_working_df.loc[~selected_mask].copy()
            st.session_state["working_df"] = updated_df

            updated_actual_names = {
                str(column).strip().lower(): column
                for column in updated_df.columns
            }
            after_validation_df = updated_df.rename(
                columns={
                    updated_actual_names[name]: name
                    for name in REQUIRED_TRANSACTION_COLUMNS
                    if name in updated_actual_names
                    and updated_actual_names[name] != name
                }
            )
            after_findings = validate_transactions(after_validation_df)

            before_rules = {item["rule"]: item["count"] for item in before_findings}
            after_rules = {item["rule"]: item["count"] for item in after_findings}
            improved_rules = [
                rule
                for rule, count in before_rules.items()
                if count > 0 and after_rules.get(rule, 0) < count
            ]

            audit_entry = {
                "action": reason,
                "rows_quarantined": int(selected_mask.sum()),
                "findings_before": len(before_findings),
                "findings_after": len(after_findings),
                "improved_rules": (
                    ", ".join(improved_rules)
                    if improved_rules
                    else "No rule count decreased"
                ),
            }
            st.session_state["remediation_audit"].append(audit_entry)
            st.rerun()

        if st.button("Reset working copy and clear quarantine/audit"):
            st.session_state["working_df"] = st.session_state["source_df"].copy(deep=True)
            st.session_state["quarantine_records"] = pd.DataFrame()
            st.session_state["remediation_audit"] = []
            st.rerun()

        quarantine_df = st.session_state.get("quarantine_records", pd.DataFrame())
        if not quarantine_df.empty:
            st.subheader("Quarantine review")
            st.write(f"Quarantined rows available for review: **{len(quarantine_df):,}**")
            st.dataframe(quarantine_df, width="stretch", hide_index=True)
            st.download_button(
                "Download quarantine CSV",
                data=quarantine_df.to_csv(index=False).encode("utf-8"),
                file_name="tracewise_quarantine.csv",
                mime="text/csv",
            )

        audit_log = st.session_state.get("remediation_audit", [])
        if audit_log:
            st.subheader("Remediation audit trail")
            audit_df = pd.DataFrame(audit_log)
            st.dataframe(audit_df, width="stretch", hide_index=True)
            st.download_button(
                "Download audit trail CSV",
                data=audit_df.to_csv(index=False).encode("utf-8"),
                file_name="tracewise_remediation_audit.csv",
                mime="text/csv",
            )

        st.info(
            f"Current working copy: {len(st.session_state['working_df']):,} rows. "
            "The source dataset remains unchanged. Reset the working copy to "
            "discard simulated recovery changes."
        )
    else:
        st.warning(
            "Remediation is enabled for datasets matching the transaction schema. "
            "Generic datasets can still be profiled and risk-scored."
        )
        st.write("Missing transaction columns:", sorted(missing_columns))
        st.write("Available columns:", list(df.columns))
