import os
import sys
import glob

def main():

    # Step 1 — Find all raw data files
    file_paths = glob.glob("data/raw/*.csv") + glob.glob("data/raw/*.xlsx")    # Step 2 — Check if files exist
    if len(file_paths) == 0:
        print("ERROR: No files found in data/raw/")
        print("Please add CSV or Excel files and try again.")
        sys.exit(1)

    print("Starting Financial Pipeline...")

    from src.ingestion import ingest_files
    from src.validator import validate
    from src.cleaner import clean
    from src.analyzer import analyze
    from src.insights import generate_insights
    from src.reporter import generate_report
    import yaml

    # Step 3 — Ingest
    df = ingest_files(
        file_paths=file_paths,
        config_path="config/schema_map.yaml"
    )
    print(f"Loaded {len(df)} rows from {len(file_paths)} files")

    # Step 4 — Validate
    flagged_df, summary = validate(df)
    print(f"Validation complete — Stop condition: {summary['stop_condition_triggered']}")

    if summary['stop_condition_triggered']:
        print(f"PIPELINE STOPPED: {summary['stop_reason']}")
        sys.exit(1)

    # Step 5 — Clean
    with open('config/schema_map.yaml', 'r') as f:
        schema = yaml.safe_load(f)

    cleaned_df = clean(flagged_df, schema)
    print(f"Cleaning complete — Valid rows: {cleaned_df['is_valid'].sum()}")

    # Step 6 — Analyze
    results = analyze(cleaned_df)

    # Step 7 — Insights
    insights = generate_insights(results, summary)
    print(f"Insights generated: {len(insights)}")

    # Step 8 — Generate report
    path = generate_report(results, summary, insights)
    print(f"\nReport ready: {path}")
    print("Open in your browser to view.")

if __name__ == "__main__":
    main()