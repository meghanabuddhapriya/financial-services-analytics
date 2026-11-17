
import random
import uuid
from datetime import date, timedelta

import numpy as np
import pandas as pd
import psycopg
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)
Faker.seed(42)

START = date(2022, 1, 1)
END = date(2026, 12, 31)

DB_CONFIG = {
    "host": "localhost",
    "dbname": "financial_services_analytics",
    "user": "fs_analyst",
    "password": "fs_analyst",
    "port": 5432
}


def new_id():
    return str(uuid.uuid4())


def random_date(start, end):
    if start >= end:
        return start
    return start + timedelta(days=random.randint(0, (end - start).days))


def month_end(year, month):
    return (pd.Timestamp(year=year, month=month, day=1)
            + pd.offsets.MonthEnd(0)).date()


def seasonal_factor(month):
    if month in (3, 4):
        return 1.35
    if month in (11, 12):
        return 1.20
    return 1.0


def monthly_return(year, month):
    # Fictional market scenarios, not actual historical returns.
    annual_trend = {
        2022: 0.009,
        2023: -0.002,
        2024: 0.007,
        2025: 0.005,
        2026: 0.004
    }
    rate = annual_trend[year] / 12
    if month in (11, 12):
        rate += 0.002
    return float(np.random.normal(rate, 0.025))


def make_df(rows, columns):
    return pd.DataFrame(rows, columns=columns)


print("Starting synthetic data generation...")


# --------------------------------------------------
# 1. FINANCIAL INSTITUTIONS
# --------------------------------------------------

institution_rows = []
institution_names = [
    "Apex Financial",
    "Horizon Bank",
    "Crescent Capital",
    "Pioneer Finance"
]

institutions = []

for name in institution_names:
    iid = new_id()
    institutions.append(iid)
    institution_rows.append((
        iid, name, fake.city(), random_date(date(1980, 1, 1), date(2015, 1, 1))
    ))

df_institutions = make_df(
    institution_rows,
    ["institution_id", "institution_name", "location", "established_date"]
)


# --------------------------------------------------
# 2. FINANCIAL PRODUCTS
# --------------------------------------------------

product_rows = []
investment_products = {}
loan_products = {}

for iid in institutions:
    investment_products[iid] = []
    loan_products[iid] = []

    for name, risk in [
        ("Growth Fund", "High"),
        ("Balanced Fund", "Medium"),
        ("Income Fund", "Low")
    ]:
        pid = new_id()
        investment_products[iid].append(pid)
        product_rows.append((pid, iid, name, "Investment", risk))

    for name, risk in [
        ("Personal Loan", "Medium"),
        ("Home Loan", "Low")
    ]:
        pid = new_id()
        loan_products[iid].append(pid)
        product_rows.append((pid, iid, name, "Loan", risk))

df_products = make_df(
    product_rows,
    ["product_id", "institution_id", "product_name",
     "product_type", "risk_category"]
)


# --------------------------------------------------
# 3. CUSTOMERS AND ACQUISITION
# --------------------------------------------------

customer_rows = []
acquisition_rows = []
customer_ids = []

channels = ["Digital", "Branch", "Referral"]

for _ in range(10000):
    cid = new_id()
    iid = random.choice(institutions)
    joining_date = random_date(START, END)
    channel = random.choice(channels)

    customer_ids.append(cid)

    customer_rows.append((
        cid,
        fake.name(),
        fake.city(),
        random.choice(["Male", "Female", "Other"]),
        fake.date_of_birth(minimum_age=21, maximum_age=75),
        joining_date
    ))

    acquisition_rows.append((
        new_id(), cid, iid, joining_date, channel,
        random.choice(["Tax Saver", "Digital Growth", "Wealth Campaign"])
    ))

df_customers = make_df(
    customer_rows,
    ["customer_id", "customer_name", "location", "gender",
     "date_of_birth", "joining_date"]
)

df_acquisition = make_df(
    acquisition_rows,
    ["acquisition_id", "customer_id", "institution_id",
     "acquisition_date", "acquisition_channel", "campaign_name"]
)


# --------------------------------------------------
# 4. INVESTMENT ACCOUNTS AND TRANSACTIONS
# --------------------------------------------------

account_rows = []
transaction_rows = []
snapshot_rows = []

investment_customer_ids = random.sample(customer_ids, 6500)

for cid in investment_customer_ids:
    iid = random.choice(institutions)
    pid = random.choice(investment_products[iid])

    aid = new_id()
    opened = random_date(START, END)

    closed = None
    status = "Active"

    if random.random() < 0.15 and opened < END:
        closed = random_date(opened, END)
        status = "Closed"

    account_rows.append((
        aid, cid, pid, opened, status, closed
    ))

    capital = random.uniform(50000, 1000000)
    transaction_rows.append((
        new_id(), aid, opened, "Contribution", round(capital, 2)
    ))

    current_value = capital

    for period in pd.period_range(
        start=opened.strftime("%Y-%m"),
        end=END.strftime("%Y-%m"),
        freq="M"
    ):
        snapshot_date = month_end(period.year, period.month)

        if snapshot_date < opened:
            continue

        if closed is not None and snapshot_date > closed:
            continue

        # Occasional additional contributions or withdrawals.
        if random.random() < 0.12:
            amount = round(random.uniform(5000, 50000), 2)

            if random.random() < 0.75:
                capital += amount
                current_value += amount
                transaction_type = "Contribution"
            else:
                amount = min(amount, capital * 0.20)
                capital -= amount
                current_value = max(0, current_value - amount)
                transaction_type = "Withdrawal"

            transaction_rows.append((
                new_id(), aid, snapshot_date,
                transaction_type, amount
            ))
            
        current_value *= (1 + monthly_return(
            period.year, period.month
        ))

        current_value = max(0, current_value)

        snapshot_rows.append((
            new_id(), aid, snapshot_date,
            round(capital, 2), round(current_value, 2)
        ))

df_accounts = make_df(
    account_rows,
    ["account_id", "customer_id", "product_id",
     "opened_date", "account_status", "closed_date"]
)

df_transactions = make_df(
    transaction_rows,
    ["transaction_id", "account_id", "transaction_date",
     "transaction_type", "amount"]
)

df_snapshots = make_df(
    snapshot_rows,
    ["snapshot_id", "account_id", "snapshot_date",
     "invested_capital", "market_value"]
)


# --------------------------------------------------
# 5. LOANS, REPAYMENTS AND LOAN STATUS
# --------------------------------------------------

loan_rows = []
repayment_rows = []
status_rows = []

loan_customer_ids = random.sample(customer_ids, 3500)

for cid in loan_customer_ids:
    iid = random.choice(institutions)
    pid = random.choice(loan_products[iid])

    lid = new_id()
    disbursement = random_date(START, END)
    amount = round(random.uniform(100000, 3000000), 2)
    tenure = random.choice([12, 24, 36, 48, 60])

    loan_rows.append((
        lid, cid, pid, amount, disbursement, tenure
    ))

    status_rows.append((
        new_id(), lid, disbursement, "Active"
    ))

    event_date = None
    final_status = None

    if (
        random.random() < 0.12
        and disbursement + timedelta(days=30) <= END
    ):
        event_date = random_date(
            disbursement + timedelta(days=30), END
        )
        final_status = "Defaulted"
    else:
        maturity = disbursement + timedelta(days=tenure * 30)
        if maturity <= END:
            event_date = maturity
            final_status = "Closed"

    if event_date:
        status_rows.append((
            new_id(), lid, event_date, final_status
        ))

    repayment_end = min(
        event_date if event_date else END, END
    )

    repayment_date = disbursement + timedelta(days=30)
    monthly_payment = amount / tenure

    while repayment_date <= repayment_end:
        repayment_status = random.choices(
            ["Paid", "Partial", "Missed"],
            weights=[0.82, 0.12, 0.06]
        )[0]

        paid = monthly_payment
        if repayment_status == "Partial":
            paid *= 0.5
        elif repayment_status == "Missed":
            paid = 0

        repayment_rows.append((
            new_id(), lid, repayment_date,
            round(paid, 2), repayment_status
        ))

        repayment_date += timedelta(days=30)

df_loans = make_df(
    loan_rows,
    ["loan_id", "customer_id", "product_id",
     "loan_amount", "disbursement_date", "tenure_months"]
)

df_repayments = make_df(
    repayment_rows,
    ["repayment_id", "loan_id", "repayment_date",
     "amount_paid", "repayment_status"]
)

df_loan_status = make_df(
    status_rows,
    ["status_history_id", "loan_id", "status_date", "loan_status"]
)


# --------------------------------------------------
# 6. MARKETING EXPENSES
# --------------------------------------------------

expense_rows = []

for iid in institutions:
    for period in pd.period_range("2022-01", "2026-12", freq="M"):
        for channel in channels:
            expense_date = month_end(period.year, period.month)
            base_expense = random.uniform(30000, 100000)
            amount = base_expense * seasonal_factor(period.month)

            expense_rows.append((
                new_id(), iid, expense_date, "Marketing",
                channel, random.choice([
                    "Tax Saver", "Digital Growth", "Wealth Campaign"
                ]), round(amount, 2)
            ))

            expense_rows.append((
                new_id(), iid, expense_date, "Sales",
                channel, random.choice([
                    "Tax Saver", "Digital Growth", "Wealth Campaign"
                ]), round(amount * 0.45, 2)
            ))

df_expenses = make_df(
    expense_rows,
    ["expense_id", "institution_id", "expense_date",
     "expense_type", "acquisition_channel",
     "campaign_name", "amount"]
)


# --------------------------------------------------
# 7. CUSTOMER SURVEYS / NPS
# --------------------------------------------------

survey_rows = []

for cid in customer_ids:
    survey_date = random_date(START, END)

    # Simulated ratings with a small seasonal effect.
    rating = random.choices(
        list(range(11)),
        weights=[2, 2, 3, 4, 5, 7, 9, 13, 20, 20, 15]
    )[0]

    if survey_date.year == 2026 and rating > 0:
        rating = max(0, rating - 1)

    survey_rows.append((
        new_id(), cid, survey_date, rating
    ))

df_surveys = make_df(
    survey_rows,
    ["survey_id", "customer_id", "survey_date", "nps_rating"]
)


# --------------------------------------------------
# 8. LOAD DATA INTO POSTGRESQL
# --------------------------------------------------

tables = [
    ("financial_institutions", df_institutions),
    ("financial_products", df_products),
    ("customers", df_customers),
    ("investment_accounts", df_accounts),
    ("investment_transactions", df_transactions),
    ("investment_account_monthly_snapshots", df_snapshots),
    ("loan_accounts", df_loans),
    ("loan_repayments", df_repayments),
    ("loan_status_history", df_loan_status),
    ("customer_acquisition", df_acquisition),
    ("marketing_expenses", df_expenses),
    ("customer_surveys", df_surveys)
]

print("\nGenerated row counts:")
for name, df in tables:
    print(f"{name}: {len(df):,}")

print("\nConnecting to PostgreSQL...")

with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:

        # Clear old generated data when rerunning this script.
        cur.execute("""
            TRUNCATE TABLE
                customer_surveys,
                marketing_expenses,
                customer_acquisition,
                loan_status_history,
                loan_repayments,
                loan_accounts,
                investment_account_monthly_snapshots,
                investment_transactions,
                investment_accounts,
                financial_products,
                customers,
                financial_institutions
            CASCADE
        """)

        for table_name, df in tables:
            if df.empty:
                continue

            columns = list(df.columns)
            placeholders = ", ".join(["%s"] * len(columns))

            query = (
                f"INSERT INTO {table_name} "
                f"({', '.join(columns)}) "
                f"VALUES ({placeholders})"
            )

            cur.executemany(
                query,
                df.itertuples(index=False, name=None)
            )

            print(f"Loaded {len(df):,} rows into {table_name}")

print("\nSUCCESS: All synthetic data loaded into PostgreSQL!")
