
USE hospitality_analytics;

DROP TABLE IF EXISTS gold_employee_turnover_monthly;

CREATE TABLE gold_employee_turnover_monthly AS

WITH RECURSIVE months AS (
    SELECT DATE('2021-01-01') AS month_start

    UNION ALL

    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM months
    WHERE month_start < '2025-12-01'
),

hotel_months AS (
    SELECT
        h.hotel_id,
        h.hotel_name,
        m.month_start
    FROM dim_hotels h
    CROSS JOIN months m
),

initial_headcount AS (
    SELECT
        de.hotel_id,
        SUM(
            CASE
                WHEN e.event_type = 'HIRE' THEN 1
                WHEN e.event_type = 'TERMINATION' THEN -1
                ELSE 0
            END
        ) AS initial_headcount
    FROM fact_employee_events e
    JOIN dim_employees de
        ON e.employee_id = de.employee_id
    WHERE e.event_date_id < 20210101
    GROUP BY de.hotel_id
),

monthly_events AS (
    SELECT
        de.hotel_id,

        STR_TO_DATE(
            CONCAT(
                LEFT(CAST(e.event_date_id AS CHAR), 4),
                '-',
                SUBSTRING(CAST(e.event_date_id AS CHAR), 5, 2),
                '-01'
            ),
            '%Y-%m-%d'
        ) AS month_start,

        SUM(
            CASE WHEN e.event_type = 'HIRE'
            THEN 1 ELSE 0 END
        ) AS hires,

        SUM(
            CASE WHEN e.event_type = 'TERMINATION'
            THEN 1 ELSE 0 END
        ) AS terminations

    FROM fact_employee_events e
    JOIN dim_employees de
        ON e.employee_id = de.employee_id

    WHERE e.event_date_id BETWEEN 20210101 AND 20251231

    GROUP BY
        de.hotel_id,
        month_start
),

monthly_series AS (
    SELECT
        hm.hotel_id,
        hm.hotel_name,
        hm.month_start,

        COALESCE(ih.initial_headcount, 0)
            AS initial_headcount,

        COALESCE(me.hires, 0) AS hires,
        COALESCE(me.terminations, 0) AS terminations

    FROM hotel_months hm

    LEFT JOIN initial_headcount ih
        ON hm.hotel_id = ih.hotel_id

    LEFT JOIN monthly_events me
        ON hm.hotel_id = me.hotel_id
        AND hm.month_start = me.month_start
),

calculated AS (
    SELECT
        *,

        initial_headcount
        +
        COALESCE(
            SUM(hires - terminations) OVER (
                PARTITION BY hotel_id
                ORDER BY month_start
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND 1 PRECEDING
            ),
            0
        ) AS starting_headcount

    FROM monthly_series
)

SELECT
    hotel_id,
    hotel_name,
    month_start,

    starting_headcount,

    hires,
    terminations,

    starting_headcount + hires - terminations
        AS ending_headcount,

    (
        starting_headcount
        + starting_headcount
        + hires - terminations
    ) / 2.0 AS average_headcount,

    CASE
        WHEN (
            starting_headcount
            + starting_headcount
            + hires - terminations
        ) <= 0 THEN 0

        ELSE ROUND(
            terminations /
            (
                (
                    starting_headcount
                    + starting_headcount
                    + hires - terminations
                ) / 2.0
            ) * 100,
            2
        )
    END AS turnover_rate

FROM calculated;
