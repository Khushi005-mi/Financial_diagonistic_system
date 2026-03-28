import pandas as pd

def clean(df, config):
    """
    Input:
        df → validated DataFrame (with flags)
        config → loaded schema_map.yaml
    Output:
        df → cleaned DataFrame with:
            - normalized fields
            - is_valid column
    """

    # -----------------------------
    # STEP 0 — Copy dataframe
    # -----------------------------
    df = df.copy()

    # -----------------------------
    # STEP 1 — Normalize dates
    # -----------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")  # unparseable → NaT

    # -----------------------------
    # STEP 2 — Normalize type values
    # -----------------------------
    type_lookup = {}
    for canonical_type, variants in config["type_normalization"].items():
        for variant in variants:
            type_lookup[variant.lower().strip()] = canonical_type

    df["type"] = df["type"].astype(str).str.lower().str.strip().map(lambda x: type_lookup.get(x, pd.NA))
    print("Unique types:", df["type"].unique())  # Should only show 'income', 'expense', or NaN

    # -----------------------------
    # STEP 3 — Normalize category values
    # -----------------------------
    category_lookup = {}
    for canonical_cat, variants in config["category_normalization"].items():
        for variant in variants:
            category_lookup[variant.lower().strip()] = canonical_cat

    df["category"] = df["category"].astype(str).str.strip().str.lower().map(lambda x: category_lookup.get(x, pd.NA))
    print("Unique categories:", df["category"].unique())

    # -----------------------------
    # STEP 4 — Normalize amount (make numeric)
    # -----------------------------
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")  # invalid → NaN
    print("Amount range:", df["amount"].min(), "to", df["amount"].max())

    # -----------------------------
    # STEP 5 — Create is_valid column
    # -----------------------------
    invalid_mask = (
        df["date"].isna() |
        df["amount"].isna() |
        df["type"].isna()
    )
    df["is_valid"] = ~invalid_mask  # True if valid, False if invalid
    print(df[["date", "amount", "type", "category", "is_valid"]].head(10))

    # -----------------------------
    # STEP 6 — Return cleaned df
    # -----------------------------
    return df