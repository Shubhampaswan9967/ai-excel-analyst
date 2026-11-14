# AI Excel Analyst – Smart Data Insight

An interactive web-based data analysis application built using Python and Streamlit. It helps users upload CSV and Excel datasets, explore data, clean data, perform analysis, generate AI-powered business insights, and download reports.

## Project Overview

AI Excel Analyst is designed to simplify the data analysis workflow through an interactive interface. Users can upload datasets, understand data quality, perform cleaning operations, explore numerical and categorical information, generate business insights, and export analysis reports.

The application also includes user authentication and analysis history.

## Features

### 1. User Authentication
- User registration
- User login
- Secure password hashing
- Forgot password using email OTP
- Logout functionality

### 2. Home Dashboard
- Dataset overview
- Total rows and columns
- Missing values count
- Duplicate rows count
- Active dataset information

### 3. Dataset Upload
- Upload CSV files
- Upload Excel files
- Select Excel worksheets
- Dataset loading and validation
- File size information

### 4. Data Preview
- Dataset preview
- Dataset information
- Column data types
- Missing values report
- Numerical and categorical columns
- Numerical statistics

### 5. Data Cleaning
- Handle missing numerical values
- Handle missing categorical values
- Remove duplicate rows
- Clean text whitespace
- Convert column data types
- Detect outliers using the IQR method
- Before-and-after data comparison
- Download cleaned CSV and Excel files

### 6. Data Analysis
- Dataset overview
- Numerical analysis
- Categorical analysis
- Top 5 values analysis
- Correlation analysis
- Correlation heatmap
- Automatic business insights

### 7. AI-Powered Business Insights
- Generate AI-powered insights from dataset statistics
- Display business analysis reports
- Download insights in Markdown and PDF formats

### 8. Ask AI
- Ask questions about the uploaded dataset
- Get answers through an interactive chat interface
- View previous chat messages
- Clear chat history

### 9. Report Generation
- Generate PDF reports
- Generate Excel reports
- View dataset summary
- Download business analysis reports
- Save analysis to history

### 10. Analysis History
- Save previous analyses
- View user-specific analysis history
- Select saved analyses
- View saved reports

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data manipulation and analysis |
| Plotly | Interactive charts and visualizations |
| MySQL | Database management |
| ReportLab | PDF report generation |
| XlsxWriter | Excel report generation |
| Bcrypt | Password hashing |
| OpenAI API | AI-powered insights and dataset question answering |

## Project Structure

```text
AI_Excel_Analyst/
│
├── app.py
├── requirements.txt
│
├── modules/
│   ├── auth.py
│   ├── database.py
│   ├── data_loader.py
│   ├── data_profiler.py
│   ├── data_cleaner.py
│   ├── data_analyzer.py
│   ├── ai_insights.py
│   ├── data_qa.py
│   ├── report_generator.py
│   ├── history.py
│   └── __init__.py
│
├── database/
│   └── schema.sql
│
├── pages/
├── reports/
└── uploads/
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Folder

```bash
cd AI_Excel_Analyst
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the database, email and AI API credentials required by the application.

Do not upload your actual passwords, API keys, or email app passwords to GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

## Database

The application uses MySQL for user authentication and analysis history.

Database tables include user accounts, analysis history, and password reset OTP records.

## Project Objective

The objective of AI Excel Analyst is to provide an interactive platform that combines data uploading, data profiling, data cleaning, exploratory data analysis, AI-powered insights, and automated report generation in one application.

## Author

**Paswan Shubham Rambadan**

B.Tech – Computer Science and Engineering

GitHub: [Shubhampaswan9967](https://github.com/Shubhampaswan9967)

LinkedIn: [Paswan Shubham](https://www.linkedin.com/in/paswanshubham9967)  
