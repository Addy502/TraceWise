"""Deterministic validation rules for transaction-shaped datasets.

The four columns below define the minimum transaction schema used by TraceWise.
Additional columns (for example currency, merchant_category, or status) are
permitted but are not mandatory.
"""

import pandas as pd


REQUIRED_COLUMNS = [
    "transaction_id",
    "account_id",
    "transaction_date",
    "amount",
]


def validate_transactions(df: pd.DataFrame) -> list[dict]:
    """Run deterministic data-quality checks on a transactions DataFrame."""
    findings = []

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        findings.append({
            "rule": "SCHEMA_MISSING_COLUMNS",
            "severity": "Critical",
            "column": ", ".join(missing_columns),
            "count": len(missing_columns),
            "message": "Required columns are missing: " + ", ".join(missing_columns),
        })

    # Run only checks whose required input columns are available.
    if "transaction_id" in df.columns:
        duplicate_mask = (
            df["transaction_id"].notna()
            & df["transaction_id"].duplicated(keep=False)
        )
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count:
            findings.append({
                "rule": "DUPLICATE_TRANSACTION_IDS",
                "severity": "High",
                "column": "transaction_id",
                "count": duplicate_count,
                "message": (
                    f"{duplicate_count} rows belong to duplicated transaction IDs."
                ),
            })

    for column in ("transaction_id", "account_id", "amount"):
        if column in df.columns:
            missing_count = int(df[column].isna().sum())
            if missing_count:
                findings.append({
                    "rule": "MISSING_REQUIRED_VALUES",
                    "severity": "High" if column == "transaction_id" else "Medium",
                    "column": column,
                    "count": missing_count,
                    "message": f"{missing_count} rows have missing values in '{column}'.",
                })

    if "amount" in df.columns:
        amount = pd.to_numeric(df["amount"], errors="coerce")
        negative_count = int((amount < 0).sum())
        if negative_count:
            findings.append({
                "rule": "NEGATIVE_TRANSACTION_AMOUNT",
                "severity": "High",
                "column": "amount",
                "count": negative_count,
                "message": f"{negative_count} transactions have negative amounts.",
            })

    if "transaction_date" in df.columns:
        parsed_dates = pd.to_datetime(df["transaction_date"], errors="coerce")
        invalid_count = int(parsed_dates.isna().sum())
        if invalid_count:
            findings.append({
                "rule": "INVALID_TRANSACTION_DATE",
                "severity": "Medium",
                "column": "transaction_date",
                "count": invalid_count,
                "message": f"{invalid_count} rows have missing or invalid dates.",
            })

    return findings
