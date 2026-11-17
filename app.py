import os
import io
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv

# ------------------------------------------------------------
# Configuration and database
# ------------------------------------------------------------
st.set_page_config(
    page_title="Hospitality Analytics",
    page_icon="🏨",
    layout="wide"
)
load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
    background: rgba(128,128,128,0.08);
    border: 1px solid rgba(128,128,128,0.18);
    padding: 14px 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing .env settings: {', '.join(missing)}")
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME")
    )
    return create_engine(url, pool_pre_ping=True)

@st.cache_data(ttl=300)
def load_tables():
    engine = get_engine()
    queries = {
        "monthly": "SELECT * FROM gold_hotel_monthly_kpis",
        "seasonal": "SELECT * FROM gold_hotel_seasonal_kpis",
        "employee_monthly": "SELECT * FROM gold_employee_turnover_monthly"
    }
    result = {}
    with engine.connect() as conn:
        for key, query in queries.items():
            result[key] = pd.read_sql_query(query, conn)
    for key in result:
        if "month_start" in result[key].columns:
            result[key]["month_start"] = pd.to_datetime(result[key]["month_start"])
    return result

st.title("🏨 Hospitality Analytics Dashboard")
st.caption("Five-year hotel performance | Seasonal demand | Guest experience | Workforce")

try:
    data = load_tables()
except Exception as exc:
    st.error(f"Could not load Gold tables: {exc}")
    st.info("Run sql/01_gold_aggregations.sql in MySQL Workbench, then refresh this app.")
    st.stop()

monthly = data["monthly"]
seasonal = data["seasonal"]
emp_monthly = data["employee_monthly"]

if monthly.empty:
    st.error("The hotel monthly Gold table has no records.")
    st.stop()

# ------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------
st.sidebar.header("Dashboard filters")
hotels = sorted(monthly["hotel_name"].dropna().unique().tolist())
selected_hotels = st.sidebar.multiselect("Hotels", hotels, default=hotels)
if not selected_hotels:
    st.warning("Select at least one hotel.")
    st.stop()

min_month = monthly["month_start"].min().date()
max_month = monthly["month_start"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_month, max_month),
    min_value=min_month,
    max_value=max_month
)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_month, max_month
if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

start_ts = pd.Timestamp(start_date).replace(day=1)
end_ts = pd.Timestamp(end_date).replace(day=1)

m = monthly[
    monthly["hotel_name"].isin(selected_hotels)
    & monthly["month_start"].between(start_ts, end_ts)
].copy()
em = emp_monthly[
    emp_monthly["hotel_name"].isin(selected_hotels)
    & emp_monthly["month_start"].between(start_ts, end_ts)
].copy()
s = seasonal[seasonal["hotel_name"].isin(selected_hotels)].copy()

if m.empty:
    st.warning("No data exists for the selected filters.")
    st.stop()

# ------------------------------------------------------------
# Correct weighted KPIs
# ------------------------------------------------------------
occupied = m["occupied_room_nights"].sum()
available = m["available_room_nights"].sum()
revenue = m["total_revenue"].sum()
feedback_n = m["feedback_count"].sum()
feedback_sum = m["feedback_rating_sum"].sum()

occupancy = 100 * occupied / available if available else 0
adr = revenue / occupied if occupied else 0
revpar = revenue / available if available else 0
guest_rating = feedback_sum / feedback_n if feedback_n else 0

if not em.empty:
    # Monthly portfolio turnover: sum exits / sum average headcount.
    total_exits = em["terminations"].sum()
    headcount_months = em["average_headcount"].sum()
    turnover = 100 * total_exits / headcount_months if headcount_months else 0
else:
    turnover = 0

# ------------------------------------------------------------
# Overview
# ------------------------------------------------------------
st.subheader("Business KPI overview")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Occupancy rate", f"{occupancy:.1f}%")
c2.metric("ADR", f"₹{adr:,.0f}")
c3.metric("RevPAR", f"₹{revpar:,.0f}")
c4.metric("Guest satisfaction", f"{guest_rating:.2f} / 5")
c5.metric("Employee turnover", f"{turnover:.2f}%")

st.caption(
    f"Selected period: {start_ts:%b %Y} – {end_ts:%b %Y} | "
    f"Hotels selected: {len(selected_hotels)}"
)

# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Monthly trends", "Seasonal analysis",
    "Workforce", "Data tables"
])

with tab1:
    st.subheader("Hotel comparison")
    comp = (
        m.groupby(["hotel_name", "city"], as_index=False)
        .agg(
            occupied=("occupied_room_nights", "sum"),
            available=("available_room_nights", "sum"),
            revenue=("total_revenue", "sum"),
            rating_sum=("feedback_rating_sum", "sum"),
            feedback_count=("feedback_count", "sum")
        )
    )
    comp["Occupancy (%)"] = 100 * comp["occupied"] / comp["available"].replace(0, pd.NA)
    comp["ADR (₹)"] = comp["revenue"] / comp["occupied"].replace(0, pd.NA)
    comp["RevPAR (₹)"] = comp["revenue"] / comp["available"].replace(0, pd.NA)
    comp["Guest rating"] = comp["rating_sum"] / comp["feedback_count"].replace(0, pd.NA)

    left, right = st.columns(2)
    with left:
        fig = px.bar(comp, x="hotel_name", y="Occupancy (%)", color="city",
                     title="Occupancy by hotel", text_auto=".1f")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(comp, x="hotel_name", y="RevPAR (₹)", color="city",
                     title="RevPAR by hotel", text_auto=".0f")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        comp[["hotel_name", "city", "Occupancy (%)", "ADR (₹)",
              "RevPAR (₹)", "Guest rating", "revenue"]].round(2),
        use_container_width=True, hide_index=True
    )

with tab2:
    st.subheader("Monthly KPI trends")
    trend = (
        m.groupby("month_start", as_index=False)
        .agg(
            occupied=("occupied_room_nights", "sum"),
            available=("available_room_nights", "sum"),
            revenue=("total_revenue", "sum"),
            rating_sum=("feedback_rating_sum", "sum"),
            feedback_count=("feedback_count", "sum")
        )
    )
    trend["Occupancy (%)"] = 100 * trend["occupied"] / trend["available"].replace(0, pd.NA)
    trend["ADR (₹)"] = trend["revenue"] / trend["occupied"].replace(0, pd.NA)
    trend["RevPAR (₹)"] = trend["revenue"] / trend["available"].replace(0, pd.NA)
    trend["Guest rating"] = trend["rating_sum"] / trend["feedback_count"].replace(0, pd.NA)

    fig = px.line(trend, x="month_start", y="Occupancy (%)", markers=True,
                  title="Monthly occupancy rate")
    st.plotly_chart(fig, use_container_width=True)

    rev = trend.melt(id_vars="month_start",
                     value_vars=["ADR (₹)", "RevPAR (₹)"],
                     var_name="Metric", value_name="Amount")
    fig = px.line(rev, x="month_start", y="Amount", color="Metric",
                  markers=True, title="ADR and RevPAR over time")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(trend, x="month_start", y="Guest rating", markers=True,
                  title="Monthly guest satisfaction")
    fig.update_yaxes(range=[0, 5])
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Seasonal KPI comparison")
    if s.empty:
        st.warning("No seasonal hotel data available.")
    else:
        season_order = ["Peak", "Shoulder", "Off-season", "Pre-Opening"]
        if "season_label" in s.columns:
            available_seasons = [x for x in season_order if x in s["season_label"].unique()]
            available_seasons += sorted(set(s["season_label"].dropna()) - set(available_seasons))
            season_pick = st.multiselect("Season", available_seasons, default=available_seasons)
            ss = s[s["season_label"].isin(season_pick)].copy()
        else:
            ss = s.copy()

        left, right = st.columns(2)
        with left:
            fig = px.bar(ss, x="hotel_name", y="occupancy_rate",
                         color="season_label", barmode="group",
                         title="Occupancy by hotel and season",
                         labels={"occupancy_rate": "Occupancy (%)"})
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(ss, x="hotel_name", y="ADR",
                         color="season_label", barmode="group",
                         title="ADR by hotel and season",
                         labels={"ADR": "ADR (₹)"})
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        with left:
            fig = px.bar(ss, x="hotel_name", y="RevPAR",
                         color="season_label", barmode="group",
                         title="RevPAR by hotel and season",
                         labels={"RevPAR": "RevPAR (₹)"})
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(ss, x="hotel_name", y="guest_satisfaction_score",
                         color="season_label", barmode="group",
                         title="Guest satisfaction by season",
                         labels={"guest_satisfaction_score": "Average rating"})
            fig.update_yaxes(range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Seasonal hotel KPI data**")
        st.dataframe(ss.round(2), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Employee turnover")
    if em.empty:
        st.warning("No employee event data for the selected period.")
    else:
        workforce = (
            em.groupby("month_start", as_index=False)
            .agg(
                terminations=("terminations", "sum"),
                hires=("hires", "sum"),
                average_headcount=("average_headcount", "sum")
            )
        )
        workforce["Turnover (%)"] = (
            100 * workforce["terminations"] /
            workforce["average_headcount"].replace(0, pd.NA)
        )
        fig = px.line(workforce, x="month_start", y="Turnover (%)",
                      markers=True, title="Monthly employee turnover")
        st.plotly_chart(fig, use_container_width=True)


        employee_hotel = (
            em.groupby("hotel_name", as_index=False)
            .agg(Hires=("hires", "sum"),
                 Terminations=("terminations", "sum"),
                 Average_headcount_months=("average_headcount", "sum"))
        )
        st.dataframe(employee_hotel, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Monthly hotel KPI records")
    st.dataframe(m.sort_values(["month_start", "hotel_name"]),
                 use_container_width=True, hide_index=True)
    st.subheader("Monthly employee records")
    st.dataframe(em.sort_values(["month_start", "hotel_name"]),
                 use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Dynamic inference report download
# ------------------------------------------------------------
def safe_change(new, old):
    if pd.isna(old) or old == 0:
        return None
    return (new - old) / abs(old) * 100

def build_inference_report():
    lines = [
        "# Hospitality Analytics – Inference Report",
        "",
        f"**Analysis period:** {start_ts:%B %Y} to {end_ts:%B %Y}",
        f"**Hotels included:** {', '.join(selected_hotels)}",
        "",
        "## KPI summary",
        f"- Occupancy rate: **{occupancy:.2f}%**",
        f"- ADR: **₹{adr:,.2f}**",
        f"- RevPAR: **₹{revpar:,.2f}**",
        f"- Guest satisfaction: **{guest_rating:.2f}/5** ({int(feedback_n):,} feedback records)",
        f"- Employee turnover: **{turnover:.2f}%** (period exits divided by summed monthly average headcount)",
        "",
        "## Hotel comparison"
    ]
    if not comp.empty:
        for _, row in comp.sort_values("Occupancy (%)", ascending=False).iterrows():
            lines.append(
                f"- **{row['hotel_name']} ({row['city']}):** "
                f"occupancy {row['Occupancy (%)']:.2f}%, "
                f"ADR ₹{row['ADR (₹)']:,.2f}, "
                f"RevPAR ₹{row['RevPAR (₹)']:,.2f}, "
                f"guest rating {row['Guest rating']:.2f}/5."
            )
    lines += ["", "## Seasonal observations"]
    if not s.empty:
        seasonal_filtered = s[s["hotel_name"].isin(selected_hotels)]
        for _, row in seasonal_filtered.iterrows():
            lines.append(
                f"- **{row['hotel_name']} – {row['season_label']}:** "
                f"occupancy {row['occupancy_rate']:.2f}%, "
                f"ADR ₹{row['ADR']:,.2f}, "
                f"RevPAR ₹{row['RevPAR']:,.2f}, "
                f"guest rating "
                f"{row['guest_satisfaction_score'] if pd.notna(row['guest_satisfaction_score']) else 'N/A'}."
            )
    lines += [
        "",
        "## Interpretation guidance",
        "- Compare peak, shoulder and off-season occupancy to assess demand seasonality.",
        "- Compare ADR with occupancy: a higher ADR alongside stable occupancy may indicate pricing power.",
        "- RevPAR combines room pricing and occupancy and is useful for revenue performance comparisons.",
        "- Review guest ratings alongside occupancy to identify whether crowding or service capacity may affect experience.",
        "- Compare employee exits with average headcount and season to investigate seasonal staffing pressure.",
        "",
        "## Limitations and methodology",
        "- Occupancy denominator includes Occupied and Available room nights; Out_of_Order rooms are excluded.",
        "- ADR = room revenue / occupied room nights.",
        "- RevPAR = room revenue / available room nights.",
        "- Guest satisfaction is a weighted mean of submitted category feedback ratings.",
        "- Employee turnover is calculated from event-based headcount. The portfolio KPI uses total terminations divided by summed monthly average headcount for the selected months; it is a period ratio, not an annualized rate.",
        "- Seasonal labels are hotel-specific and come from the generated room-night data. The feedback season is assigned using the booking's first occupied night.",
        "- Seasonal patterns are descriptive associations; they do not prove that seasonality alone caused the KPI movement."
    ]
    return "\n".join(lines)

st.divider()
st.download_button(
    "📄 Download inference report (Markdown)",
    data=build_inference_report(),
    file_name="hospitality_inference_report.md",
    mime="text/markdown"
)
st.caption("Hospitality Analytics | MySQL • Python • Pandas • Plotly • Streamlit")