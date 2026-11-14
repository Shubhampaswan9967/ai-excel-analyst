
# import os
# import json
# import pandas as pd

# from dotenv import load_dotenv
# from openai import OpenAI


# load_dotenv()


# def build_dataset_context(df):

#     context = {
#         "rows": len(df),
#         "columns": len(df.columns),
#         "column_names": df.columns.astype(str).tolist()[:30],
#         "missing_values": {
#             str(col): int(count)
#             for col, count in df.isnull().sum().items()
#             if count > 0
#         },
#         "duplicate_rows": int(df.duplicated().sum()),
#         "numeric_summary": {},
#         "categorical_summary": {}
#     }

#     numeric_columns = df.select_dtypes(
#         include="number"
#     ).columns.tolist()

#     for col in numeric_columns[:20]:

#         stats = df[col].describe()

#         context["numeric_summary"][str(col)] = {
#             "average": round(float(stats["mean"]), 2)
#                 if pd.notna(stats.get("mean")) else None,
#             "minimum": round(float(stats["min"]), 2)
#                 if pd.notna(stats.get("min")) else None,
#             "maximum": round(float(stats["max"]), 2)
#                 if pd.notna(stats.get("max")) else None,
#             "median": round(float(stats["50%"]), 2)
#                 if pd.notna(stats.get("50%")) else None
#         }

#     categorical_columns = df.select_dtypes(
#         include=["object", "category", "bool"]
#     ).columns.tolist()

#     for col in categorical_columns[:20]:

#         top_values = df[col].value_counts().head(5)

#         context["categorical_summary"][str(col)] = {
#             str(key): int(value)
#             for key, value in top_values.items()
#         }

#     return context


# def generate_ai_insights(df):

#     api_key = os.getenv("OPENAI_API_KEY")

#     if not api_key:
#         raise ValueError(
#             "OPENAI_API_KEY not found. Please add it to your .env file."
#         )

#     client = OpenAI(api_key=api_key)

#     dataset_context = build_dataset_context(df)

#     prompt = f"""
# Analyze this dataset as an experienced business data analyst.

# DATASET SUMMARY:
# {json.dumps(dataset_context, indent=2, default=str)}

# Prepare the analysis using these sections:

# 1. Business Overview
# 2. Important Findings
# 3. Potential Business Problems
# 4. Possible Reasons (clearly label assumptions)
# 5. Actionable Recommendations
# 6. Further Analysis Suggestions

# Rules:
# - Use only the statistics provided.
# - Do not invent facts, numbers, causes, or business context.
# - Clearly distinguish observed findings from possible explanations.
# - If the dataset does not support a conclusion, say so.
# - Use simple, professional English.
# - Make recommendations practical and specific.
# """

#     response = client.responses.create(
#         model="gpt-5.5",
#         instructions=(
#             "You are a careful business intelligence analyst. "
#             "Be accurate, evidence-based, and transparent about limitations."
#         ),
#         input=prompt
#     )

#     return response.output_text






import pandas as pd
import numpy as np


def generate_ai_insights(df):

    if df is None or df.empty:
        return "Dataset is empty. Please upload a valid dataset."

    report = []

    # 1. Business Overview
    rows, columns = df.shape

    report.append("# Automatic Business Insights")
    report.append("## 1. Dataset Overview")

    report.append(f"- Total Rows: {rows:,}")
    report.append(f"- Total Columns: {columns}")
    report.append(f"- Duplicate Rows: {df.duplicated().sum():,}")
    report.append(
        f"- Total Missing Values: {df.isnull().sum().sum():,}"
    )

    # 2. Data Quality Analysis
    report.append("\n## 2. Data Quality Findings")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        for col, count in missing.items():
            percentage = (count / rows) * 100

            report.append(
                f"- **{col}**: {count} missing values "
                f"({percentage:.2f}%)."
            )
    else:
        report.append("- No missing values detected.")

    if df.duplicated().sum() > 0:
        report.append(
            "- Duplicate records detected. Review them before analysis."
        )
    else:
        report.append("- No duplicate rows detected.")

    # 3. Numeric Analysis
    report.append("\n## 3. Numeric Column Analysis")

    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        for col in numeric_cols:

            series = df[col].dropna()

            if series.empty:
                continue

            average = series.mean()
            median = series.median()
            minimum = series.min()
            maximum = series.max()

            report.append(
                f"- **{col}**: Average = {average:,.2f}, "
                f"Median = {median:,.2f}, "
                f"Minimum = {minimum:,.2f}, "
                f"Maximum = {maximum:,.2f}."
            )

            # Outlier detection using IQR
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            lower_limit = q1 - (1.5 * iqr)
            upper_limit = q3 + (1.5 * iqr)

            outliers = (
                (series < lower_limit) |
                (series > upper_limit)
            ).sum()

            if outliers > 0:
                report.append(
                    f"  - Potential outliers detected: {outliers:,}. "
                    "Investigate these values."
                )

    else:
        report.append("- No numeric columns found.")

    # 4. Categorical Analysis
    report.append("\n## 4. Categorical Column Analysis")

    categorical_cols = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns

    if len(categorical_cols) > 0:

        for col in categorical_cols:

            top_values = df[col].value_counts().head(5)

            report.append(f"\n**Column: {col}**")

            for value, count in top_values.items():

                percentage = (count / rows) * 100

                report.append(
                    f"- {value}: {count:,} records "
                    f"({percentage:.2f}%)."
                )

    else:
        report.append("- No categorical columns found.")

    # 5. Correlation Analysis
    report.append("\n## 5. Correlation Findings")

    if len(numeric_cols) >= 2:

        correlation = df[numeric_cols].corr()

        pairs = []

        for i in range(len(correlation.columns)):
            for j in range(i + 1, len(correlation.columns)):

                col1 = correlation.columns[i]
                col2 = correlation.columns[j]
                value = correlation.iloc[i, j]

                if pd.notna(value):
                    pairs.append((col1, col2, value))

        pairs.sort(key=lambda x: abs(x[2]), reverse=True)

        if pairs:
            for col1, col2, value in pairs[:5]:
                report.append(
                    f"- {col1} and {col2}: "
                    f"Correlation = {value:.2f}."
                )
        else:
            report.append("- No usable correlations found.")

    else:
        report.append(
            "- At least two numeric columns are required."
        )

    # 6. Recommendations
    report.append("\n## 6. Recommended Next Steps")

    if not missing.empty:
        report.append(
            "- Review missing values and decide how to handle them."
        )

    if df.duplicated().sum() > 0:
        report.append(
            "- Investigate duplicate records before reporting results."
        )

    if len(numeric_cols) > 0:
        report.append(
            "- Investigate numeric outliers and validate unusual values."
        )

    if len(categorical_cols) > 0:
        report.append(
            "- Review the most frequent categories to understand "
            "the dataset's distribution."
        )

    report.append(
        "\n*Note: These are statistical findings, not confirmed "
        "business causes. Correlation does not prove causation.*"
    )

    return "\n".join(report)
