import pandas as pd
from pathlib import Path


def extract_data(csv_path: Path | str = "data/raw/diabetes_raw.csv") -> pd.DataFrame:
    """
    Read the raw diabetes CSV file into a pandas DataFrame.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find file at: {csv_path.resolve()}")

    df = pd.read_csv(csv_path)
    return df


def quick_data_check(df: pd.DataFrame) -> None:
    """
    Print basic info about the dataset to understand its structure and quality.
    """
    print("✅ Data loaded successfully")
    print("-" * 60)
    print(f"Shape (rows, columns): {df.shape}")
    print("-" * 60)
    print("📌 Columns and dtypes:")
    print(df.dtypes)
    print("-" * 60)
    print("🔎 First 5 rows:")
    print(df.head())
    print("-" * 60)
    print("🧱 Missing values per column:")
    print(df.isna().sum())
    print("-" * 60)

    # Many medical datasets use 0 as “missing” for some fields – let’s inspect that.
    zero_counts = (df == 0).sum()
    print("🩺 Zero values per column (may indicate missing for some clinical fields):")
    print(zero_counts)
    print("-" * 60)

    if "Outcome" in df.columns:
        print("⚖ Outcome value counts:")
        print(df["Outcome"].value_counts())
        print("-" * 60)


def main():
    df = extract_data()
    quick_data_check(df)


if __name__ == "__main__":
    main()