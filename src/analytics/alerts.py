import pandas as pd
from pathlib import Path


PROCESSED_PATH = Path("data/processed/diabetes_processed.csv")
ALERT_LOG_PATH = Path("data/processed/alerts_log.csv")


def load_processed_data(path: Path = PROCESSED_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Processed file not found at: {path.resolve()}")
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def build_daily_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate patient-level data to daily trends for alerting.
    """
    df = df.sort_values("date").set_index("date")

    daily = df.resample("D").agg(
        avg_glucose=("Glucose", "mean"),
        avg_bmi=("BMI", "mean"),
        avg_risk_score=("risk_score", "mean"),
        diabetes_rate=("Outcome", "mean"),
        high_glucose_rate=("high_glucose_flag", "mean"),
        high_risk_rate=("high_risk_flag", "mean"),
        obese_rate=("obese_flag", "mean"),
        patient_count=("Id", "count"),
    )

    daily = daily.dropna(subset=["avg_glucose", "avg_risk_score"], how="all")
    return daily


def rule_high_glucose_rate(daily: pd.DataFrame, threshold: float = 0.30) -> pd.DataFrame:
    """
    Alert when more than `threshold` proportion of patients have high glucose.
    """
    mask = daily["high_glucose_rate"] > threshold

    alerts = daily.loc[mask].copy()
    alerts["rule_name"] = "HIGH_GLUCOSE_RATE"
    alerts["severity"] = "HIGH"
    alerts["message"] = (
        "High glucose rate exceeded threshold "
        f"({threshold:.0%}); current={alerts['high_glucose_rate'].round(3)}"
    )

    return alerts[["rule_name", "severity", "message"]]


def rule_risk_score_spike(daily: pd.DataFrame, window: int = 7, delta: float = 8.0) -> pd.DataFrame:
    """
    Alert when avg_risk_score jumps more than `delta` above the rolling mean.
    """
    daily = daily.copy()
    daily["risk_score_ma"] = daily["avg_risk_score"].rolling(window=window, min_periods=window).mean()
    daily["risk_score_spike"] = daily["avg_risk_score"] - daily["risk_score_ma"]

    mask = daily["risk_score_spike"] > delta

    alerts = daily.loc[mask].copy()
    alerts["rule_name"] = "RISK_SCORE_SPIKE"
    alerts["severity"] = "MEDIUM"
    alerts["message"] = (
        "Average risk score spiked more than "
        f"{delta} above {window}-day moving average."
    )

    return alerts[["rule_name", "severity", "message"]]


def rule_diabetes_rate_high(daily: pd.DataFrame, threshold: float = 0.45) -> pd.DataFrame:
    """
    Alert when daily diabetes rate (Outcome=1) is unusually high.
    """
    mask = daily["diabetes_rate"] > threshold

    alerts = daily.loc[mask].copy()
    alerts["rule_name"] = "DIABETES_RATE_HIGH"
    alerts["severity"] = "MEDIUM"
    alerts["message"] = (
        "Daily diabetes rate exceeded threshold "
        f"({threshold:.0%})."
    )

    return alerts[["rule_name", "severity", "message"]]


def combine_alerts(daily: pd.DataFrame) -> pd.DataFrame:
    """
    Run all alert rules and combine them into a single log.
    """
    alerts_list = []

    high_glucose_alerts = rule_high_glucose_rate(daily)
    alerts_list.append(high_glucose_alerts)

    risk_spike_alerts = rule_risk_score_spike(daily)
    alerts_list.append(risk_spike_alerts)

    diabetes_rate_alerts = rule_diabetes_rate_high(daily)
    alerts_list.append(diabetes_rate_alerts)

    # Concatenate all alerts
    all_alerts = pd.concat(alerts_list, axis=0)
    all_alerts = all_alerts.sort_index()

    # Turn index (date) into a column
    all_alerts = all_alerts.reset_index().rename(columns={"index": "date"})

    # Add an alert_id
    all_alerts.insert(0, "alert_id", range(1, len(all_alerts) + 1))

    return all_alerts


def save_alert_log(alerts: pd.DataFrame, path: Path = ALERT_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    alerts.to_csv(path, index=False)
    print(f"✅ Alert log saved to: {path}")


def main():
    # 1. Load processed patient-level data
    df = load_processed_data()

    # 2. Build daily trend table
    daily = build_daily_trends(df)

    # 3. Generate alerts
    alerts = combine_alerts(daily)

    # 4. Save & show a preview
    save_alert_log(alerts)
    print("\n🔔 Sample alerts:")
    print(alerts.head())


if __name__ == "__main__":
    main()