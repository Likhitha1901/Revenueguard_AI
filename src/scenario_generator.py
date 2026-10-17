
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "synthetic_scenarios"


def main():
    print("=" * 65)
    print("CONTROLLED REVENUE LEAKAGE SCENARIO GENERATOR")
    print("=" * 65)

    orders = pd.read_csv(
        RAW_DIR / "olist_orders_dataset.csv"
    )

    items = pd.read_csv(
        RAW_DIR / "olist_order_items_dataset.csv"
    )

    payments = pd.read_csv(
        RAW_DIR / "olist_order_payments_dataset.csv"
    )

    # Build expected item + freight amounts.
    # Aggregate first to avoid multiplying records during joins.
    item_totals = items.groupby("order_id").agg(
        item_total=("price", "sum"),
        freight_total=("freight_value", "sum")
    ).reset_index()

    payment_totals = payments.groupby("order_id").agg(
        payment_total=("payment_value", "sum")
    ).reset_index()

    df = orders[
        ["order_id", "order_status"]
    ].merge(
        item_totals,
        on="order_id",
        how="inner",
        validate="one_to_one"
    ).merge(
        payment_totals,
        on="order_id",
        how="left",
        validate="one_to_one"
    )

    # Restrict initial experiments to delivered orders
    df = df[df["order_status"] == "delivered"].copy()

    df["payment_total"] = df["payment_total"].fillna(0)
    df["expected_total"] = df["item_total"] + df["freight_total"]

    # Exclude zero-value records from percentage-based experiments
    df = df[df["expected_total"] > 0].copy()

    # Baseline: preserve observed data and mark as non-synthetic
    df["scenario_type"] = "baseline"
    df["is_synthetic_leakage"] = 0
    df["simulated_payment"] = df["payment_total"]

    # Reproducible selection of separate cases
    rng = np.random.default_rng(42)

    eligible = df.index.to_numpy(copy=True)
    rng.shuffle(eligible)

    n = min(300, len(eligible))
    underpayment_ids = eligible[:n]

    n2 = min(300, max(0, len(eligible) - n))
    missing_payment_ids = eligible[n:n + n2]

    n3 = min(300, max(0, len(eligible) - n - n2))
    freight_ids = eligible[n + n2:n + n2 + n3]

    # Scenario 1: simulated 10–30% underpayment
    if len(underpayment_ids):
        rates = rng.uniform(0.10, 0.30, len(underpayment_ids))
        df.loc[underpayment_ids, "simulated_payment"] = (
            df.loc[underpayment_ids, "expected_total"].to_numpy()
            * (1 - rates)
        )
        df.loc[underpayment_ids, "scenario_type"] = "underpayment"
        df.loc[underpayment_ids, "is_synthetic_leakage"] = 1

    # Scenario 2: simulated missing payment
    if len(missing_payment_ids):
        df.loc[missing_payment_ids, "simulated_payment"] = 0.0
        df.loc[missing_payment_ids, "scenario_type"] = "missing_payment"
        df.loc[missing_payment_ids, "is_synthetic_leakage"] = 1

    # Scenario 3: simulated freight under-recovery
    if len(freight_ids):
        df.loc[freight_ids, "simulated_payment"] = (
            df.loc[freight_ids, "expected_total"]
            - df.loc[freight_ids, "freight_total"] * 0.5
        )
        df.loc[freight_ids, "scenario_type"] = "freight_under_recovery"
        df.loc[freight_ids, "is_synthetic_leakage"] = 1

    df["simulated_difference"] = (
        df["simulated_payment"] - df["expected_total"]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "controlled_leakage_scenarios.csv"
    df.to_csv(output_path, index=False)

    print("Eligible delivered orders:", len(df))
    print("\nScenario counts:")
    print(df["scenario_type"].value_counts().to_string())

    print("\nSynthetic positive labels:", int(
        df["is_synthetic_leakage"].sum()
    ))

    print("\nSaved to:", output_path)
    print(
        "\nResearch note: these are simulated scenarios, "
        "not confirmed real-world leakage."
    )


if __name__ == "__main__":
    main()
