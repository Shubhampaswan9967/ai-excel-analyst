
from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def create_excel_report(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        # Original dataset
        df.to_excel(
            writer,
            sheet_name="Dataset",
            index=False
        )

        # Data quality
        quality = pd.DataFrame({
            "Column": df.columns.astype(str),
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isnull().sum().values,
            "Missing Percentage": (
                df.isnull().mean().values * 100
            ).round(2)
        })

        quality.to_excel(
            writer,
            sheet_name="Data Quality",
            index=False
        )

        # Numeric summary
        numeric = df.select_dtypes(include="number")

        if not numeric.empty:
            numeric.describe().T.to_excel(
                writer,
                sheet_name="Numeric Analysis"
            )

        # Categorical summary
        categorical = df.select_dtypes(
            include=["object", "category", "bool"]
        )

        if not categorical.empty:

            rows = []

            for col in categorical.columns:

                top = df[col].value_counts().head(5)

                for value, count in top.items():

                    rows.append({
                        "Column": col,
                        "Value": str(value),
                        "Count": int(count)
                    })

            pd.DataFrame(rows).to_excel(
                writer,
                sheet_name="Category Analysis",
                index=False
            )

    output.seek(0)

    return output.getvalue()


def create_pdf_dataset_report(df):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "Business Data Analysis Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    # Dataset overview
    story.append(
        Paragraph("1. Dataset Overview", styles["Heading2"])
    )

    overview = [
        ["Metric", "Value"],
        ["Total Rows", f"{len(df):,}"],
        ["Total Columns", str(len(df.columns))],
        ["Missing Values", f"{df.isnull().sum().sum():,}"],
        ["Duplicate Rows", f"{df.duplicated().sum():,}"]
    ]

    table = Table(overview, colWidths=[3 * inch, 2 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Missing value details
    story.append(
        Paragraph("2. Data Quality Analysis", styles["Heading2"])
    )

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        story.append(
            Paragraph(
                "No missing values detected.",
                styles["BodyText"]
            )
        )
    else:
        for col, count in missing.items():
            story.append(
                Paragraph(
                    f"{escape(str(col))}: {count} missing values",
                    styles["BodyText"]
                )
            )

    story.append(Spacer(1, 15))

    # Numeric analysis
    story.append(
        Paragraph("3. Numeric Analysis", styles["Heading2"])
    )

    numeric = df.select_dtypes(include="number")

    if numeric.empty:
        story.append(
            Paragraph("No numeric columns found.", styles["BodyText"])
        )
    else:
        for col in numeric.columns:

            series = numeric[col].dropna()

            if series.empty:
                continue

            story.append(
                Paragraph(
                    f"<b>{escape(str(col))}</b>",
                    styles["Heading3"]
                )
            )

            summary = (
                f"Average: {series.mean():,.2f} | "
                f"Median: {series.median():,.2f} | "
                f"Minimum: {series.min():,.2f} | "
                f"Maximum: {series.max():,.2f}"
            )

            story.append(
                Paragraph(summary, styles["BodyText"])
            )

            story.append(Spacer(1, 8))

    # Categorical analysis
    story.append(
        Paragraph("4. Categorical Analysis", styles["Heading2"])
    )

    categorical = df.select_dtypes(
        include=["object", "category", "bool"]
    )

    if categorical.empty:
        story.append(
            Paragraph(
                "No categorical columns found.",
                styles["BodyText"]
            )
        )
    else:
        for col in categorical.columns:

            top = df[col].value_counts().head(5)

            story.append(
                Paragraph(
                    f"<b>{escape(str(col))}</b>",
                    styles["Heading3"]
                )
            )

            for value, count in top.items():

                story.append(
                    Paragraph(
                        f"{escape(str(value))}: {count:,} records",
                        styles["BodyText"]
                    )
                )

            story.append(Spacer(1, 8))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Note: This report contains descriptive statistics. "
            "Statistical relationships do not establish causation.",
            styles["Italic"]
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
