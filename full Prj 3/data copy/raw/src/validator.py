import pandas as pd

def validate(df):
    df = df.copy()

    # -------------------------------------------------
    # CRITICAL FIX — enforce schema BEFORE validation
    # -------------------------------------------------
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["type"] = df["type"].astype(str).str.lower().str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    # -------------------------------------------------
    # Flags
    # -------------------------------------------------
    df["missing_date"] = df["date"].isna()
    df["missing_amount"] = df["amount"].isna()
    df["missing_type"] = df["type"].isin(["nan", "none", ""])
    df["missing_category"] = df["category"].isin(["nan", "none", ""])

    df["duplicate_flag"] = df.duplicated(
        subset=["date", "amount", "type", "source_file"]
    )

    df["invalid_amount_flag"] = (
        (df["amount"].isna()) |
        (df["amount"] <= 0)
    )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------
    total_rows = len(df)
    missing_type_pct = df["missing_type"].mean()
    missing_amount_pct = df["missing_amount"].mean()
    missing_category_pct = df["missing_category"].mean()
    duplicate_count = df["duplicate_flag"].sum()
    invalid_amount_count = df["invalid_amount_flag"].sum()

    # -------------------------------------------------
    # Stop conditions
    # -------------------------------------------------
    stop_condition_triggered = False
    stop_reason = None

    if missing_type_pct > 0.30:
        stop_condition_triggered = True
        stop_reason = f"Missing type exceeds 30%: {missing_type_pct:.1%}"

    elif missing_amount_pct > 0.10:
        stop_condition_triggered = True
        stop_reason = f"Missing amount exceeds 10%: {missing_amount_pct:.1%}"

    elif (invalid_amount_count / total_rows) > 0.40:
        stop_condition_triggered = True
        stop_reason = "Invalid rows exceed 40%"

    quality_summary = {
        "total_rows": int(total_rows),
        "missing_type_pct": round(float(missing_type_pct), 4),
        "missing_amount_pct": round(float(missing_amount_pct), 4),
        "missing_category_pct": round(float(missing_category_pct), 4),
        "duplicate_count": int(duplicate_count),
        "invalid_amount_count": int(invalid_amount_count),
        "stop_condition_triggered": stop_condition_triggered,
        "stop_reason": stop_reason
    }

    return df, quality_summary


if __name__ == "__main__":
    print("Validator module loaded successfully")