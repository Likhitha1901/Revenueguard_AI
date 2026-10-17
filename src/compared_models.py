
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data" / "synthetic_scenarios" / "controlled_leakage_scenarios.csv"
MODEL = ROOT / "models" / "revenue_leakage_model.joblib"
REPORTS = ROOT / "reports"

FEATURES = [
    "item_total",
    "freight_total",
    "expected_total",
    "payment_total",
    "simulated_payment",
    "simulated_difference",
]


def metrics(name, y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).ravel()

    return {
        "method": name,
        "precision": precision_score(
            y_true, y_pred, zero_division=0
        ),
        "recall": recall_score(
            y_true, y_pred, zero_division=0
        ),
        "f1_score": f1_score(
            y_true, y_pred, zero_division=0
        ),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn),
    }


def main():
    df = pd.read_csv(DATA)
    X = df[FEATURES]
    y = df["is_synthetic_leakage"].astype(int)

    # Reproduce the exact split used in the first model.
    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(MODEL)
    ml_predictions = model.predict(X_test)

    # Simple financial shortfall rule.
    rule_predictions = (
        X_test["expected_total"]
        - X_test["simulated_payment"] > 1.00
    ).astype(int)

    results = pd.DataFrame([
        metrics("Rule-based", y_test, rule_predictions),
        metrics("Random Forest", y_test, ml_predictions),
    ])

    REPORTS.mkdir(parents=True, exist_ok=True)
    output = REPORTS / "model_comparison.csv"
    results.to_csv(output, index=False)

    print("=" * 60)
    print("RULE-BASED VS RANDOM FOREST")
    print("=" * 60)
    print(results.round(4).to_string(index=False))
    print("\nSaved comparison:", output)
    print(
        "\nResearch caution: these are synthetic labels, "
        "and simulated financial features may reveal the labels."
    )


if __name__ == "__main__":
    main()
