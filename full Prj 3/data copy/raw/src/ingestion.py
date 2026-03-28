import yaml
import pandas as pd
import os

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def build_alias_lookup(column_aliases):
    lookup = {}
    for standard_col, aliases in column_aliases.items():
        for alias in aliases:
            lookup[alias.lower().strip()] = standard_col
    return lookup

def standardize_columns(df, alias_lookup):
    new_columns = {}
    for col in df.columns:
        key = col.lower().strip()
        new_columns[col] = alias_lookup.get(key, col)
    return df.rename(columns=new_columns)

REQUIRED_COLUMNS = ["date", "amount", "type", "category", "description"]

def ensure_required_columns(df):
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df

def add_metadata(df, source_name, start_id):
    df = df.copy()
    df["source_file"] = source_name
    df["row_id"] = range(start_id, start_id + len(df))
    return df

def ingest_files(file_paths, config_path):
    config = load_config(config_path)
    alias_lookup = build_alias_lookup(config["column_aliases"])

    all_dfs = []
    global_row_id = 0

    for path in file_paths:
        file_name = os.path.basename(path)

        if path.endswith(".csv"):
            df = pd.read_csv(path)

            df = standardize_columns(df, alias_lookup)
            df = ensure_required_columns(df)
            df = add_metadata(df, file_name, global_row_id)

            global_row_id += len(df)
            all_dfs.append(df)

        elif path.endswith(".xlsx"):
            sheets = pd.read_excel(path, sheet_name=None)

            for sheet_name, sheet_df in sheets.items():
                df = standardize_columns(sheet_df, alias_lookup)
                df = ensure_required_columns(df)

                source = f"{file_name}::{sheet_name}"
                df = add_metadata(df, source, global_row_id)

                global_row_id += len(df)
                all_dfs.append(df)

    if not all_dfs:
        raise ValueError("No valid files were processed")

    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df

if __name__ == "__main__":
    df = ingest_files(
        file_paths=[
            'data/raw/clean_data.csv',
            'data/raw/messy_dates.csv',
            'data/raw/missing_fields.csv',
            'data/raw/inconsistent_categories.csv',
            'data/raw/multi_schema.xlsx'
        ],
        config_path='config/schema_map.yaml'
    )

    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Unique sources: {df['source_file'].unique()}")
    print(f"Null counts:\n{df.isnull().sum()}")
    print(f"Row ID range: {df['row_id'].min()} to {df['row_id'].max()}")
    print(df.head(5))