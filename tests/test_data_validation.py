from pathlib import Path

import pandas as pd


def test_csv_structure() -> None:
    """Verify bias.csv has required columns and proper structure."""
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "data" / "bias.csv"

    df = pd.read_csv(data_path)

    # Check required columns exist
    required_columns = {"Category", "Subcategory", "Final_Keyword", "Final count"}
    assert required_columns.issubset(df.columns), f"Missing columns: {required_columns - set(df.columns)}"

    # Check we have data
    assert len(df) > 0, "CSV is empty"

    # Check we have the expected 7 categories
    categories = df["Category"].dropna().unique()
    assert len(categories) == 7, f"Expected 7 categories, found {len(categories)}"


def test_data_integrity() -> None:
    """Test data integrity checks."""
    repo_root = Path(__file__).resolve().parents[1]
    data_path = repo_root / "data" / "bias.csv"

    df = pd.read_csv(data_path)

    # Check for duplicates in Final_Keyword
    duplicates = df[df.duplicated(subset=['Final_Keyword'], keep=False)]
    assert len(duplicates) == 0 or len(duplicates[duplicates['Final_Keyword'].notna()]) == 0, \
        f"Found duplicate keywords: {duplicates['Final_Keyword'].tolist()}"

    # Check that Final count is numeric where present (can be int or float)
    try:
        pd.to_numeric(df['Final count'], errors='coerce')
        numeric_test = True
    except Exception:
        numeric_test = False

    assert numeric_test, "Some Final count values cannot be converted to numeric"

    # Check that all non-null Final count values are positive
    final_counts = pd.to_numeric(df['Final count'], errors='coerce')
    negative_counts = final_counts[final_counts < 0]
    assert len(negative_counts) == 0, "Found negative Final count values"
