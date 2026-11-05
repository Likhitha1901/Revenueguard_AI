
from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR / "reports" / "financial_anomaly_results.csv"
)

OUTPUT_PATH = (
    BASE_DIR / "reports" / "financial_case_classification.csv"
)


def classify_cases():

    print("Loading financial anomaly results...")

    df = pd.read_csv(INPUT_PATH)

    # Remove insignificant floating-point differences
    df["clean_payment_difference"] = (
        df["payment_difference"].round(2)
    )

    tolerance = 1.00

    # Classify each transaction
    conditions = [
        df["clean_payment_difference"] < -tolerance,

        df["clean_payment_difference"] > tolerance,

        (
            (df["financial_anomaly_prediction"] == -1)
            & (
                df["clean_payment_difference"].abs()
                <= tolerance
            )
        )
    ]

    categories = [
        "Potential Underpayment",
        "Potential Overpayment",
        "Behavioural Anomaly"
    ]

    df["financial_case_type"] = np.select(
        conditions,
        categories,
        default="Normal"
    )

    # Assign investigation priority
    priority_conditions = [
        df["financial_case_type"] == "Potential Underpayment",
        df["financial_case_type"] == "Potential Overpayment",
        df["financial_case_type"] == "Behavioural Anomaly"
    ]

    priority_values = [
        "High",
        "Medium",
        "Low"
    ]

    df["investigation_priority"] = np.select(
        priority_conditions,
        priority_values,
        default="None"
    )

    # Sort investigation cases before normal transactions
    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
        "None": 4
    }

    df["priority_order"] = (
        df["investigation_priority"].map(priority_order)
    )

    df = df.sort_values(
        ["priority_order", "financial_anomaly_score"],
        ascending=[True, False]
    )

    # Save classified results
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nFINANCIAL CLASSIFICATION COMPLETED")
    print("----------------------------------")

    print("\nCase category counts:")

    print(
        df["financial_case_type"]
        .value_counts()
        .to_string()
    )

    print("\nInvestigation priority counts:")

    print(
        df["investigation_priority"]
        .value_counts()
        .to_string()
    )

    print("\nSaved:", OUTPUT_PATH)


if __name__ == "__main__":
    classify_cases()
