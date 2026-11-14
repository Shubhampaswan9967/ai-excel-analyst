
import pandas as pd
import numpy as np


def get_analysis_summary(df):

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(numeric_columns),
        "categorical_columns": len(categorical_columns),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }

    return summary


def get_numeric_analysis(df):

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numeric_columns:
        return pd.DataFrame()

    result = df[numeric_columns].describe().T

    result = result.reset_index()

    result = result.rename(
        columns={"index": "Column"}
    )

    return result.round(2)


def get_categorical_analysis(df):

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    results = []

    for col in categorical_columns:

        results.append({
            "Column": col,
            "Unique Values": df[col].nunique(),
            "Most Frequent": (
                df[col].mode().iloc[0]
                if not df[col].mode().empty
                else "N/A"
            ),
            "Frequency": (
                int(df[col].value_counts().iloc[0])
                if not df[col].value_counts().empty
                else 0
            )
        })

    return pd.DataFrame(results)


def get_top_values(df, column, top_n=5):

    if column not in df.columns:
        return pd.DataFrame()

    result = (
        df[column]
        .value_counts()
        .head(top_n)
        .reset_index()
    )

    result.columns = [column, "Count"]

    return result


def get_correlation_analysis(df):

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] < 2:
        return pd.DataFrame()

    return numeric_df.corr().round(2)


def generate_business_insights(df):

    insights = []

    insights.append(
        f"Dataset contains {len(df)} rows and {len(df.columns)} columns."
    )

    missing = int(df.isnull().sum().sum())

    if missing > 0:
        insights.append(
            f"Dataset has {missing} missing values. "
            "Further cleaning may be required."
        )
    else:
        insights.append(
            "No missing values found in the dataset."
        )

    duplicates = int(df.duplicated().sum())

    if duplicates > 0:
        insights.append(
            f"{duplicates} duplicate rows detected."
        )
    else:
        insights.append(
            "No exact duplicate rows detected."
        )

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    for col in numeric_columns:

        if df[col].notna().sum() == 0:
            continue

        average = df[col].mean()
        maximum = df[col].max()
        minimum = df[col].min()

        insights.append(
            f"{col}: Average = {average:.2f}, "
            f"Maximum = {maximum:.2f}, "
            f"Minimum = {minimum:.2f}."
        )

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    for col in categorical_columns:

        counts = df[col].value_counts()

        if not counts.empty:
            insights.append(
                f"{col}: Most frequent value is "
                f"'{counts.index[0]}' "
                f"({counts.iloc[0]} records)."
            )

    return insights
