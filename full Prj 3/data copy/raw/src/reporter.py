from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os
import yaml

# Always resolve paths from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "schema_map.yaml")

def generate_report(results, quality, insights):

    # Safe template loader
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("report.html")

    # SAFE extraction from results dictionary
    pnl = results.get("pnl", {})
    revenue = results.get("revenue", {}).get("by_category", {})
    expenses = results.get("expenses", {}).get("by_category", {})

    context = {
        "generated_date": datetime.today().strftime("%d %B %Y"),
        "quality": quality,
        "results": results,
        "pnl": pnl,
        "revenue": revenue,
        "expenses": expenses,
        "insights": insights
    }

    html_output = template.render(context)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(
        OUTPUT_DIR,
        f"report_{datetime.today().strftime('%Y%m%d')}.html"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"Report saved: {filename}")
    return filename


if __name__ == "__main__":

    # Import modules only when running the pipeline
    from src.ingestion import ingest_files
    from src.validator import validate
    from src.cleaner import clean
    from src.analyzer import analyze
    from src.insights import generate_insights

    print("Starting Financial Pipeline...")

    # 1) INGEST DATA
    df = ingest_files(
        file_paths=[
            "data/raw/clean_data.csv",
            "data/raw/messy_dates.csv",
            "data/raw/missing_fields.csv",
            "data/raw/inconsistent_categories.csv",
            "data/raw/multi_schema.xlsx"
        ],
        config_path=CONFIG_PATH
    )

    print("Data ingestion completed")

    # 2) VALIDATE
    flagged_df, summary = validate(df)
    print("Validation completed")

    # 3) LOAD SCHEMA
    with open(CONFIG_PATH, "r") as f:
        schema = yaml.safe_load(f)

    # 4) CLEAN
    cleaned_df = clean(flagged_df, schema)
    print("Cleaning completed")

    # 5) ANALYZE
    results = analyze(cleaned_df)
    print("Analysis completed")

    # 6) GENERATE INSIGHTS
    insights = generate_insights(results, summary)
    print("Insights generated")

    # 7) GENERATE REPORT
    path = generate_report(results, summary, insights)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")
    print(f"Open this file in your browser:\n{path}")