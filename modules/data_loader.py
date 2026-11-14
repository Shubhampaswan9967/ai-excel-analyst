
import io
import pandas as pd


# Get Excel worksheet names
def get_excel_sheet_names(file_name, file_bytes):

    if file_name.lower().endswith(".xlsx"):

        excel_file = pd.ExcelFile(
            io.BytesIO(file_bytes),
            engine="openpyxl"
        )

        return excel_file.sheet_names

    return []


# Load CSV or Excel dataset
def load_dataset(file_name, file_bytes, sheet_name=None):

    if file_name.lower().endswith(".csv"):

        encodings = ["utf-8-sig", "utf-8", "cp1252"]

        for encoding in encodings:

            try:

                df = pd.read_csv(
                    io.BytesIO(file_bytes),
                    encoding=encoding
                )

                return df

            except UnicodeDecodeError:
                continue

        raise ValueError("Unable to read CSV encoding.")

    elif file_name.lower().endswith(".xlsx"):

        df = pd.read_excel(
            io.BytesIO(file_bytes),
            sheet_name=sheet_name,
            engine="openpyxl"
        )

        return df

    else:

        raise ValueError("Unsupported file format.")
