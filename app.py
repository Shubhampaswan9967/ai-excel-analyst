
import streamlit as st
import pandas as pd


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

from modules.ai_insights import generate_ai_insights

from modules.data_qa import answer_dataset_question

from modules.report_generator import (
    create_excel_report,
    create_pdf_dataset_report
)

from modules.database import create_tables
from modules.auth import (
    register_user, 
    login_user,
    send_password_reset_otp,
    reset_password
)    
    

from modules.data_analyzer import (
    get_analysis_summary,
    get_numeric_analysis,
    get_categorical_analysis,
    get_top_values,
    get_correlation_analysis,
    generate_business_insights
)

import plotly.express as px

from modules.data_loader import (
    load_dataset,
    get_excel_sheet_names
)

from modules.data_profiler import get_profile


from modules.data_cleaner import (
    clean_dataset,
    convert_column_type,
    detect_outliers
)


from modules.history import (
    save_analysis,
    get_user_history,
    get_history_report
)


def create_pdf_report(report_text):
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

    for line in report_text.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 8))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        else:
            clean_line = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("**", "")
            )
            story.append(Paragraph(clean_line, styles["BodyText"]))

        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="AI Excel Analyst",
    page_icon="📊",
    layout="wide"
)


# ----------------------------------
# SESSION STATE
# ----------------------------------

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = None

if "selected_file_name" not in st.session_state:
    st.session_state.selected_file_name = None


if "cleaned_dataset" not in st.session_state:
    st.session_state.cleaned_dataset = None

if "cleaning_summary" not in st.session_state:
    st.session_state.cleaning_summary = None



# ----------------------------------
# CUSTOM CSS
# ----------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FB;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] * {
    color: white;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
}

</style>
""", unsafe_allow_html=True)



def show_auth_screen():

    st.title("AI Excel Analyst")
    st.subheader("Welcome! Please login or register.")

    login_tab, register_tab, forgot_tab = st.tabs(
        ["Login", "Register", "Forgot Password"]
    )

    # LOGIN TAB
    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", key="login_button"):

            if not email or not password:
                st.warning("Enter email and password.")

            else:
                user = login_user(email.strip(), password)

                if user:
                    st.session_state.user = user
                    st.rerun()

                else:
                    st.error("Invalid email or password.")

    # REGISTER TAB
    with register_tab:

        username = st.text_input(
            "Username",
            key="register_username"
        )

        new_email = st.text_input(
            "Email",
            key="register_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        if st.button("Create Account", key="register_button"):

            if not username.strip() or not new_email.strip() or not new_password:
                st.warning("Please fill all fields.")

            elif len(new_password) < 8:
                st.warning("Password must have at least 8 characters.")

            else:
                success, message = register_user(
                    username.strip(),
                    new_email.strip(),
                    new_password
                )

                if success:
                    st.success(message)

                else:
                    st.error(message)

    # FORGOT PASSWORD TAB
    with forgot_tab:

        st.subheader("Reset Your Password")

        reset_email = st.text_input(
            "Registered Email",
            key="reset_email"
        )

        if st.button("Send OTP", key="send_otp_button"):

            if not reset_email.strip() or "@" not in reset_email:
                st.warning("Please enter a valid email address.")

            else:
                send_password_reset_otp(reset_email)

                st.info(
                    "If this email is registered and email delivery "
                    "is configured, an OTP will be sent. Check your inbox "
                    "and spam folder."
                )

        st.divider()

        st.write("Enter the OTP received in your email.")

        otp = st.text_input(
            "6-Digit OTP",
            max_chars=6,
            key="reset_otp"
        )

        new_reset_password = st.text_input(
            "New Password",
            type="password",
            key="new_reset_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="confirm_reset_password"
        )

        if st.button("Reset Password", key="reset_password_button"):

            if not reset_email.strip() or not otp or not new_reset_password or not confirm_password:
                st.warning("Please fill all fields.")

            elif not otp.isdigit() or len(otp) != 6:
                st.warning("Enter a valid 6-digit OTP.")

            elif len(new_reset_password) < 8:
                st.warning("Password must have at least 8 characters.")

            elif new_reset_password != confirm_password:
                st.error("Passwords do not match.")

            else:
                success, message = reset_password(
                    reset_email.strip(),
                    otp,
                    new_reset_password
                )

                if success:
                    st.success(message)

                else:
                    st.error(message)



try:
    create_tables()
except Exception:
    st.error("Database connection failed. Check your MySQL settings.")
    st.stop()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    show_auth_screen()
    st.stop()                    



# ----------------------------------
# NAVIGATION
# ----------------------------------

menu_options = [
    "🏠 Home Dashboard",
    "📁 Upload Dataset",
    "📋 Data Preview",
    "🧹 Data Cleaning",
    "📊 Data Analysis",
    "💡 AI Insights",
    "🤖 Ask AI",
    "📄 Generate Report",
    "🕘 Analysis History"
]


def navigate(page):
    st.session_state.menu = page


with st.sidebar:

    st.title("📊 AI Excel Analyst")

    st.caption("SMART DATA INSIGHT")

    st.divider()

    menu = st.radio(
        "MAIN MENU",
        menu_options,
        key="menu"
    )

    st.divider()

    st.caption("VERSION 1.0")


    st.sidebar.write(
    f"Welcome, {st.session_state.user['username']}"
   )

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.chat_history = []
    st.rerun()





# ----------------------------------
# HOME DASHBOARD
# ----------------------------------

if menu == "🏠 Home Dashboard":

    st.title("Welcome to AI Excel Analyst 👋")

    st.write(
        "Your intelligent data analysis workspace."
    )

    df = st.session_state.dataset

    if df is not None:

        profile = get_profile(df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Rows", profile["total_rows"])

        col2.metric("Total Columns", profile["total_columns"])

        col3.metric("Missing Values", profile["total_missing"])

        col4.metric("Duplicate Rows", profile["duplicate_rows"])

        st.success(
            f"Active Dataset: {st.session_state.dataset_name}"
        )

    else:

        st.info("Upload a dataset to get started.")

        st.button(
            "Upload Dataset",
            on_click=navigate,
            args=("📁 Upload Dataset",)
        )


# ----------------------------------
# UPLOAD DATASET
# ----------------------------------

elif menu == "📁 Upload Dataset":

    st.title("📁 Upload Dataset")

    st.write(
        "Upload your Excel or CSV file."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"],
        max_upload_size=50
    )

    if uploaded_file is not None:

        file_name = uploaded_file.name

        file_bytes = uploaded_file.getvalue()

        # Reset old dataset when new file is selected

        if st.session_state.selected_file_name != file_name:

            st.session_state.dataset = None

            st.session_state.dataset_name = None

            st.session_state.cleaned_dataset = None

            st.session_state.cleaning_summary = None

            st.session_state.outlier_report = None

            st.session_state.ai_insights_result = None

            st.session_state.selected_file_name = file_name

            if "sheet_choice" in st.session_state:
                del st.session_state["sheet_choice"]

        st.success(f"Selected File: {file_name}")

        st.write(
            f"File Size: {uploaded_file.size / 1024:.2f} KB"
        )

        selected_sheet = None

        # Excel worksheet selection

        if file_name.lower().endswith(".xlsx"):

            sheet_names = get_excel_sheet_names(
                file_name,
                file_bytes
            )

            if not sheet_names:

                st.error("No worksheets found.")

            else:

                selected_sheet = st.selectbox(
                    "Select Excel Worksheet",
                    sheet_names,
                    key="sheet_choice"
                )

        # Load dataset

        if st.button("Load Dataset", type="primary"):

            try:
                
                with st.spinner("Loading your dataset... Please wait."):

                    df = load_dataset(
                        file_name,
                        file_bytes,
                        selected_sheet
                    )
                
                if df.empty:
                    st.error("Uploaded dataset is empty")

                elif df.shape[1] == 0:

                    st.error("Dataset has no columns.")

                else:
                    
                    if df.columns.duplicated().any():
                        st.warning(
                            "Duplicate column names detected"
                            "Please check your dataset"
                        )

                    st.session_state.dataset = df

                    st.session_state.dataset_name = file_name

                    st.success("Dataset loaded successfully!")

                    st.rerun()

            except Exception as e:
                
                    st.error(
            "Unable to load your dataset. "
            "Please check your file format and try again."
        )

                    with st.expander("Technical Error Details"):
                        st.exception(e)
            

    if st.session_state.dataset is not None:

        st.success(
            f"Currently loaded: {st.session_state.dataset_name}"
        )


# ----------------------------------
# DATA PREVIEW
# ----------------------------------

elif menu == "📋 Data Preview":

    st.title("📋 Data Preview")

    df = st.session_state.dataset

    if df is None:

        st.warning("Please upload a dataset first.")

        st.button(
            "Go to Upload",
            on_click=navigate,
            args=("📁 Upload Dataset",)
        )

    else:

        st.subheader("Dataset Information")

        profile = get_profile(df)

        # KPI cards

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Rows",
            profile["total_rows"]
        )

        col2.metric(
            "Total Columns",
            profile["total_columns"]
        )

        col3.metric(
            "Missing Values",
            profile["total_missing"]
        )

        col4.metric(
            "Duplicate Rows",
            profile["duplicate_rows"]
        )

        st.divider()

        

        
        # Dataset Preview

        st.subheader("Dataset Preview")

        # Select columns
        search_columns = st.multiselect(
        "Select columns to display and search",
        options=df.columns.tolist(),
        default=df.columns.tolist(),
        key="preview_columns"
        )

        # Search box
        search_query = st.text_input(
        "Search in dataset",
        placeholder="Enter a value to search...",
        key="preview_search"
        )

        # Number of rows
        rows_to_display = st.number_input(
        "Number of rows to display",
        min_value=1,
        max_value=max(1, len(df)),
        value=min(100, max(1, len(df))),
        step=10,
        key="preview_rows"
        )

        # Apply search
        filtered_df = df.copy()

        if search_query and search_columns:

            search_mask = (
             filtered_df[search_columns]
             .astype("string")
             .apply(
                lambda column: column.str.contains(
                    search_query,
                    case=False,
                    na=False,
                    regex=False
                )
            )
             .any(axis=1)
            )

            filtered_df = filtered_df[search_mask]

        elif search_query and not search_columns:

          st.warning("Please select at least one column to search.")

        # Display result
        st.caption(f"Showing {min(len(filtered_df), int(rows_to_display))} of {len(filtered_df)} matching rows")

        if search_columns:

            st.dataframe(
              filtered_df[search_columns].head(int(rows_to_display)),
              use_container_width=True,
              height=350
            )

        else:

           st.info("Please select columns to display.")


        # Data types

        st.subheader("Column Data Types")

        st.dataframe(
            profile["data_types"],
            use_container_width=True,
            hide_index=True
        )

        # Missing values

        st.subheader("Missing Values Report")

        st.dataframe(
            profile["missing_table"],
            use_container_width=True,
            hide_index=True
        )

        # Column categories

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Numerical Columns")

            st.write(
                profile["numeric_columns"]
            )

        with col2:

            st.subheader("Categorical Columns")

            st.write(
                profile["categorical_columns"]
            )

        # Numerical summary

        st.subheader("Numerical Statistics")

        if not profile["numeric_summary"].empty:

            st.dataframe(
                profile["numeric_summary"],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No numerical columns found.")


# ----------------------------------
# FUTURE MODULES
# ----------------------------------


elif menu == "🧹 Data Cleaning":

    st.title("🧹 Smart Data Cleaning")

    df = st.session_state.dataset

    if df is None:

        st.warning("Please upload a dataset first.")

    else:

        st.write("Analyze and clean your uploaded dataset.")

        # Original dataset

        st.subheader("Original Data Quality")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", len(df))

        col2.metric(
            "Missing Values",
            int(df.isna().sum().sum())
        )

        col3.metric(
            "Duplicate Rows",
            int(df.duplicated().sum())
        )

        st.divider()

        # Cleaning options

        st.subheader("Cleaning Options")

        col1, col2 = st.columns(2)

        with col1:

            numeric_strategy = st.selectbox(
                "Numeric Missing Values",
                ["median", "mean", "zero", "keep"]
            )

        with col2:

            categorical_strategy = st.selectbox(
                "Categorical Missing Values",
                ["mode", "unknown", "keep"]
            )

        remove_duplicate = st.checkbox(
            "Remove exact duplicate rows",
            value=True
        )

        type_column = st.selectbox(
            "Select column for type correction",
            ["None"] + df.columns.tolist()
        )

        target_type = None

        if type_column != "None":

            target_type = st.selectbox(
                "Convert selected column to",
                ["Numeric", "Datetime"]
            )

        st.info(
            "Text whitespace will be cleaned automatically. "
            "Outliers will only be detected, not removed."
        )

        # Run cleaning

        if st.button("Run Data Cleaning", type="primary"):

            try:
                
                with st.spinner("Cleaning your dataset... Please wait."):

                    cleaned_df, summary, outliers = clean_dataset(
                        df,
                        numeric_strategy,
                        categorical_strategy,
                        remove_duplicate,
                        None if type_column == "None" else type_column,
                        target_type
                    )

                st.session_state.cleaned_dataset = cleaned_df

                st.session_state.cleaning_summary = summary

                st.session_state.outlier_report = outliers

                st.success("Data cleaning completed!")

            except Exception as e:
                
                st.error(
                 "Data cleaning failed. Please check your cleaning options."
                )

                with st.expander("Technical Error Details"):
                    st.exception(e)
                    

        # Cleaning results

        cleaned_df = st.session_state.cleaned_dataset

        summary = st.session_state.cleaning_summary

        if cleaned_df is not None and summary is not None:

            st.divider()

            st.subheader("Cleaning Results")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Original Rows",
                summary["original_rows"]
            )

            col2.metric(
                "Cleaned Rows",
                summary["cleaned_rows"]
            )

            col3.metric(
                "Duplicates Removed",
                summary["duplicates_removed"]
            )

            col4.metric(
                "Remaining Missing",
                summary["remaining_missing"]
            )

            st.write("")

            st.metric(
                "Missing Values Filled",
                summary["missing_values_filled"]
            )

            st.metric(
                "Type Conversion Failures",
                summary["conversion_failures"]
            )

            st.subheader("Before vs After")

            comparison = pd.DataFrame({

                "Metric": [
                    "Total Rows",
                    "Missing Values",
                    "Duplicate Rows"
                ],

                "Before Cleaning": [
                    len(df),
                    int(df.isna().sum().sum()),
                    int(df.duplicated().sum())
                ],

                "After Cleaning": [
                    len(cleaned_df),
                    int(cleaned_df.isna().sum().sum()),
                    int(cleaned_df.duplicated().sum())
                ]

            })

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Outlier Detection Report")

            outlier_report = st.session_state.get(
                "outlier_report",
                pd.DataFrame()
            )

            if not outlier_report.empty:

                st.dataframe(
                    outlier_report,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No outliers detected by the IQR method.")

            st.subheader("Cleaned Dataset Preview")

            st.dataframe(
                cleaned_df.head(100),
                use_container_width=True
            )

            # Download CSV

            csv_data = cleaned_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv"
            )

            # Download Excel

            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="xlsxwriter"
            ) as writer:

                cleaned_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Cleaned Data"
                )

            st.download_button(
                "Download Cleaned Excel",
                data=excel_buffer.getvalue(),
                file_name="cleaned_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


elif menu == "📊 Data Analysis":

    st.title("📊 Smart Data Analysis")

    if st.session_state.get("dataset") is None:
        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.get("cleaned_dataset")

        if df is None:
            df = st.session_state.dataset

        st.subheader("Dataset Overview")

        summary = get_analysis_summary(df)

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", summary["total_rows"])
        col2.metric("Total Columns", summary["total_columns"])
        col3.metric("Missing Values", summary["total_missing"])

        col4, col5, col6 = st.columns(3)

        col4.metric("Numeric Columns", summary["numeric_columns"])
        col5.metric("Categorical Columns", summary["categorical_columns"])
        col6.metric("Duplicate Rows", summary["duplicate_rows"])

        st.divider()

        st.subheader("Numeric Analysis")

        numeric_result = get_numeric_analysis(df)

        if not numeric_result.empty:
            st.dataframe(numeric_result, use_container_width=True)
        else:
            st.info("No numeric columns found.")

        st.divider()

        st.subheader("Categorical Analysis")

        categorical_result = get_categorical_analysis(df)

        if not categorical_result.empty:
            st.dataframe(categorical_result, use_container_width=True)
        else:
            st.info("No categorical columns found.")

        st.divider()

        st.subheader("Top 5 Values Analysis")

        selected_column = st.selectbox(
            "Select a column",
            df.columns.tolist()
        )

        top_values = get_top_values(df, selected_column)

        if not top_values.empty:

            st.dataframe(top_values, use_container_width=True)

            fig = px.bar(
                top_values,
                x=selected_column,
                y="Count",
                title=f"Top Values: {selected_column}"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("Correlation Analysis")

        correlation = get_correlation_analysis(df)

        if not correlation.empty:

            fig = px.imshow(
                correlation,
                text_auto=True,
                aspect="auto",
                title="Correlation Heatmap"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("At least two numeric columns are required.")

        st.divider()

        st.subheader("Automatic Business Insights")

        insights = generate_business_insights(df)

        for i, insight in enumerate(insights, start=1):
            st.write(f"{i}. {insight}")


elif menu == "💡 AI Insights":

    st.title("💡 AI-Powered Business Insights")

    st.write(
        "Generate business insights and recommendations "
        "from your uploaded dataset."
    )

    if st.session_state.get("dataset") is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.get("cleaned_dataset")

        if df is None:
            df = st.session_state.dataset

        st.info(
            f"Dataset ready: {df.shape[0]} rows "
            f"and {df.shape[1]} columns"
        )

        st.warning(
            "AI analysis sends aggregate dataset statistics "
            "to the OpenAI API. Review sensitive data before use."
        )

        if st.button("Generate AI Business Insights"):

            with st.spinner(
                "AI is analyzing your dataset..."
            ):

                try:

                    ai_result = generate_ai_insights(df)

                    st.session_state.ai_insights_result = ai_result

                except Exception as e:

                    st.error(f"AI Analysis Error: {e}")

        
        if st.session_state.get("ai_insights_result"):

             st.divider()

             st.subheader("📊 AI Analysis Report")

             total_rows = len(df)
             total_columns = len(df.columns)
             missing_values = int(df.isnull().sum().sum())
             duplicate_rows = int(df.duplicated().sum())

             col1, col2, col3, col4 = st.columns(4)

             with col1:
               st.metric("Total Rows", f"{total_rows:,}")

             with col2:
                st.metric("Total Columns", total_columns)

             with col3:
                st.metric("Missing Values", f"{missing_values:,}")

             with col4:
                st.metric("Duplicate Rows", f"{duplicate_rows:,}")

             st.divider()

             st.subheader("📋 Business Insights Report")

             st.markdown(
                st.session_state.ai_insights_result
            )

             st.divider()

             st.subheader("📥 Download Your Report")

             report_text = st.session_state.ai_insights_result

             col1, col2 = st.columns(2)

             with col1:
               st.download_button(
                    "Download Markdown",
                     data=report_text,
                     file_name="business_insights_report.md",
                    mime="text/markdown"
                )

             with col2:
                pdf_data = create_pdf_report(report_text)

                st.download_button(
                    "Download PDF Report",
                    data=pdf_data,
                    file_name="business_insights_report.pdf",
                    mime="application/pdf"
                )
    


elif menu == "🤖 Ask AI":

    st.title("🤖 Chat With Your Dataset")

    st.write(
        "Ask questions about your uploaded dataset "
        "and get instant answers."
    )

    if st.session_state.get("dataset") is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.get("cleaned_dataset")

        if df is None:
            df = st.session_state.dataset

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        col1, col2 = st.columns([3, 1])

        with col1:
            st.info(
                f"Dataset: {df.shape[0]:,} rows × "
                f"{df.shape[1]} columns"
            )

        with col2:
            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        # Display previous messages
        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # # Chat input
        # question = st.chat_input(
        #     "Ask something about your dataset..."
        # )

        # Suggested Questions

        st.subheader("Suggested Questions")

        suggested_questions = [
            "What is the average purchase amount?",
            "Which category has the highest sales?",
            "Which products are most popular?",
            "How many missing values are present?",
            "What are the top five locations?"
        ]

        selected_question = st.selectbox(
            "Choose a suggested question",
            suggested_questions,
            key="suggested_question"
        )

        ask_suggested = st.button(
            "Ask Suggested Question",
            key="ask_suggested_question"
        )

        # Chat input
        question = st.chat_input(
            "Ask something about your dataset..."
        )

        # Use suggested question if button is clicked
        if ask_suggested:
            question = selected_question

        if question:

            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })

            answer = answer_dataset_question(df, question)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()


elif menu == "📄 Generate Report":

    st.title("📄 Generate Business Report")

    st.write(
        "Generate downloadable PDF and Excel reports "
        "from your uploaded dataset."
    )

    if st.session_state.get("dataset") is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state.get("cleaned_dataset")

        if df is None:
            df = st.session_state.dataset

        st.subheader("Dataset Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Rows", f"{len(df):,}")

        with col2:
            st.metric("Columns", len(df.columns))

        with col3:
            st.metric(
                "Missing Values",
                int(df.isnull().sum().sum())
            )

        with col4:
            st.metric(
                "Duplicates",
                int(df.duplicated().sum())
            )

        st.divider()

        st.subheader("Choose Report Format")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### 📕 PDF Report")

            st.write(
                "Download a readable business analysis "
                "report with tables and statistics."
            )

            pdf_data = create_pdf_dataset_report(df)

            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name="business_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col2:

            st.markdown("### 📗 Excel Report")

            st.write(
                "Download the dataset with multiple "
                "analysis sheets."
            )

            excel_data = create_excel_report(df)

            st.download_button(
                label="Download Excel Report",
                data=excel_data,
                file_name="business_analysis_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        
        # Save Analysis to History

        report_df = st.session_state.cleaned_dataset

        if report_df is None:
            report_df = st.session_state.dataset

        if report_df is not None:

            if st.button("Save Analysis to History"):

                try:
                    report_text = generate_ai_insights(report_df)

                    success = save_analysis(
                        st.session_state.user["id"],
                        st.session_state.dataset_name,
                        report_df,
                        report_text
                    )

                    if success:
                        st.success("Analysis saved successfully!")

                except Exception as e:
                    st.error(f"Unable to save analysis: {e}")

       

        st.divider()

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )





elif menu == "🕘 Analysis History":

    st.title("🕘 Analysis History")

    st.write(
        "View your previously saved dataset analysis reports."
    )

    try:

        with st.spinner("Loading analysis history..."):

            history = get_user_history(
                st.session_state.user["id"]
            )

        if not history:

            st.info("No analysis history found.")

        else:

            st.subheader("Saved Analyses")

            # History overview
            st.metric(
                "Total Saved Analyses",
                len(history)
            )

            # History table
            history_df = pd.DataFrame(history)

            display_columns = [
                column for column in
                ["file_name", "created_at", "id"]
                if column in history_df.columns
            ]

            if display_columns:

                st.dataframe(
                    history_df[display_columns],
                    use_container_width=True,
                    hide_index=True
                )

            # Select saved report
            history_ids = {
                f"{item['file_name']} | {item['created_at']}":
                item["id"]
                for item in history
            }

            st.divider()

            st.subheader("View Saved Report")

            selected_history = st.selectbox(
                "Select an analysis",
                list(history_ids.keys())
            )

            if st.button("View Saved Report"):

                with st.spinner("Fetching saved report..."):

                    report = get_history_report(
                        st.session_state.user["id"],
                        history_ids[selected_history]
                    )

                if report and report.get("report_text"):

                    st.success("Report loaded successfully!")

                    st.markdown(report["report_text"])

                else:

                    st.info("No saved report available.")

    except Exception as e:

        st.error(
            f"Unable to load analysis history: {e}"
        )




