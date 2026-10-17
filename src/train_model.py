
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    average_precision_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "synthetic_scenarios"
    / "controlled_leakage_scenarios.csv"
)
MODEL_DIR = PROJECT_DIR / "models"
REPORT_DIR = PROJECT_DIR / "reports"

FEATURES = [
    "item_total",
    "freight_total",
    "expected_total",
    "payment_total",
    "simulated_payment",
    "simulated_difference",
]


def main():
    print("=" * 65)
    print("REVENUE LEAKAGE DETECTION - FIRST MODEL")
    print("=" * 65)

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Scenario dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + ["is_synthetic_leakage"]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X = df[FEATURES].replace([np.inf, -np.inf], np.nan)
    y = df["is_synthetic_leakage"].astype(int)

    if y.nunique() != 2:
        raise ValueError("The dataset must contain both classes.")

    # Stratification preserves the class ratio in both splits.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\nDataset summary")
    print("Total records:", len(df))
    print("Training records:", len(X_train))
    print("Test records:", len(X_test))
    print("Synthetic positive cases:", int(y.sum()))
    print("Baseline cases:", int((y == 0).sum()))

    print("\nClassification report")
    print(classification_report(
        y_test,
        predictions,
        target_names=["Baseline", "Synthetic leakage"],
        zero_division=0,
    ))

    print("Confusion matrix [ [TN, FP], [FN, TP] ]:")
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    print(matrix)

    print(
        "ROC-AUC:",
        round(roc_auc_score(y_test, probabilities), 4),
    )
    print(
        "Average precision:",
        round(average_precision_score(y_test, probabilities), 4),
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_DIR / "revenue_leakage_model.joblib")

    metrics = {
        "records": int(len(df)),
        "positive_cases": int(y.sum()),
        "train_records": int(len(X_train)),
        "test_records": int(len(X_test)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "average_precision": float(
            average_precision_score(y_test, probabilities)
        ),
        "confusion_matrix": matrix.tolist(),
    }

    with open(
        REPORT_DIR / "initial_model_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=2)

    print("\nModel saved to models/revenue_leakage_model.joblib")
    print("Metrics saved to reports/initial_model_metrics.json")
    print("\nNOTE: These metrics evaluate synthetic scenarios only.")


if __name__ == "__main__":
    main()
