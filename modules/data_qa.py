
# import pandas as pd
# import re


# def normalize(text):
#     text = str(text).lower()
#     text = re.sub(r"[^a-z0-9]+", " ", text)
#     return " ".join(text.split())


# def find_column(df, question):

#     q = normalize(question)

#     # Business-specific column mapping
#     sales_aliases = [
#         "sales", "sale", "revenue", "purchase amount",
#         "amount", "total sales", "sales amount"
#     ]

#     product_aliases = [
#         "products", "product", "items", "item",
#         "item purchased", "product name"
#     ]

#     # Find sales column
#     if any(alias in q.split() for alias in ["sales", "sale", "revenue"]):

#         preferred = [
#             "purchase amount usd",
#             "purchase amount",
#             "sales",
#             "revenue",
#             "sales amount",
#             "amount",
#             "order value",
#             "total amount"
#         ]

#         for candidate in preferred:
#             for col in df.columns:
#                 if normalize(col) == candidate:
#                     return col

#     # Find product column
#     if any(alias in q.split() for alias in ["product", "products", "item", "items"]):

#         preferred = [
#             "item purchased",
#             "product name",
#             "product",
#             "products",
#             "item",
#             "items"
#         ]

#         for candidate in preferred:
#             for col in df.columns:
#                 if normalize(col) == candidate:
#                     return col

#     # Exact column name matching
#     padded_question = f" {q} "

#     for col in df.columns:
#         normalized_col = normalize(col)

#         if normalized_col and f" {normalized_col} " in padded_question:
#             return col

#     return None


# def answer_dataset_question(df, question):

#     if df is None or df.empty:
#         return "Please upload a dataset first."

#     if not question or not question.strip():
#         return "Please enter a question."

#     q = normalize(question)

#     # 1. Rows
#     if any(word in q.split() for word in ["rows", "records", "row"]):
#         return f"Your dataset contains {len(df):,} rows."

#     # 2. Columns
#     if "columns" in q.split() or "column" in q.split():
#         return (
#             f"Your dataset contains {len(df.columns)} columns:\n"
#             + ", ".join(map(str, df.columns))
#         )

#     # 3. Missing values
#     if any(word in q.split() for word in ["missing", "null"]):

#         missing = df.isnull().sum()
#         missing = missing[missing > 0]

#         if missing.empty:
#             return "There are no missing values."

#         result = f"Total missing values: {missing.sum()}\n\n"

#         for col, count in missing.items():
#             result += f"- {col}: {count}\n"

#         return result

#     # 4. Duplicates
#     if "duplicate" in q.split():
#         return f"Total duplicate rows: {df.duplicated().sum():,}"

#     # 5. Identify business column
#     column = find_column(df, question)

#     if column is None:
#         return (
#             "I could not identify the required column.\n\n"
#             "Available columns:\n"
#             + ", ".join(map(str, df.columns))
#         )

#     # 6. Numeric analysis
#     if pd.api.types.is_numeric_dtype(df[column]):

#         series = pd.to_numeric(df[column], errors="coerce").dropna()

#         if series.empty:
#             return f"No numeric data available in {column}."

#         if any(word in q.split() for word in ["average", "avg", "mean"]):
#             return f"Average {column}: {series.mean():,.2f}"

#         if any(word in q.split() for word in ["total", "sum"]):
#             return f"Total {column}: {series.sum():,.2f}"

#         if any(word in q.split() for word in ["highest", "maximum", "max"]):
#             return f"Highest {column}: {series.max():,.2f}"

#         if any(word in q.split() for word in ["lowest", "minimum", "min"]):
#             return f"Lowest {column}: {series.min():,.2f}"

#         if "median" in q.split():
#             return f"Median {column}: {series.median():,.2f}"

#         return (
#             f"Numeric summary for {column}:\n"
#             f"- Average: {series.mean():,.2f}\n"
#             f"- Total: {series.sum():,.2f}\n"
#             f"- Highest: {series.max():,.2f}\n"
#             f"- Lowest: {series.min():,.2f}\n"
#             f"- Median: {series.median():,.2f}"
#         )

#     # 7. Top products by sales
#     if (
#         any(word in q.split() for word in ["product", "products", "item", "items"])
#         and any(word in q.split() for word in ["sales", "revenue"])
#     ):

#         sales_col = None

#         for candidate in ["purchase amount usd", "purchase amount", "sales", "revenue"]:
#             for col in df.columns:
#                 if normalize(col) == candidate:
#                     sales_col = col
#                     break
#             if sales_col is not None:
#                 break

#         if sales_col is not None:
#             result = df.groupby(column)[sales_col].sum().sort_values(
#                 ascending=False
#             ).head(5)

#             return (
#                 f"Top 5 products by total {sales_col}:\n\n"
#                 + result.to_string()
#             )

#     # 8. Top categorical values
#     if any(word in q.split() for word in ["top", "most", "popular", "frequent"]):

#         top_values = df[column].value_counts().head(5)

#         if top_values.empty:
#             return f"No values found in {column}."

#         return (
#             f"Top 5 values in {column}:\n\n"
#             + top_values.to_string()
#         )

#     return (
#         f"Column identified: {column}\n\n"
#         f"Unique values: {df[column].nunique(dropna=True)}\n\n"
#         f"Most frequent values:\n"
#         + df[column].value_counts().head(5).to_string()
#     )

#-----------------------------------------------------------------------------
# New Code Likh Raha Hu Agar ye sahi nahi huva tho uper wala code hi ralhunga
#-----------------------------------------------------------------------------


import pandas as pd
import re


def normalize(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def get_column(df, aliases):
    """
    Dataset mein aliases ke according column find karta hai.
    """
    normalized_columns = {
        normalize(col): col for col in df.columns
    }

    for alias in aliases:
        if normalize(alias) in normalized_columns:
            return normalized_columns[normalize(alias)]

    return None


def format_number(value):
    return f"{value:,.2f}"


def answer_dataset_question(df, question):

    if df is None or df.empty:
        return "Please upload a dataset first."

    if not question or not question.strip():
        return "Please enter a question."

    q = normalize(question)
    words = q.split()

    # 1. Total rows
    if any(word in words for word in ["rows", "records", "row"]):
        return f"Your dataset contains {len(df):,} rows."

    # 2. Total columns
    if "columns" in words or "column" in words:
        return (
            f"Your dataset contains {len(df.columns)} columns:\n\n"
            + ", ".join(map(str, df.columns))
        )

    # 3. Missing values
    if any(word in words for word in ["missing", "null"]):

        missing = df.isnull().sum()
        missing = missing[missing > 0]

        if missing.empty:
            return "There are no missing values."

        result = f"Total missing values: {missing.sum()}\n\n"

        for col, count in missing.items():
            result += f"- {col}: {count}\n"

        return result

    # 4. Duplicate rows
    if "duplicate" in words:
        return f"Total duplicate rows: {df.duplicated().sum():,}"

    # 5. Average purchase amount
    if any(term in q for term in [
        "average purchase amount",
        "average amount",
        "avg amount",
        "mean amount"
    ]):

        amount_col = get_column(
            df,
            ["Purchase Amount (USD)",
             "Purchase Amount USD",
             "Amount",
             "Purchase Amount",
             "Sales"]
        )

        if amount_col is None:
            return "Purchase amount column not found."

        values = pd.to_numeric(
            df[amount_col], errors="coerce"
        ).dropna()

        if values.empty:
            return "No numeric purchase amount data available."

        return (
            f"Average Purchase Amount: "
            f"{format_number(values.mean())}"
        )

    # 6. Highest sales category
    if (
        "category" in words
        and any(term in words for term in [
            "highest", "maximum", "max", "top"
        ])
        and any(term in words for term in [
            "sales", "sale", "revenue", "amount"
        ])
    ):

        category_col = get_column(df, ["Category"])
        amount_col = get_column(
            df, ["Purchase Amount (USD)",
                "Purchase Amount USD",
                "Amount",
                "Purchase Amount",
                "Sales",
                "Revenue"]
        )

        if category_col is None or amount_col is None:
            return "Category or sales amount column not found."

        temp = df[[category_col, amount_col]].copy()

        temp[amount_col] = pd.to_numeric(
            temp[amount_col], errors="coerce"
        )

        result = (
            temp.dropna()
            .groupby(category_col)[amount_col]
            .sum()
            .sort_values(ascending=False)
        )

        if result.empty:
            return "No category sales data available."

        highest_category = result.index[0]
        highest_sales = result.iloc[0]

        return (
            f"Highest Sales Category: {highest_category}\n"
            f"Total Sales: {format_number(highest_sales)}"
        )

    # 7. Most popular products by quantity
    if any(term in words for term in [
        "product", "products", "item", "items"
    ]) and any(term in words for term in [
        "popular", "top", "most"
    ]):

        product_col = get_column(
            df,
            ["SKU", "Product", "Product Name", "Item Purchased"]
        )

        quantity_col = get_column(
            df,
            ["Qty", "Quantity", "Units Sold"]
        )

        if product_col is None:
            return "Product column not found."

        if quantity_col is not None:

            temp = df[[product_col, quantity_col]].copy()

            temp[quantity_col] = pd.to_numeric(
                temp[quantity_col], errors="coerce"
            )

            result = (
                temp.dropna()
                .groupby(product_col)[quantity_col]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            return (
                "Top 5 Most Popular Products by Quantity:\n\n"
                + result.to_string()
            )

        result = df[product_col].value_counts().head(5)

        return (
            "Top 5 Most Popular Products by Frequency:\n\n"
            + result.to_string()
        )

    # 8. Top five locations
    if any(term in words for term in [
        "location", "locations", "city", "cities"
    ]):

        location_col = get_column(
            df,
            ["ship-city", "City", "Location", "Town"]
        )

        if location_col is None:
            return "Location or city column not found."

        result = df[location_col].value_counts().head(5)

        return (
            "Top 5 Locations by Number of Records:\n\n"
            + result.to_string()
        )

    # 9. Generic column matching
    column = get_column(df, df.columns.tolist())

    if column is None:

        return (
            "I could not identify the required column.\n\n"
            "Available columns:\n"
            + ", ".join(map(str, df.columns))
        )

    # 10. Numeric analysis
    if pd.api.types.is_numeric_dtype(df[column]):

        series = pd.to_numeric(
            df[column], errors="coerce"
        ).dropna()

        if series.empty:
            return f"No numeric data available in {column}."

        if any(word in words for word in ["average", "avg", "mean"]):
            return f"Average {column}: {format_number(series.mean())}"

        if any(word in words for word in ["total", "sum"]):
            return f"Total {column}: {format_number(series.sum())}"

        if any(word in words for word in ["highest", "maximum", "max"]):
            return f"Highest {column}: {format_number(series.max())}"

        if any(word in words for word in ["lowest", "minimum", "min"]):
            return f"Lowest {column}: {format_number(series.min())}"

        if "median" in words:
            return f"Median {column}: {format_number(series.median())}"

        return (
            f"Numeric Summary: {column}\n\n"
            f"Average: {format_number(series.mean())}\n"
            f"Total: {format_number(series.sum())}\n"
            f"Highest: {format_number(series.max())}\n"
            f"Lowest: {format_number(series.min())}\n"
            f"Median: {format_number(series.median())}"
        )

    # 11. Categorical analysis
    result = df[column].value_counts().head(5)

    return (
        f"Column: {column}\n"
        f"Unique Values: {df[column].nunique(dropna=True)}\n\n"
        f"Top 5 Values:\n"
        + result.to_string()
    )



