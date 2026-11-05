
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "reports" / "advanced_detection_features.csv"
MODEL_PATH = BASE_DIR / "models" / "isolation_forest_model.joblib"
OUTPUT_PATH = BASE_DIR / "reports" / "advanced_anomaly_results.csv"


def train_advanced_model():

    print("Loading advanced detection features...")

    df = pd.read_csv(DATA_PATH)

    # Use only eligible delivered transactions
    data = df[df["eligible_for_model"] == True].copy()

    # Select independent financial and transaction features
    features = [
        "item_price_total",
        "freight_total",
        "payment_total",
        "item_count",
        "payment_type_count",
        "payment_installments_max",
        "payment_ratio"
    ]

    X = data[features].copy()

    # Reduce skew in financial amount features
    amount_features = [
        "item_price_total",
        "freight_total",
        "payment_total"
    ]

    for column in amount_features:
        X[column] = np.log1p(X[column])

    print("Training Isolation Forest...")

    model = IsolationForest(
        n_estimators=300,
        contamination=0.01,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X)

    # Isolation Forest: -1 = anomaly, 1 = normal
    predictions = model.predict(X)

    # Higher score means more unusual
    anomaly_scores = -model.decision_function(X)

    data["anomaly_prediction"] = predictions
    data["anomaly_status"] = np.where(
        predictions == -1,
        "Anomaly",
        "Normal"
    )

    data["anomaly_score"] = anomaly_scores

    # Rank most unusual transactions first
    data = data.sort_values(
        "anomaly_score",
        ascending=False
    )

    # Save model and results
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "features": features,
            "amount_features": amount_features
        },
        MODEL_PATH
    )

    data.to_csv(OUTPUT_PATH, index=False)

    print("\nEXPERIMENT 2 COMPLETED")
    print("------------------------------")
    print("Total eligible orders:", len(data))
    print("Detected anomalies:", (predictions == -1).sum())
    print("Normal orders:", (predictions == 1).sum())

    print("\nTop 10 unusual transactions:")

    print(
        data[
            [
                "order_id",
                "payment_difference",
                "payment_ratio",
                "payment_installments_max",
                "anomaly_score",
                "anomaly_status"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nModel saved:", MODEL_PATH)
    print("Results saved:", OUTPUT_PATH)


if __name__ == "__main__":
    train_advanced_model()
