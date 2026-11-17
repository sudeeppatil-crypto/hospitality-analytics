USE hospitality_analytics;

-- ============================================================
-- HOSPITALITY ANALYTICS: GOLD AGGREGATIONS (MySQL 8.0+)
-- Source room table: fact_room_daily_v2
-- Source feedback: fact_guest_feedback
-- Source workforce events: fact_employee_events
-- ============================================================

-- 1) MONTHLY HOTEL KPIs: 5 hotels x 60 months = 300 rows
DROP TABLE IF EXISTS gold_hotel_monthly_kpis;

CREATE TABLE gold_hotel_monthly_kpis AS
WITH months AS (
    SELECT DISTINCT CAST(DATE_FORMAT(full_date, '%Y-%m-01') AS DATE) AS month_start
    FROM dim_date
    WHERE full_date BETWEEN '2021-01-01' AND '2025-12-31'
),
room_metrics AS (
    SELECT
        r.hotel_id,
        CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE) AS month_start,
        SUM(r.room_status = 'Occupied') AS occupied_room_nights,
        SUM(r.room_status IN ('Occupied', 'Available')) AS available_room_nights,
        SUM(r.room_revenue) AS total_revenue
    FROM fact_room_daily_v2 r
    JOIN dim_date d ON d.date_id = r.stay_date_id
    WHERE d.full_date BETWEEN '2021-01-01' AND '2025-12-31'
    GROUP BY r.hotel_id, CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE)
),
booking_season AS (
    -- One hotel-specific season per completed booking, based on its first occupied night.
    SELECT
        r.booking_id,
        MIN(r.hotel_id) AS hotel_id,
        SUBSTRING_INDEX(
            GROUP_CONCAT(r.season_label ORDER BY r.stay_date_id SEPARATOR ','),
            ',', 1
        ) AS season_label
    FROM fact_room_daily_v2 r
    WHERE r.booking_id IS NOT NULL
      AND r.room_status = 'Occupied'
    GROUP BY r.booking_id
),
feedback_monthly AS (
    SELECT
        f.hotel_id,
        CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE) AS month_start,
        COUNT(*) AS feedback_count,
        SUM(f.rating) AS feedback_rating_sum,
        AVG(f.rating) AS avg_guest_rating
    FROM fact_guest_feedback f
    JOIN dim_date d ON d.date_id = f.feedback_date_id
    WHERE d.full_date BETWEEN '2021-01-01' AND '2026-01-01'
    GROUP BY f.hotel_id, CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE)
)
SELECT
    h.hotel_id,
    h.hotel_name,
    h.city,
    m.month_start,
    COALESCE(r.occupied_room_nights, 0) AS occupied_room_nights,
    COALESCE(r.available_room_nights, 0) AS available_room_nights,
    COALESCE(r.total_revenue, 0) AS total_revenue,
    ROUND(100.0 * COALESCE(r.occupied_room_nights, 0) /
          NULLIF(r.available_room_nights, 0), 2) AS occupancy_rate,
    ROUND(r.total_revenue / NULLIF(r.occupied_room_nights, 0), 2) AS ADR,
    ROUND(r.total_revenue / NULLIF(r.available_room_nights, 0), 2) AS RevPAR,
    COALESCE(f.feedback_count, 0) AS feedback_count,
    COALESCE(f.feedback_rating_sum, 0) AS feedback_rating_sum,
    ROUND(f.avg_guest_rating, 2) AS guest_satisfaction_score
FROM dim_hotels h
CROSS JOIN months m
LEFT JOIN room_metrics r
    ON r.hotel_id = h.hotel_id AND r.month_start = m.month_start
LEFT JOIN feedback_monthly f
    ON f.hotel_id = h.hotel_id AND f.month_start = m.month_start;


-- 2) SEASONAL HOTEL KPIs
-- Feedback is assigned to the hotel's season at the booking's first occupied night.
DROP TABLE IF EXISTS gold_hotel_seasonal_kpis;

CREATE TABLE gold_hotel_seasonal_kpis AS
WITH room_season AS (
    SELECT
        r.hotel_id,
        r.season_label,
        SUM(r.room_status = 'Occupied') AS occupied_room_nights,
        SUM(r.room_status IN ('Occupied', 'Available')) AS available_room_nights,
        SUM(r.room_revenue) AS total_revenue
    FROM fact_room_daily_v2 r
    JOIN dim_date d ON d.date_id = r.stay_date_id
    WHERE d.full_date BETWEEN '2021-01-01' AND '2025-12-31'
    GROUP BY r.hotel_id, r.season_label
),
booking_season AS (
    SELECT
        r.booking_id,
        MIN(r.hotel_id) AS hotel_id,
        SUBSTRING_INDEX(
            GROUP_CONCAT(r.season_label ORDER BY r.stay_date_id SEPARATOR ','),
            ',', 1
        ) AS season_label
    FROM fact_room_daily_v2 r
    WHERE r.booking_id IS NOT NULL
      AND r.room_status = 'Occupied'
    GROUP BY r.booking_id
),
feedback_season AS (
    SELECT
        bs.hotel_id,
        bs.season_label,
        COUNT(*) AS feedback_count,
        SUM(f.rating) AS feedback_rating_sum,
        AVG(f.rating) AS guest_satisfaction_score
    FROM fact_guest_feedback f
    JOIN booking_season bs ON bs.booking_id = f.booking_id
    GROUP BY bs.hotel_id, bs.season_label
)
SELECT
    h.hotel_id,
    h.hotel_name,
    h.city,
    rs.season_label,
    rs.occupied_room_nights,
    rs.available_room_nights,
    rs.total_revenue,
    ROUND(100.0 * rs.occupied_room_nights /
          NULLIF(rs.available_room_nights, 0), 2) AS occupancy_rate,
    ROUND(rs.total_revenue / NULLIF(rs.occupied_room_nights, 0), 2) AS ADR,
    ROUND(rs.total_revenue / NULLIF(rs.available_room_nights, 0), 2) AS RevPAR,
    COALESCE(fs.feedback_count, 0) AS feedback_count,
    COALESCE(fs.feedback_rating_sum, 0) AS feedback_rating_sum,
    ROUND(fs.guest_satisfaction_score, 2) AS guest_satisfaction_score
FROM room_season rs
JOIN dim_hotels h ON h.hotel_id = rs.hotel_id
LEFT JOIN feedback_season fs
    ON fs.hotel_id = rs.hotel_id
   AND fs.season_label = rs.season_label;


-- 3) MONTHLY EMPLOYEE TURNOVER
-- Headcount is reconstructed from HIRE (+1) and TERMINATION (-1) events.
DROP TABLE IF EXISTS gold_employee_turnover_monthly;

CREATE TABLE gold_employee_turnover_monthly AS
WITH months AS (
    SELECT DISTINCT CAST(DATE_FORMAT(full_date, '%Y-%m-01') AS DATE) AS month_start
    FROM dim_date
    WHERE full_date BETWEEN '2021-01-01' AND '2025-12-31'
),
hotel_months AS (
    SELECT h.hotel_id, h.hotel_name, m.month_start
    FROM dim_hotels h CROSS JOIN months m
),
events_by_month AS (
    SELECT
        e.hotel_id,
        CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE) AS month_start,
        SUM(ev.event_type = 'HIRE') AS hires,
        SUM(ev.event_type = 'TERMINATION') AS terminations
    FROM fact_employee_events ev
    JOIN dim_employees e ON e.employee_id = ev.employee_id
    JOIN dim_date d ON d.date_id = ev.event_date_id
    WHERE d.full_date BETWEEN '2021-01-01' AND '2025-12-31'
    GROUP BY e.hotel_id, CAST(DATE_FORMAT(d.full_date, '%Y-%m-01') AS DATE)
),
headcount_before AS (
    SELECT
        e.hotel_id,
        SUM(CASE WHEN ev.event_type = 'HIRE' THEN 1
                 WHEN ev.event_type = 'TERMINATION' THEN -1 ELSE 0 END) AS headcount_before_period
    FROM fact_employee_events ev
    JOIN dim_employees e ON e.employee_id = ev.employee_id
    JOIN dim_date d ON d.date_id = ev.event_date_id
    WHERE d.full_date < '2021-01-01'
    GROUP BY e.hotel_id
),
monthly_running AS (
    SELECT
        hm.hotel_id,
        hm.hotel_name,
        hm.month_start,
        COALESCE(hb.headcount_before_period, 0)
        + COALESCE(
            SUM(COALESCE(em.hires, 0) - COALESCE(em.terminations, 0))
            OVER (
                PARTITION BY hm.hotel_id
                ORDER BY hm.month_start
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ), 0
          ) AS starting_headcount,
        COALESCE(em.hires, 0) AS hires,
        COALESCE(em.terminations, 0) AS terminations
    FROM hotel_months hm
    LEFT JOIN headcount_before hb ON hb.hotel_id = hm.hotel_id
    LEFT JOIN events_by_month em
        ON em.hotel_id = hm.hotel_id AND em.month_start = hm.month_start
),
monthly_with_season AS (
    SELECT
        mr.*,
        COALESCE(
            (SELECT MAX(rd.season_label)
             FROM fact_room_daily_v2 rd
             JOIN dim_date dd ON dd.date_id = rd.stay_date_id
             WHERE rd.hotel_id = mr.hotel_id
               AND dd.full_date >= mr.month_start
               AND dd.full_date < DATE_ADD(mr.month_start, INTERVAL 1 MONTH)),
            'Pre-Opening'
        ) AS season_label
    FROM monthly_running mr
)
SELECT
    hotel_id,
    hotel_name,
    month_start,
    season_label,
    starting_headcount,
    hires,
    terminations,
    starting_headcount + hires - terminations AS ending_headcount,
    ROUND((starting_headcount +
          (starting_headcount + hires - terminations)) / 2.0, 2) AS average_headcount,
    ROUND(
        100.0 * terminations /
        NULLIF((starting_headcount +
               (starting_headcount + hires - terminations)) / 2.0, 0),
        2
    ) AS turnover_rate
FROM monthly_with_season;


-- 4) SEASONAL EMPLOYEE TURNOVER
-- Rate = season terminations / average monthly headcount during that season.
DROP TABLE IF EXISTS gold_employee_turnover_seasonal;

CREATE TABLE gold_employee_turnover_seasonal AS
SELECT
    hotel_id,
    hotel_name,
    season_label,
    COUNT(*) AS months_in_season,
    SUM(hires) AS total_hires,
    SUM(terminations) AS total_terminations,
    ROUND(AVG(average_headcount), 2) AS avg_monthly_headcount,
    ROUND(
        100.0 * SUM(terminations) /
        NULLIF(AVG(average_headcount), 0),
        2
    ) AS turnover_rate
FROM gold_employee_turnover_monthly
GROUP BY hotel_id, hotel_name, season_label;


-- 5) VALIDATION QUERIES
SELECT COUNT(*) AS monthly_hotel_rows FROM gold_hotel_monthly_kpis;
SELECT COUNT(*) AS seasonal_hotel_rows FROM gold_hotel_seasonal_kpis;
SELECT COUNT(*) AS monthly_employee_rows FROM gold_employee_turnover_monthly;
SELECT COUNT(*) AS seasonal_employee_rows FROM gold_employee_turnover_seasonal;

SELECT
    MIN(month_start) AS first_month,
    MAX(month_start) AS last_month,
    SUM(occupancy_rate IS NOT NULL AND (occupancy_rate < 0 OR occupancy_rate > 100))
        AS invalid_occupancy_rows
FROM gold_hotel_monthly_kpis;

SELECT *
FROM gold_hotel_seasonal_kpis
ORDER BY hotel_name, season_label;

SELECT *
FROM gold_employee_turnover_seasonal
ORDER BY hotel_name, season_label;
