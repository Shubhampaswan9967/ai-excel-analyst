
import pandas as pd


def get_profile(df):

    # Dataset information

    total_rows = df.shape[0]

    total_columns = df.shape[1]

    total_missing = int(df.isnull().sum().sum())

    duplicate_rows = int(df.duplicated().sum())


    # Column data types

    data_types = pd.DataFrame({

        "Column": df.columns.astype(str),

        "Data Type": df.dtypes.astype(str).values

    })


    # Missing values report

    missing_counts = df.isnull().sum()

    missing_table = pd.DataFrame({

        "Column": missing_counts.index.astype(str),

        "Missing Values": missing_counts.values,

        "Missing %": (
            missing_counts.values /
            max(total_rows, 1) * 100
        ).round(2)

    })


    # Identify numerical columns

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()


    # Identify categorical columns

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()


    # Numerical summary

    if numeric_columns:

        numeric_summary = (
            df[numeric_columns]
            .describe()
            .T
            .reset_index()
            .rename(columns={"index": "Column"})
        )

    else:

        numeric_summary = pd.DataFrame()


    # Final profile

    profile = {

        "total_rows": total_rows,

        "total_columns": total_columns,

        "total_missing": total_missing,

        "duplicate_rows": duplicate_rows,

        "numeric_columns": numeric_columns,

        "categorical_columns": categorical_columns,

        "data_types": data_types,

        "missing_table": missing_table,

        "numeric_summary": numeric_summary

    }

    return profile
