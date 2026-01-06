import pandas as pd
import numpy as np
from pathlib import Path


def clean_zero_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace clinically impossible zero values with NaN.
    """
    df = df.copy()
    zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    df[zero_cols] = df[zero_cols].replace(0, np.nan)
    return df


def add_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a synthetic date column to enable trend analysis.
    """
    df = df.copy()
    df["date"] = pd.date_range(start="2018-01-01", periods=len(df), freq="D")
    return df


def add_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a simple risk score based on clinical variables.
    """
    df = df.copy()
    df["risk_score"] = (
        df["Glucose"].fillna(df["Glucose"].median()) * 0.4 +
        df["BMI"].fillna(df["BMI"].median()) * 0.3 +
        df["Age"] * 0.3
    )
    return df


def add_alert_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create alert columns based on clinical thresholds.
    """
    df = df.copy()
    df["high_glucose_flag"] = df["Glucose"].apply(lambda x: 1 if x > 180 else 0)
    df["obese_flag"] = df["BMI"].apply(lambda x: 1 if x >= 30 else 0)
    df["high_risk_flag"] = df["risk_score"].apply(lambda x: 1 if x > df["risk_score"].quantile(0.75) else 0)
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full transformation pipeline: clean, enrich, add dates, risk scores, alerts.
    """
    df = clean_zero_values(df)
    df = add_date_column(df)
    df = add_risk_score(df)
    df = add_alert_flags(df)
    return df


def main():
    raw_path = Path("data/raw/diabetes_raw.csv")
    df = pd.read_csv(raw_path)

    processed_df = transform_data(df)

    print("Transformation successful! New columns:")
    print(processed_df.head())


if __name__ == "__main__":
    main()