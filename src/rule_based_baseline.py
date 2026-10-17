
from pathlib import Path
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    average_precision_score,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "synthetic_scenarios"
    / "controlled_leakage_scenarios.csv"
)

REPORT_DIR = PROJECT_DIR / "reports"


def main():
    print("=" * 65)
    print("RULE-BASED REVENUE LEAKAGE BASELINE")
    print("=" * 65)

    df = pd.read_csv(DATA_PATH)

    # Ground-truth labels from our controlled experiment
    y_true = df["is_synthetic_leakage"].astype(int)

    # Simple reconciliation rule:
    # Flag a record if its simulated payment is below expected revenue.
    tolerance = 1.00  # Ignore differences of ₹/$1 or less

    shortfall = (
        df["expected_total"] - df["simulated_payment"]
    )

    predictions = (shortfall > tolerance).astype(int)

    # Score based on the size of the observed shortfall.
    scores = shortfall.clip(lower=0)

    print("\nTotal records:", len(df))
    print("Actual synthetic cases:", int(y_true.sum()))
    print("Cases flagged by rule:", int(predictions.sum()))

    print("\nClassification report:")
    print(classification_report(
        y_true,
        predictions,
        target_names=["Baseline", "Synthetic leakage"],
        zero_division=0,
    ))

    print("\nConfusion matrix [ [TN, FP], [FN, TP] ]:")
    matrix = confusion_matrix(
        y_true, predictions, labels=[0, 1]
    )
    print(matrix)

    print(
        "\nAverage precision:",
        round(average_precision_score(y_true, scores), 4),
    )

    # Preserve record-level results for investigation.
    df["rule_shortfall"] = shortfall
    df["rule_prediction"] = predictions

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "rule_based_baseline.csv"
    df.to_csv(output_path, index=False)

    print("\nDetailed results saved to:", output_path)
    print(
        "\nNOTE: This evaluates simulated scenarios, "
        "not confirmed real-world leakage."
    )


if __name__ == "__main__":
    main()
