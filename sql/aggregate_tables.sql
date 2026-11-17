
-- ==========================================
-- 1. MONTHLY ROI
-- ==========================================

DROP TABLE IF EXISTS monthly_roi;

CREATE TABLE monthly_roi AS
SELECT
    snapshot_date AS report_month,
    ROUND(
        (
            SUM(market_value) - SUM(invested_capital)
        ) / NULLIF(SUM(invested_capital), 0) * 100,
        2
    ) AS roi_percentage
FROM investment_account_monthly_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date;


-- ==========================================
-- 2. MONTHLY AUM
-- ==========================================

DROP TABLE IF EXISTS monthly_aum;

CREATE TABLE monthly_aum AS
SELECT
    s.snapshot_date AS report_month,
    ROUND(SUM(s.market_value), 2) AS total_aum
FROM investment_account_monthly_snapshots s
JOIN investment_accounts a
    ON s.account_id = a.account_id
WHERE
    a.opened_date <= s.snapshot_date
    AND (
        a.closed_date IS NULL
        OR a.closed_date >= s.snapshot_date
    )
GROUP BY s.snapshot_date
ORDER BY s.snapshot_date;


-- ==========================================
-- 3. MONTHLY CAC
-- ==========================================

DROP TABLE IF EXISTS monthly_cac;

CREATE TABLE monthly_cac AS
WITH monthly_expenses AS (
    SELECT
        institution_id,
        (
            DATE_TRUNC('month', expense_date)
            + INTERVAL '1 month'
            - INTERVAL '1 day'
        )::DATE AS report_month,
        SUM(amount) AS total_expenses
    FROM marketing_expenses
    GROUP BY institution_id, DATE_TRUNC('month', expense_date)
),
monthly_customers AS (
    SELECT
        institution_id,
        (
            DATE_TRUNC('month', acquisition_date)
            + INTERVAL '1 month'
            - INTERVAL '1 day'
        )::DATE AS report_month,
        COUNT(*) AS new_customers
    FROM customer_acquisition
    GROUP BY institution_id, DATE_TRUNC('month', acquisition_date)
)
SELECT
    e.report_month,
    ROUND(
        SUM(e.total_expenses) / NULLIF(SUM(c.new_customers), 0),
        2
    ) AS cac
FROM monthly_expenses e
JOIN monthly_customers c
    ON e.institution_id = c.institution_id
    AND e.report_month = c.report_month
GROUP BY e.report_month
ORDER BY e.report_month;


-- ==========================================
-- 4. MONTHLY NPS
-- ==========================================

DROP TABLE IF EXISTS monthly_nps;

CREATE TABLE monthly_nps AS
SELECT
    (DATE_TRUNC('month', survey_date) + INTERVAL '1 month' - INTERVAL '1 day')::DATE AS report_month,

    ROUND(
        (
            COUNT(*) FILTER (WHERE nps_rating >= 9) * 100.0
            / NULLIF(COUNT(*), 0)
        )
        -
        (
            COUNT(*) FILTER (WHERE nps_rating <= 6) * 100.0
            / NULLIF(COUNT(*), 0)
        ),
        2
    ) AS nps_score

FROM customer_surveys
GROUP BY DATE_TRUNC('month', survey_date)
ORDER BY report_month;


-- ==========================================
-- 5. MONTHLY LOAN DEFAULT RATE
-- ==========================================

DROP TABLE IF EXISTS monthly_loan_default_rate;

CREATE TABLE monthly_loan_default_rate AS
WITH months AS (
    SELECT
        (
            DATE_TRUNC('month', generated_date)
            + INTERVAL '1 month - 1 day'
        )::DATE AS report_month
    FROM GENERATE_SERIES(
        DATE '2022-01-01',
        DATE '2026-12-01',
        INTERVAL '1 month'
    ) AS generated_date
),
loan_position AS (
    SELECT
        m.report_month,
        l.loan_id,
        (
            SELECT h.loan_status
            FROM loan_status_history h
            WHERE h.loan_id = l.loan_id
              AND h.status_date <= m.report_month
            ORDER BY h.status_date DESC
            LIMIT 1
        ) AS status_at_month_end
    FROM months m
    JOIN loan_accounts l
        ON l.disbursement_date <= m.report_month
)
SELECT
    report_month,
    COUNT(*) AS total_loans,
    COUNT(*) FILTER (
        WHERE status_at_month_end = 'Defaulted'
    ) AS defaulted_loans,
    ROUND(
        COUNT(*) FILTER (
            WHERE status_at_month_end = 'Defaulted'
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS default_rate
FROM loan_position
GROUP BY report_month
ORDER BY report_month;
