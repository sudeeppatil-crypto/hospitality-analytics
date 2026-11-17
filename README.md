# Hospitality Analytics – End-to-End Data Analytics Project

## 1. Project Overview

The **Hospitality Analytics Project** is an end-to-end data analytics solution designed to analyze hotel operations, revenue performance, guest satisfaction, and employee turnover across multiple hotels in India.

The project uses five years of generated hospitality data (2021–2025) to identify business trends, seasonal patterns, operational inefficiencies, and opportunities for revenue optimization.

The solution follows a dimensional data modeling approach and includes:

- Relational database design using MySQL.
- Synthetic data generation using Python and Pandas.
- Data validation and transformation using SQL.
- Gold-layer analytical tables for business reporting.
- Interactive dashboard development using Streamlit and Plotly.
- Business insights and recommendations based on analytical findings.

## 2. Business Objectives

The primary objective is to help hotel management understand business performance and make data-driven decisions.

The project focuses on five major business KPIs:

1. **Occupancy Rate:** Measures how efficiently hotel room inventory is being utilized.
2. **Average Daily Rate (ADR):** Measures the average revenue generated per occupied room.
3. **Revenue per Available Room (RevPAR):** Measures revenue performance across available room inventory.
4. **Guest Satisfaction Score:** Measures customer experience using guest feedback ratings.
5. **Employee Turnover Rate:** Measures employee attrition and workforce stability.

### Key Business Questions

- Which hotels have the highest occupancy rates?
- How does hotel revenue change month over month and year over year?
- Which seasons generate the highest revenue?
- Which hotels have the highest ADR and RevPAR?
- How does guest satisfaction vary across hotels?
- Are guest satisfaction scores correlated with hotel performance?
- During which months is employee turnover highest?
- Which departments experience higher employee attrition?
- Are there seasonal patterns in employee turnover?

## 3. Project Scope

| Parameter | Details |
|---|---|
| Industry | Hospitality |
| Geography | India |
| Analysis Period | January 2021 – December 2025 |
| Duration | 5 Years |
| Hotels | 5 |
| Approximate Rooms | 500 |
| Guests | Approximately 10,000 |
| Employees | Approximately 500 |
| Currency | INR |
| Database | MySQL |
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Dashboard | Streamlit |
| Visualization | Plotly |

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and processing |
| Pandas | Data manipulation and transformation |
| NumPy | Numerical operations and statistical distributions |
| UUID | Generation of unique identifiers |
| MySQL | Relational database storage |
| SQL | Data validation, aggregation, and analytics |
| SQLAlchemy | Database connectivity |
| Streamlit | Interactive dashboard development |
| Plotly | Interactive charts and visualizations |
| Git & GitHub | Version control and project management |

## 5. Data Architecture

The project follows a dimensional modeling approach using fact and dimension tables.

The architecture is organized into three logical layers:

### Layer 1 – Data Generation

Python and Pandas are used to generate realistic synthetic hospitality data covering five years.

The generated datasets incorporate:

- Seasonal demand variations.
- Monthly and yearly business trends.
- Different hotel performance characteristics.
- Realistic guest and employee information.
- Booking cancellations and no-shows.
- Room availability and occupancy.
- Guest feedback and ratings.
- Employee joining and exit events.

### Layer 2 – Database and Analytics

Generated datasets are loaded into MySQL.

SQL transformations are used to:

- Validate data quality.
- Check primary and foreign key relationships.
- Calculate operational metrics.
- Aggregate data at monthly, seasonal, and yearly levels.
- Create analytical Gold tables.

### Layer 3 – Dashboard and Reporting

The Streamlit dashboard connects to MySQL and retrieves the analytical Gold tables.

Pandas and Plotly are used to process and visualize the data through interactive KPI cards, charts, filters, and comparisons.

## 6. Dimensional Data Model

The project uses a nine-table dimensional model consisting of five dimension tables and four fact tables.

### Dimension Tables

| Table | Description |
|---|---|
| dim_hotels | Stores hotel details, location, and hotel attributes |
| dim_rooms | Stores room information, room categories, and room attributes |
| dim_guests | Stores guest information and guest attributes |
| dim_employees | Stores employee details, department, designation, and employment information |
| dim_date | Stores calendar information for daily, monthly, quarterly, and yearly analysis |

### Fact Tables

| Table | Grain | Description |
|---|---|---|
| fact_bookings | One room reservation | Stores booking information, booking status, guest, hotel, and room details |
| fact_room_daily | One room per calendar date | Stores daily room status and revenue information |
| fact_guest_feedback | One feedback submission | Stores guest ratings, feedback categories, and comments |
| fact_employee_events | One employee event | Stores employee-related events such as joining and exit |

### Important Modeling Decisions

- UUID-based identifiers are used for business entities.
- Date identifiers follow the YYYYMMDD format.
- Fact tables maintain relationships with relevant dimension tables.
- `fact_room_daily` has a room-date grain.
- A room can have only one daily record for a particular date.
- The room-date combination is treated as a unique business key.
- Room statuses include Occupied, Available, and Out_of_Order.
- Revenue is recorded for occupied room-days.
- Out-of-order rooms are excluded from the available-room denominator when calculating occupancy.

## 7. Data Generation Using Python

Synthetic data is generated using Python, Pandas, NumPy, and UUID.

The dataset covers five years, from January 2021 through December 2025.

### Data Generation Requirements

The generated data incorporates:

1. Realistic hotel names and locations.
2. Unique hotel, room, guest, booking, and employee identifiers.
3. Realistic room categories and room attributes.
4. Guest booking behavior.
5. Booking statuses such as Checked-out, Cancelled, and No-show.
6. Daily room occupancy and availability.
7. Guest satisfaction ratings.
8. Employee joining and exit events.
9. Monthly and seasonal variations.
10. Long-term business trends across the five-year period.

### Seasonal and Trend Variations

The generated data incorporates seasonal patterns to simulate realistic hospitality business behavior.

Examples include:

- Higher booking demand during peak travel seasons.
- Changes in occupancy across different months.
- Variations in room revenue based on seasonal demand.
- Different performance patterns across hotels.
- Changes in employee turnover over time.

The objective is to create a dataset that supports meaningful business analysis rather than purely random records.

## 8. Key Performance Indicators (KPIs)

### 8.1 Occupancy Rate

Measures the percentage of available rooms that are occupied.

**Formula:**

Occupancy Rate (%) = (Occupied Room Days / Available Room Days) × 100

Out-of-order rooms are excluded from the available-room denominator.

### 8.2 Average Daily Rate (ADR)

Measures the average room revenue earned per occupied room.

**Formula:**

ADR = Total Room Revenue / Occupied Room Days

### 8.3 Revenue per Available Room (RevPAR)

Measures the revenue generated per available room.

**Formula:**

RevPAR = Total Room Revenue / Available Room Days

Alternatively:

RevPAR = ADR × Occupancy Rate

For this formula, occupancy rate must be expressed as a decimal.

### 8.4 Guest Satisfaction Score

Measures the average guest rating.

**Formula:**

Guest Satisfaction Score = Sum of Valid Guest Ratings / Number of Valid Feedback Submissions

Ratings are measured on a scale of 1 to 5.

### 8.5 Employee Turnover Rate

Measures employee exits relative to the average workforce during a reporting period.

**Formula:**

Employee Turnover Rate (%) = (Employee Exits During Period / Average Employee Headcount During Period) × 100

Average Headcount = (Opening Headcount + Closing Headcount) / 2

The reporting logic should account for employee joining and exit dates when calculating workforce headcount.

## 9. SQL Analytics and Gold Layer

SQL is used to transform the generated datasets into business-ready analytical tables.

The Gold layer contains aggregated metrics that can be directly consumed by the dashboard.

### Analytical Aggregations

The project includes analysis at different reporting levels:

- Monthly hotel performance.
- Seasonal hotel performance.
- Monthly employee turnover.
- Seasonal employee turnover.
- Hotel-level KPI comparisons.
- Historical performance trends.

### Gold Layer Outputs

The analytical layer is designed to provide:

| Analytical Output | Purpose |
|---|---|
| Monthly Hotel KPIs | Tracks occupancy, ADR, RevPAR, and guest satisfaction |
| Monthly Employee Turnover | Tracks workforce movement and monthly attrition |
| Seasonal Hotel Performance | Compares hotel performance across seasons |
| Seasonal Employee Turnover | Identifies seasonal workforce attrition patterns |

The Gold tables are stored in MySQL and consumed by the Streamlit dashboard.

## 10. Interactive Dashboard

The project includes an interactive Streamlit dashboard that connects to MySQL and retrieves Gold-layer analytical data.

### Dashboard Capabilities

- KPI summary cards.
- Monthly performance trends.
- Hotel-level comparisons.
- Seasonal performance analysis.
- Employee turnover analysis.
- Interactive filtering.
- Historical trend visualization.
- Business performance comparisons.

### Dashboard KPIs

The dashboard focuses on the following five business areas:

**1. Occupancy Performance**
- Occupancy rate trends.
- Hotel-wise occupancy comparison.
- Monthly and seasonal occupancy patterns.

**2. Revenue Performance**
- ADR trends.
- RevPAR trends.
- Hotel-wise revenue comparisons.
- Monthly revenue performance.

**3. Guest Satisfaction**
- Average guest satisfaction.
- Hotel-wise rating comparison.
- Guest satisfaction trends.

**4. Employee Turnover**
- Monthly employee exits.
- Employee turnover rate.
- Seasonal attrition patterns.
- Hotel or department-level comparisons where available.

**5. Overall Hotel Performance**
- Consolidated KPI monitoring.
- Historical performance analysis.
- Comparisons across reporting periods.

## 11. Project Structure

The project is organized into data generation, database, analytics, and dashboard components.

```text
hospitality_analytics/
│
├── data/
│   ├── dim_hotels.csv
│   ├── dim_rooms.csv
│   ├── dim_guests.csv
│   ├── dim_employees.csv
│   ├── dim_date.csv
│   ├── fact_bookings.csv
│   ├── fact_room_daily.csv
│   ├── fact_guest_feedback.csv
│   └── fact_employee_events.csv
│
├── scripts/
│   ├── data generation scripts
│   ├── database loading scripts
│   └── data validation scripts
│
├── sql/
│   ├── database_schema.sql
│   ├── silver_transformations.sql
│   └── gold_transformations.sql
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

*Note: The structure above describes the logical organization. Actual script and SQL filenames may differ in the repository.*

## 12. Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or later.
- MySQL Server.
- Git.
- pip.

### Step 1 – Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd hospitality_analytics
```

### Step 2 – Create a Virtual Environment

```bash
python3 -m venv venv
```

Activate the environment.

For Linux/macOS:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### Step 3 – Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 – Create the MySQL Database

Open MySQL:

```sql
CREATE DATABASE hospitality_analytics;
```

Use the database:

```sql
USE hospitality_analytics;
```

Execute the project's database schema SQL file to create the required dimension and fact tables.

### Step 5 – Generate and Load Data

Run the Python data-generation scripts included in the project.

The generated CSV files should be loaded into the corresponding MySQL dimension and fact tables.

Ensure the data-generation and loading steps are completed before executing the analytical SQL transformations.

### Step 6 – Execute SQL Transformations

Execute the SQL transformation scripts in the correct order:

1. Create and populate the database tables.
2. Perform data validation.
3. Execute the required Silver-layer transformations, if applicable.
4. Create and populate the Gold analytical tables.

Verify that the required Gold tables exist and contain data before starting the dashboard.

### Step 7 – Configure Database Connection

Configure the MySQL connection using environment variables or the project's existing database configuration.

Example `.env` configuration:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=hospitality_analytics
```

Do not commit your `.env` file or database credentials to GitHub.

### Step 8 – Run the Streamlit Dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## 13. Data Validation and Quality Checks

Data quality is an important part of the analytics pipeline.

The following validations are considered:

- Primary key uniqueness.
- Foreign key consistency.
- Missing-value checks.
- Duplicate record checks.
- Valid date ranges.
- Valid booking statuses.
- Valid room statuses.
- Guest ratings within the 1–5 range.
- Consistency between room, hotel, booking, and guest identifiers.
- One room record per room per date in the daily room fact.
- Correct treatment of occupied, available, and out-of-order rooms.
- Correct calculation of room revenue and occupancy metrics.
- Correct employee joining and exit dates.

## 14. Business Insights and Recommendations

The analytical outputs can help hotel management make decisions in the following areas.

### Revenue Optimization

- Identify hotels with lower ADR or RevPAR.
- Understand seasonal revenue fluctuations.
- Evaluate pricing and room utilization opportunities.
- Identify periods with stronger revenue potential.

### Operational Efficiency

- Monitor occupancy and room availability.
- Identify underutilized room inventory.
- Compare operational performance across hotels.
- Understand the impact of out-of-order rooms.

### Guest Experience

- Identify hotels with lower satisfaction scores.
- Monitor guest feedback trends.
- Identify potential service-quality improvement areas.

### Workforce Management

- Identify months with high employee turnover.
- Compare workforce stability across hotels.
- Understand seasonal staffing requirements.
- Support better employee retention planning.

## 15. Expected Project Deliverables

The project is designed to deliver:

1. MySQL database with a dimensional data model.
2. Five years of synthetic hospitality data.
3. Python scripts for data generation and processing.
4. SQL transformations and analytical aggregations.
5. Gold-layer KPI tables.
6. Interactive Streamlit dashboard.
7. Business insights and recommendations.
8. Project documentation.

## 16. Future Enhancements

Potential future improvements include:

- Forecasting occupancy and revenue using time-series models.
- Predicting booking cancellations.
- Forecasting employee turnover.
- Guest segmentation using clustering.
- Identifying factors influencing guest satisfaction.
- Automated data pipeline scheduling.
- Role-based dashboard access.
- Cloud deployment of the dashboard and database.

## 17. Conclusion

The Hospitality Analytics Project demonstrates an end-to-end data analytics workflow, starting from synthetic data generation and dimensional modeling to SQL-based analytical transformations and interactive dashboard development.

By analyzing five years of hospitality data, the solution helps monitor hotel performance, understand revenue trends, improve guest experience, and evaluate employee turnover.

The project demonstrates practical skills in Python, Pandas, MySQL, SQL analytics, dimensional modeling, data validation, and dashboard development.

---

**Project Domain:** Hospitality Analytics  
**Analysis Period:** 2021–2025  
**Database:** MySQL  
**Language:** Python  
**Dashboard:** Streamlit  
**Visualization:** Plotly  
**Status:** Project implementation and documentation