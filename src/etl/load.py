import pandas as pd
from pathlib import Path


def load_data(df: pd.DataFrame, output_path="data/processed/diabetes_processed.csv"):
    """
    Save the transformed DataFrame to the processed data directory.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Processed data saved to {output_path}")


def main():
    # Read transformed data from transform.py output
    from transform import transform_data
    raw_df = pd.read_csv("data/raw/diabetes_raw.csv")
    processed_df = transform_data(raw_df)

    load_data(processed_df)


if __name__ == "__main__":
    main()