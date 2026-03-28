import pandas as pd

# ─────────────────────────────────────────
# RULE 3 — Data Quality Risk
# ─────────────────────────────────────────

def check_data_quality_risk(quality_summary: dict):
    """
    If missing type OR category > 30% → return insight
    """
    missing_type_pct = quality_summary.get("missing_type_pct", 0)
    missing_category_pct = quality_summary.get("missing_category_pct", 0)

    if missing_type_pct > 0.30 or missing_category_pct > 0.30:
        return {
            "rule": "data_quality_risk",
            "severity": "high",
            "message": "Data quality risk detected. Large percentage of missing fields.",
            "details": {
                "missing_type_pct": missing_type_pct,
                "missing_category_pct": missing_category_pct,
            }
        }
    return None


# ─────────────────────────────────────────
# RULE 1 — Expense Spike Detection
# ─────────────────────────────────────────

def check_expense_by_category(analyzer_output: dict):
    """
    Detect >25% month-over-month spike in expenses per category
    Returns LIST of insights
    """

    monthly_expenses = analyzer_output.get("monthly_expenses", {})
    insights = []

    months = sorted(monthly_expenses.keys())

    for i in range(1, len(months)):
        prev_month = months[i - 1]
        curr_month = months[i]

        prev_data = monthly_expenses.get(prev_month, {})
        curr_data = monthly_expenses.get(curr_month, {})

        for category in curr_data:
            if category in prev_data and prev_data[category] > 0:
                prev_val = prev_data[category]
                curr_val = curr_data[category]

                pct_change = (curr_val - prev_val) / prev_val

                if pct_change > 0.25:
                    insights.append({
                        "rule": "expense_spike",
                        "severity": "medium",
                        "message": f"{category} expenses increased {pct_change:.2%} from {prev_month} to {curr_month}",
                        "details": {
                            "category": category,
                            "previous_month": prev_month,
                            "current_month": curr_month,
                            "previous_value": prev_val,
                            "current_value": curr_val,
                            "pct_change": pct_change
                        }
                    })

    return insights


# ─────────────────────────────────────────
# RULE 2 — Revenue Drop Detection
# ─────────────────────────────────────────

def check_revenue_drop(analyzer_output: dict):
    """
    Detect >20% revenue drop month-over-month
    """

    monthly_revenue = analyzer_output.get("monthly_revenue", {})
    months = sorted(monthly_revenue.keys())

    for i in range(1, len(months)):
        prev_month = months[i - 1]
        curr_month = months[i]

        prev_rev = monthly_revenue[prev_month]
        curr_rev = monthly_revenue[curr_month]

        if prev_rev > 0:
            pct_change = (curr_rev - prev_rev) / prev_rev

            if pct_change < -0.20:
                return {
                    "rule": "revenue_drop",
                    "severity": "high",
                    "message": f"Revenue dropped {pct_change:.2%} from {prev_month} to {curr_month}",
                    "details": {
                        "previous_month": prev_month,
                        "current_month": curr_month,
                        "previous_revenue": prev_rev,
                        "current_revenue": curr_rev,
                        "pct_change": pct_change
                    }
                }

    return None


# ─────────────────────────────────────────
# MAIN FUNCTION — Generate All Insights
# ─────────────────────────────────────────

def generate_insights(analyzer_output: dict, quality_summary: dict):
    """
    Run all rules and return list of insights
    """

    insights = []

    # Rule 3 — Data quality
    quality_risk = check_data_quality_risk(quality_summary)
    if quality_risk:
        insights.append(quality_risk)

    # Rule 1 — Expense spikes
    spikes = check_expense_by_category(analyzer_output)
    insights.extend(spikes)

    # Rule 2 — Revenue drop
    revenue_drop = check_revenue_drop(analyzer_output)
    if revenue_drop:
        insights.append(revenue_drop)

    return insights


# ─────────────────────────────────────────
# TEST BLOCK
# ─────────────────────────────────────────

if __name__ == "__main__":

    # Fake sample data so file runs independently
    quality_summary = {
        "missing_type_pct": 0.35,
        "missing_category_pct": 0.10
    }

    analyzer_output = {
        "monthly_revenue": {
            "2024-01": 10000,
            "2024-02": 7000
        },
        "monthly_expenses": {
            "2024-01": {"Food": 2000, "Travel": 1000},
            "2024-02": {"Food": 3000, "Travel": 1100}
        }
    }

    insights = generate_insights(analyzer_output, quality_summary)

    print(f"\nTotal insights generated: {len(insights)}")
    for i, insight in enumerate(insights):
        print(f"\nInsight {i+1}:")
        print(f"  Rule: {insight['rule']}")
        print(f"  Severity: {insight['severity']}")
        print(f"  Message: {insight['message']}")