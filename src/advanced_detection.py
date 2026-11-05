
from pathlib import Path
import pandas as pd
import numpy as np


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

RECONCILIATION_PATH = BASE_DIR / "reports" / "initial_reconciliation.csv"
PAYMENTS_PATH = BASE_DIR / "data" / "raw" / "olist_order_payments_dataset.csv"

OUTPUT_PATH = BASE_DIR / "reports" / "advanced_detection_features.csv"


def prepare_features():

    print("Loading original transaction data...")

    reconciliation = pd.read_csv(RECONCILIATION_PATH)
    payments = pd.read_csv(PAYMENTS_PATH)

    # Aggregate individual payment records at order level
    payment_features = payments.groupby("order_id").agg(
        payment_type_count=("payment_type", "nunique"),
        payment_installments_max=("payment_installments", "max"),
        payment_record_count_raw=("payment_sequential", "count"),
        payment_total_raw=("payment_value", "sum")
    ).reset_index()

    # Merge payment features with reconciliation data
    df = reconciliation.merge(
        payment_features,
        on="order_id",
        how="left",
        validate="one_to_one"
    )

    # Handle orders without payment records
    count_columns = [
        "payment_type_count",
        "payment_record_count_raw"
    ]

    df[count_columns] = df[count_columns].fillna(0)

    df["payment_installments_max"] = (
        df["payment_installments_max"].fillna(0)
    )

    # Financial feature engineering
    df["absolute_payment_difference"] = (
        df["payment_difference"].abs()
    )

    df["payment_ratio"] = np.where(
        df["item_plus_freight"] > 0,
        df["payment_total"] / df["item_plus_freight"],
        np.nan
    )

    df["difference_percentage"] = np.where(
        df["item_plus_freight"] > 0,
        (
            df["payment_difference"]
            / df["item_plus_freight"]
        ) * 100,
        np.nan
    )

    # Eligible transactions for the initial anomaly model
    df["eligible_for_model"] = (
        (df["order_status"] == "delivered")
        & (df["has_items"] == True)
        & (df["has_payments"] == True)
        & (df["item_plus_freight"] > 0)
    )

    # Save the enriched dataset
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFEATURE PREPARATION COMPLETED")
    print("--------------------------------")
    print("Total orders:", len(df))
    print("Eligible delivered orders:", df["eligible_for_model"].sum())
    print("Orders excluded from initial model:", (~df["eligible_for_model"]).sum())

    print("\nNew feature columns:")
    print([
        "payment_type_count",
        "payment_installments_max",
        "absolute_payment_difference",
        "payment_ratio",
        "difference_percentage"
    ])

    print("\nSaved file:", OUTPUT_PATH)


if __name__ == "__main__":
    prepare_features()
