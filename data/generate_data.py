
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

# Save the dataset in the project's data folder.
OUTPUT_FILE = Path(__file__).with_name("demo_transactions.csv")

merchant_categories = [
    "Groceries",
    "Travel",
    "Fuel",
    "Shopping",
    "Restaurants",
    "Utilities",
]

statuses = ["completed", "pending", "failed"]

rows = []
start_date = datetime(2026, 1, 1)

# Generate 1,000 synthetic transactions.
for i in range(1, 1001):
    transaction_date = start_date + timedelta(
        minutes=random.randint(0, 60 * 24 * 90)
    )

    rows.append(
        {
            "transaction_id": f"TXN{i:05d}",
            "account_id": f"ACC{random.randint(1000, 1099)}",
            "transaction_date": transaction_date.isoformat(
                timespec="seconds"
            ),
            "amount": round(random.uniform(50, 25000), 2),
            "currency": "INR",
            "merchant_category": random.choice(merchant_categories),
            "status": random.choice(statuses),
        }
    )

df = pd.DataFrame(rows)

# Inject known data-quality defects.
# 1. Duplicate transaction IDs.
df.loc[100, "transaction_id"] = df.loc[99, "transaction_id"]
df.loc[250, "transaction_id"] = df.loc[249, "transaction_id"]

# 2. Missing transaction amounts.
df.loc[400, "amount"] = None
df.loc[401, "amount"] = None

# 3. Invalid negative transaction amounts.
df.loc[600, "amount"] = -500.00
df.loc[601, "amount"] = -125.00

# 4. Missing account ID.
df.loc[700, "account_id"] = None

df.to_csv(OUTPUT_FILE, index=False)

print(f"Dataset created: {OUTPUT_FILE}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("Injected defects:")
print("- 2 duplicate transaction IDs")
print("- 2 missing amounts")
print("- 2 negative amounts")
print("- 1 missing account ID")
