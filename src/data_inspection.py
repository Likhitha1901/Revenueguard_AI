
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

def main():
    print("=" * 65)
    print("AI-POWERED REVENUE LEAKAGE DETECTION SYSTEM")
    print("PHASE 1: DATASET INSPECTION")
    print("=" * 65)

    if not RAW_DATA_DIR.exists():
        print(f"ERROR: Dataset folder not found: {RAW_DATA_DIR}")
        return

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("ERROR: No CSV files found in data/raw.")
        print("Please check that you copied the extracted CSV files.")
        return

    print(f"\nCSV files found: {len(csv_files)}")

    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)

            print("\n" + "-" * 65)
            print(f"FILE: {file_path.name}")
            print("-" * 65)
            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns)}")
            print(f"Duplicate rows: {df.duplicated().sum():,}")
            print(f"Missing cells: {df.isna().sum().sum():,}")

            print("\nColumn names:")
            print(", ".join(df.columns.astype(str)))

            missing = df.isna().sum()
            missing = missing[missing > 0]

            if not missing.empty:
                print("\nColumns with missing values:")
                print(missing.sort_values(ascending=False).to_string())
            else:
                print("\nNo missing values found.")

            # Display a small preview without printing the entire dataset
            print("\nFirst 3 rows:")
            print(df.head(3).to_string(index=False))

        except Exception as error:
            print(f"\nCould not inspect {file_path.name}: {error}")

    print("\n" + "=" * 65)
    print("DATASET INSPECTION COMPLETED")
    print("=" * 65)

if __name__ == "__main__":
    main()
