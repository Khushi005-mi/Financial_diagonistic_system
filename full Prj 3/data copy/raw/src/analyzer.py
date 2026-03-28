import pandas as pd

def analyze(df: pd.DataFrame) -> dict:
    """
    Perform business analysis on cleaned dataframe.
    Returns structured dictionary used by insights + report engine.
    """

    # Step 1 — keep only valid rows
    df = df[df["is_valid"] == True].copy()

    # Step 2 — ensure date column is datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Step 3 — create month column
    df["month"] = df["date"].dt.to_period("M")

    # Step 4 — split income vs expenses
    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]

    # -----------------------------
    # Revenue Metrics
    # -----------------------------
    total_revenue = income_df["amount"].sum()

    revenue_by_category = (
        income_df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    top_3_revenue = dict(list(revenue_by_category.items())[:3])

    monthly_revenue = (
        income_df.groupby("month")["amount"]
        .sum()
        .astype(float)
        .to_dict()
    )

    # -----------------------------
    # Expense Metrics
    # -----------------------------
    total_expenses = expense_df["amount"].sum()

    expenses_by_category = (
        expense_df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    top_3_expenses = dict(list(expenses_by_category.items())[:3])

    monthly_expenses = (
        expense_df.groupby("month")["amount"]
        .sum()
        .astype(float)
        .to_dict()
    )

    # -----------------------------
    # Profit & Loss
    # -----------------------------
    net_profit = total_revenue - total_expenses

    margin_pct = (
        (net_profit / total_revenue) * 100
        if total_revenue != 0 else 0
    )

    # -----------------------------
    # FINAL STRUCTURED OUTPUT
    # -----------------------------
    return {
        "revenue": {
            "total": float(total_revenue),
            "by_category": revenue_by_category,
            "top_3": top_3_revenue,
            "monthly": monthly_revenue
        },
        "expenses": {
            "total": float(total_expenses),
            "by_category": expenses_by_category,
            "top_3": top_3_expenses,
            "monthly": monthly_expenses
        },
        "pnl": {
            "net": float(net_profit),
            "margin_pct": float(margin_pct)
        }
    }