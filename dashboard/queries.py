
import pandas as pd
import streamlit as st
from sqlalchemy import text

from dashboard.db_connection import get_engine


# -----------------------------------------
# FILTER OPTIONS
# -----------------------------------------

@st.cache_data(ttl=60)
def get_institutions():
    query = """
        SELECT institution_name
        FROM financial_institutions
        ORDER BY institution_name
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=60)
def get_locations():
    query = """
        SELECT DISTINCT location
        FROM financial_institutions
        WHERE location IS NOT NULL
        ORDER BY location
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=60)
def get_product_categories():
    query = """
        SELECT DISTINCT product_type
        FROM financial_products
        ORDER BY product_type
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=60)
def get_products(category):
    query = text("""
        SELECT DISTINCT product_name
        FROM financial_products
        WHERE (:category = 'All Categories'
               OR product_type = :category)
        ORDER BY product_name
    """)

    return pd.read_sql(
        query,
        get_engine(),
        params={"category": category}
    )


# -----------------------------------------
# DASHBOARD DATA
# -----------------------------------------

@st.cache_data(ttl=60)
def get_dashboard_data(
    institution,
    location,
    product_category,
    product_name,
    start_date,
    end_date
):

    query = text("""
        WITH months AS (
            SELECT
                (
                    month_start
                    + INTERVAL '1 month'
                    - INTERVAL '1 day'
                )::DATE AS report_month
            FROM GENERATE_SERIES(
                DATE_TRUNC('month', CAST(:start_date AS DATE)),
                DATE_TRUNC('month', CAST(:end_date AS DATE)),
                INTERVAL '1 month'
            ) AS month_start
        ),

        eligible_institutions AS (
            SELECT institution_id
            FROM financial_institutions
            WHERE
                (:institution = 'All Institutions'
                 OR institution_name = :institution)
                AND
                (:location = 'All Locations'
                 OR location = :location)
        ),

        -- ROI and AUM: investment products only
        investment_metrics AS (
            SELECT
                (
                    DATE_TRUNC('month', s.snapshot_date)
                    + INTERVAL '1 month'
                    - INTERVAL '1 day'
                )::DATE AS report_month,

                ROUND(
                    (
                        SUM(s.market_value)
                        - SUM(s.invested_capital)
                    )
                    / NULLIF(SUM(s.invested_capital), 0) * 100,
                    2
                ) AS roi_percentage,

                ROUND(SUM(s.market_value), 2) AS total_aum

            FROM investment_account_monthly_snapshots s

            JOIN investment_accounts ia
                ON s.account_id = ia.account_id

            JOIN financial_products fp
                ON ia.product_id = fp.product_id

            JOIN eligible_institutions ei
                ON fp.institution_id = ei.institution_id

            WHERE
                ia.opened_date <= s.snapshot_date
                AND (
                    ia.closed_date IS NULL
                    OR ia.closed_date >= s.snapshot_date
                )
                AND (
                    :product_category = 'All Categories'
                    OR fp.product_type = :product_category
                )
                AND (
                    :product_name = 'All Products'
                    OR fp.product_name = :product_name
                )
                AND :product_category <> 'Loan'

            GROUP BY 1
        ),

        -- CAC: institution/location level
        monthly_expenses AS (
            SELECT
                (
                    DATE_TRUNC('month', expense_date)
                    + INTERVAL '1 month'
                    - INTERVAL '1 day'
                )::DATE AS report_month,
                SUM(amount) AS total_expenses

            FROM marketing_expenses

            WHERE institution_id IN (
                SELECT institution_id
                FROM eligible_institutions
            )

            GROUP BY 1
        ),

        monthly_acquisitions AS (
            SELECT
                (
                    DATE_TRUNC('month', acquisition_date)
                    + INTERVAL '1 month'
                    - INTERVAL '1 day'
                )::DATE AS report_month,
                COUNT(DISTINCT customer_id) AS new_customers

            FROM customer_acquisition

            WHERE institution_id IN (
                SELECT institution_id
                FROM eligible_institutions
            )

            GROUP BY 1
        ),

        cac_metrics AS (
            SELECT
                m.report_month,

                ROUND(
                    e.total_expenses
                    / NULLIF(a.new_customers, 0),
                    2
                ) AS cac

            FROM months m

            LEFT JOIN monthly_expenses e
                ON m.report_month = e.report_month

            LEFT JOIN monthly_acquisitions a
                ON m.report_month = a.report_month
        ),

        -- NPS: institution/location level
        nps_metrics AS (
            SELECT
                (
                    DATE_TRUNC('month', s.survey_date)
                    + INTERVAL '1 month'
                    - INTERVAL '1 day'
                )::DATE AS report_month,

                ROUND(
                    100.0 * (
                        COUNT(*) FILTER (
                            WHERE s.nps_rating >= 9
                        )
                        -
                        COUNT(*) FILTER (
                            WHERE s.nps_rating <= 6
                        )
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS nps_score

            FROM customer_surveys s

            JOIN customer_acquisition ca
                ON s.customer_id = ca.customer_id

            JOIN eligible_institutions ei
                ON ca.institution_id = ei.institution_id

            GROUP BY 1
        ),

        -- Loan default rate: loan products only
        loan_position AS (
            SELECT
                m.report_month,
                la.loan_id,
                latest.loan_status

            FROM months m

            JOIN loan_accounts la
                ON la.disbursement_date <= m.report_month

            JOIN financial_products fp
                ON la.product_id = fp.product_id

            JOIN eligible_institutions ei
                ON fp.institution_id = ei.institution_id

            LEFT JOIN LATERAL (
                SELECT loan_status
                FROM loan_status_history h
                WHERE h.loan_id = la.loan_id
                  AND h.status_date <= m.report_month
                ORDER BY h.status_date DESC
                LIMIT 1
            ) latest ON TRUE

            WHERE
                (
                    :product_category = 'All Categories'
                    OR fp.product_type = :product_category
                )
                AND (
                    :product_name = 'All Products'
                    OR fp.product_name = :product_name
                )
                AND :product_category <> 'Investment'
        ),

        loan_metrics AS (
            SELECT
                report_month,

                ROUND(
                    COUNT(*) FILTER (
                        WHERE loan_status = 'Defaulted'
                    ) * 100.0
                    / NULLIF(COUNT(loan_id), 0),
                    2
                ) AS default_rate

            FROM loan_position
            GROUP BY report_month
        )

        SELECT
            m.report_month,

            CASE
                WHEN :product_category = 'Loan'
                THEN NULL
                ELSE COALESCE(i.roi_percentage, 0)
            END AS roi_percentage,

            CASE
                WHEN :product_category = 'Loan'
                THEN NULL
                ELSE COALESCE(i.total_aum, 0)
            END AS total_aum,

            c.cac,
            n.nps_score,

            CASE
                WHEN :product_category = 'Investment'
                THEN NULL
                ELSE l.default_rate
            END AS default_rate

        FROM months m

        LEFT JOIN investment_metrics i
            ON m.report_month = i.report_month

        LEFT JOIN cac_metrics c
            ON m.report_month = c.report_month

        LEFT JOIN nps_metrics n
            ON m.report_month = n.report_month

        LEFT JOIN loan_metrics l
            ON m.report_month = l.report_month

        ORDER BY m.report_month
    """)

    params = {
        "institution": institution,
        "location": location,
        "product_category": product_category,
        "product_name": product_name,
        "start_date": start_date,
        "end_date": end_date
    }

    return pd.read_sql(
        query,
        get_engine(),
        params=params
    )
