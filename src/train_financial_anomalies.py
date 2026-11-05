
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "reports" / "advanced_detection_features.csv"
MODEL_PATH = BASE_DIR / "models" / "financial_anomaly_model.joblib"
OUTPUT_PATH = BASE_DIR / "reports" / "financial_anomaly_results.csv"


def train_financial_model():

    print("Loading transaction data...")

    df = pd.read_csv(DATA_PATH)

    data = df[df["eligible_for_model"] == True].copy()

    # Remove insignificant floating-point differences.
    data["clean_payment_difference"] = (
        data["payment_difference"].round(2)
    )

    data["absolute_difference"] = (
        data["clean_payment_difference"].abs()
    )

    data["difference_percentage_clean"] = np.where(
        data["item_plus_freight"] > 0,
        (
            data["clean_payment_difference"]
            / data["item_plus_freight"]
        ) * 100,
        0
    )

    # Focus on financial discrepancy and supporting context.
    features = [
        "absolute_difference",
        "difference_percentage_clean",
        "payment_installments_max",
        "item_count"
    ]

    X = data[features].copy()

    # Reduce skew in absolute financial differences.
    X["absolute_difference"] = np.log1p(
        X["absolute_difference"]
    )

    print("Training financial anomaly model...")

    model = IsolationForest(
        n_estimators=300,
        contamination=0.01,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X)

    predictions = model.predict(X)
    scores = -model.decision_function(X)

    data["financial_anomaly_prediction"] = predictions
    data["financial_anomaly_status"] = np.where(
        predictions == -1,
        "Review",
        "Normal"
    )

    data["financial_anomaly_score"] = scores

    data = data.sort_values(
        "financial_anomaly_score",
        ascending=False
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "features": features
        },
        MODEL_PATH
    )

    data.to_csv(OUTPUT_PATH, index=False)

    flagged = data[
        data["financial_anomaly_prediction"] == -1
    ]

    print("\nEXPERIMENT 2B COMPLETED")
    print("------------------------------")
    print("Eligible transactions:", len(data))
    print("Flagged for review:", len(flagged))
    print(
        "Flagged with difference above ₹1:",
        (flagged["absolute_difference"] > 1).sum()
    )
    print(
        "Flagged with difference above ₹10:",
        (flagged["absolute_difference"] > 10).sum()
    )

    print("\nTop 10 financial anomalies:")

    print(
        data[
            [
                "order_id",
                "clean_payment_difference",
                "difference_percentage_clean",
                "payment_installments_max",
                "financial_anomaly_score",
                "financial_anomaly_status"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nModel saved:", MODEL_PATH)
    print("Results saved:", OUTPUT_PATH)


if __name__ == "__main__":
    train_financial_model()
