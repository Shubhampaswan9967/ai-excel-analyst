
import pandas as pd
import numpy as np


# ----------------------------------
# 1. TEXT CLEANING
# ----------------------------------

def clean_text(df):

    df = df.copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:

        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

        df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)

    return df


# ----------------------------------
# 2. DUPLICATE REMOVAL
# ----------------------------------

def remove_duplicates(df):

    df = df.copy()

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    return df, removed


# ----------------------------------
# 3. MISSING VALUE HANDLING
# ----------------------------------

def handle_missing_values(
    df,
    numeric_strategy="median",
    categorical_strategy="mode"
):

    df = df.copy()

    changes = {}

    for col in df.columns:

        missing_count = int(df[col].isna().sum())

        if missing_count == 0:
            continue

        # Numeric columns

        if pd.api.types.is_numeric_dtype(df[col]):

            if numeric_strategy == "median":

                fill_value = df[col].median()

            elif numeric_strategy == "mean":

                fill_value = df[col].mean()

            elif numeric_strategy == "zero":

                fill_value = 0

            else:
                continue

            if pd.notna(fill_value):

                df[col] = df[col].fillna(fill_value)

                changes[col] = missing_count

        # Categorical columns

        else:

            if categorical_strategy == "mode":

                modes = df[col].mode(dropna=True)

                if not modes.empty:

                    fill_value = modes.iloc[0]

                else:

                    fill_value = None

            elif categorical_strategy == "unknown":

                fill_value = "Unknown"

            else:

                continue

            if fill_value is not None:

                df[col] = df[col].fillna(fill_value)

                changes[col] = missing_count

    return df, changes


# ----------------------------------
# 4. DATA TYPE CONVERSION
# ----------------------------------

def convert_column_type(df, column, target_type):

    df = df.copy()

    before_missing = int(df[column].isna().sum())

    if target_type == "Numeric":

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    elif target_type == "Datetime":

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    new_missing = int(df[column].isna().sum())

    conversion_failures = max(
        0,
        new_missing - before_missing
    )

    return df, conversion_failures


# ----------------------------------
# 5. OUTLIER DETECTION
# ----------------------------------

def detect_outliers(df):

    results = []

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for col in numeric_columns:

        series = df[col].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)

        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_limit = q1 - 1.5 * iqr

        upper_limit = q3 + 1.5 * iqr

        outliers = (
            (series < lower_limit) |
            (series > upper_limit)
        ).sum()

        results.append({

            "Column": col,

            "Outliers": int(outliers),

            "Lower Limit": round(lower_limit, 2),

            "Upper Limit": round(upper_limit, 2)

        })

    return pd.DataFrame(results)


# ----------------------------------
# 6. COMPLETE CLEANING ENGINE
# ----------------------------------

def clean_dataset(
    df,
    numeric_strategy,
    categorical_strategy,
    remove_duplicate,
    conversion_column=None,
    target_type=None
):

    original_df = df.copy()

    # Clean text

    cleaned_df = clean_text(original_df)

    conversion_failures = 0

    if conversion_column and target_type:

        cleaned_df, conversion_failures = convert_column_type(
            cleaned_df,
            conversion_column,
            target_type
        )
    # Remove duplicates

    duplicate_count = 0

    if remove_duplicate:

        cleaned_df, duplicate_count = remove_duplicates(
            cleaned_df
        )

    # Handle missing values

    cleaned_df, missing_changes = handle_missing_values(
        cleaned_df,
        numeric_strategy,
        categorical_strategy
    )

    # Detect outliers (report only)

    outliers = detect_outliers(cleaned_df)

    # Cleaning summary

    summary = {

        "original_rows": len(original_df),

        "cleaned_rows": len(cleaned_df),

        "duplicates_removed": duplicate_count,

        "missing_values_filled": sum(
            missing_changes.values()
        ),

        "remaining_missing": int(
            cleaned_df.isna().sum().sum()
        ),

        "conversion_failures": conversion_failures


    }

    return cleaned_df, summary, outliers
