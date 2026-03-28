from src.ingestion import ingest_files
from src.cleaner import clean
import yaml
with open("config/schema_map.yaml", "r") as f:
    config = yaml.safe_load(f)
    df_raw = ingest_files(
    file_paths=[
        'data/raw/clean_data.csv',
        'data/raw/messy_dates.csv',
        'data/raw/missing_fields.csv',
        'data/raw/inconsistent_categories.csv',
        'data/raw/multi_schema.xlsx'
    ],
    config_path='config/schema_map.yaml'
)
df_clean = clean(df_raw, config)
print("Shape:", df_clean.shape)
print("\nColumns:", df_clean.columns.tolist())

print("\nUnique types:", df_clean["type"].unique())
print("\nUnique categories:", df_clean["category"].unique())

print("\nNull counts:\n", df_clean.isnull().sum())

print("\nValid vs Invalid:")
print(df_clean["is_valid"].value_counts())

print("\nSample:")
print(df_clean.head(10))