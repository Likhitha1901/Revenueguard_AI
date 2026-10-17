
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"

def load_csv(filename):
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset file: {path}")
    return pd.read_csv(path)

def main():
    print("=" * 65)
    print("REVENUE RECONCILIATION - INITIAL VALIDATION")
    print("=" * 65)

    orders = load_csv("olist_orders_dataset.csv")
    items = load_csv("olist_order_items_dataset.csv")
    payments = load_csv("olist_order_payments_dataset.csv")

    # Check key uniqueness in the orders table
    print("\n1. ORDER ID VALIDATION")
    print("Total order rows:", len(orders))
    print("Unique order IDs:", orders["order_id"].nunique())
    print("Duplicate order IDs:", orders["order_id"].duplicated().sum())

    # Order items: an order may legitimately have multiple items
    print("\n2. ORDER ITEM VALIDATION")
    print("Total item rows:", len(items))
    print("Unique orders with items:", items["order_id"].nunique())
    print("Missing order IDs:", items["order_id"].isna().sum())
    print("Missing item prices:", items["price"].isna().sum())
    print("Missing freight values:", items["freight_value"].isna().sum())

    # Payments: an order may legitimately have multiple payment records
    print("\n3. PAYMENT VALIDATION")
    print("Total payment rows:", len(payments))
    print("Unique orders with payments:", payments["order_id"].nunique())
    print("Missing payment values:", payments["payment_value"].isna().sum())

    # Aggregate each table BEFORE joining, to avoid multiplying amounts
    item_totals = (
        items.groupby("order_id", as_index=False)
        .agg(
            item_price_total=("price", "sum"),
            freight_total=("freight_value", "sum"),
            item_count=("order_item_id", "count"),
        )
    )

    payment_totals = (
        payments.groupby("order_id", as_index=False)
        .agg(
            payment_total=("payment_value", "sum"),
            payment_record_count=("payment_value", "count"),
        )
    )

    # One row per order in each aggregated table
    reconciliation = (
        orders.merge(item_totals, on="order_id", how="left",
                    validate="one_to_one")
        .merge(payment_totals, on="order_id", how="left",
            validate="one_to_one")
    )

    reconciliation["item_price_total"] = reconciliation[
        "item_price_total"
    ].fillna(0)

    reconciliation["freight_total"] = reconciliation[
        "freight_total"
    ].fillna(0)

    reconciliation["payment_total"] = reconciliation[
        "payment_total"
    ].fillna(0)

    reconciliation["item_count"] = reconciliation[
        "item_count"
    ].fillna(0)

    reconciliation["payment_record_count"] = reconciliation[
        "payment_record_count"
    ].fillna(0)

    # This is a screening signal, NOT proof of lost revenue.
    reconciliation["item_plus_freight"] = (
        reconciliation["item_price_total"]
        + reconciliation["freight_total"]
    )

    reconciliation["payment_difference"] = (
        reconciliation["payment_total"]
        - reconciliation["item_plus_freight"]
    )

    reconciliation["has_items"] = reconciliation["item_count"] > 0
    reconciliation["has_payments"] = (
        reconciliation["payment_record_count"] > 0
    )

    # Keep all orders; review the differences in context.
    reconciliation["payment_check"] = "REVIEW"
    reconciliation.loc[
        reconciliation["has_items"] & reconciliation["has_payments"],
        "payment_check"
    ] = "COMPARE"

    # Create reports folder if needed
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = REPORT_DIR / "initial_reconciliation.csv"
    reconciliation.to_csv(output_path, index=False)

    print("\n4. RECONCILIATION SUMMARY")
    print("Orders analyzed:", len(reconciliation))
    print("Orders with items:", int(reconciliation["has_items"].sum()))
    print("Orders with payments:", int(reconciliation["has_payments"].sum()))
    print(
        "Orders requiring initial review:",
        int((reconciliation["payment_check"] == "REVIEW").sum())
    )

    print("\nItem + freight total:",
        round(reconciliation["item_plus_freight"].sum(), 2))
    print("Payment total:",
        round(reconciliation["payment_total"].sum(), 2))

    print("\nReport saved to:", output_path)
    print("\nIMPORTANT: Differences are screening signals, not confirmed leakage.")
    print("Investigate order status, discounts, refunds and payment context.")

if __name__ == "__main__":
    main()
