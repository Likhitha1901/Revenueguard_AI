
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"


def main():
    print("=" * 65)
    print("REVENUE LEAKAGE INVESTIGATION")
    print("=" * 65)

    # Load the existing one-row-per-order reconciliation report
    report_path = REPORT_DIR / "initial_reconciliation.csv"

    if not report_path.exists():
        raise FileNotFoundError(
            "Run src/reconciliation.py first."
        )

    df = pd.read_csv(report_path)

    # Load order status information
    if "order_status" not in df.columns:
        orders= pd.read_csv(RAW_DIR / "olist_orders_dataset.csv",
        usecols = ["order_id", "order_status"]
        )
        df = df.merge(orders, on="order_id", how="left", validate="one_to_one")
    # Identify the reason each order needs investigation
    df["investigation_reason"] = "No missing-record signal"

    no_items = df["item_count"] == 0
    no_payments = df["payment_record_count"] == 0

    df.loc[no_items & no_payments, "investigation_reason"] = (
        "No item records or payment records"
    )

    df.loc[no_items & ~no_payments, "investigation_reason"] = (
        "Payment exists but item records are missing"
    )

    df.loc[~no_items & no_payments, "investigation_reason"] = (
        "Item records exist but payment records are missing"
    )

    # Payment difference is useful for investigation, but not proof
    df["absolute_payment_difference"] = (
        df["payment_difference"].abs()
    )

    # Rank orders for review without claiming they are confirmed leakage
    review = df[
        (no_items | no_payments)
        & (~df["order_status"].isin(["canceled", "unavailable"]))
    ].copy()

    review = review.sort_values(
        "absolute_payment_difference",
        ascending=False
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    all_path = REPORT_DIR / "orders_with_investigation_reasons.csv"
    review_path = REPORT_DIR / "leakage_review_queue.csv"

    df.to_csv(all_path, index=False)
    review.to_csv(review_path, index=False)

    print("\nTotal orders:", len(df))
    print("Orders with missing item/payment records:", int(
        (no_items | no_payments).sum()
    ))
    print("Orders in initial review queue:", len(review))

    print("\nReview reasons:")
    print(review["investigation_reason"].value_counts().to_string())

    print("\nOrder statuses in review queue:")
    print(review["order_status"].value_counts().to_string())

    print("\nSaved reports:")
    print(all_path)
    print(review_path)

    print(
        "\nNOTE: These are investigation candidates, "
        "not confirmed revenue leakage."
    )


if __name__ == "__main__":
    main()
