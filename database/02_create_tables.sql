
-- 1. Financial institutions
CREATE TABLE financial_institutions (
    institution_id UUID PRIMARY KEY,
    institution_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    established_date DATE
);

-- 2. Financial products
CREATE TABLE financial_products (
    product_id UUID PRIMARY KEY,
    institution_id UUID NOT NULL REFERENCES financial_institutions(institution_id),
    product_name VARCHAR(100) NOT NULL,
    product_type VARCHAR(20) NOT NULL CHECK (product_type IN ('Investment', 'Loan')),
    risk_category VARCHAR(30)
);

-- 3. Customers
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    gender VARCHAR(20),
    date_of_birth DATE,
    joining_date DATE NOT NULL
);

-- 4. Investment accounts
CREATE TABLE investment_accounts (
    account_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    product_id UUID NOT NULL REFERENCES financial_products(product_id),
    opened_date DATE NOT NULL,
    account_status VARCHAR(20) NOT NULL,
    closed_date DATE,
    CHECK (closed_date IS NULL OR closed_date >= opened_date)
);

-- 5. Investment transactions
CREATE TABLE investment_transactions (
    transaction_id UUID PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES investment_accounts(account_id),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL
        CHECK (transaction_type IN ('Contribution', 'Withdrawal', 'Return', 'Fee')),
    amount NUMERIC(18,2) NOT NULL CHECK (amount >= 0)
);

-- 6. Monthly investment snapshots
CREATE TABLE investment_account_monthly_snapshots (
    snapshot_id UUID PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES investment_accounts(account_id),
    snapshot_date DATE NOT NULL,
    invested_capital NUMERIC(18,2) NOT NULL CHECK (invested_capital >= 0),
    market_value NUMERIC(18,2) NOT NULL CHECK (market_value >= 0),
    UNIQUE (account_id, snapshot_date)
);

-- 7. Loan accounts
CREATE TABLE loan_accounts (
    loan_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    product_id UUID NOT NULL REFERENCES financial_products(product_id),
    loan_amount NUMERIC(18,2) NOT NULL CHECK (loan_amount > 0),
    disbursement_date DATE NOT NULL,
    tenure_months INTEGER NOT NULL CHECK (tenure_months > 0)
);

-- 8. Loan repayments
CREATE TABLE loan_repayments (
    repayment_id UUID PRIMARY KEY,
    loan_id UUID NOT NULL REFERENCES loan_accounts(loan_id),
    repayment_date DATE NOT NULL,
    amount_paid NUMERIC(18,2) NOT NULL CHECK (amount_paid >= 0),
    repayment_status VARCHAR(20) NOT NULL
        CHECK (repayment_status IN ('Paid', 'Partial', 'Missed'))
);

-- 9. Loan status history
CREATE TABLE loan_status_history (
    status_history_id UUID PRIMARY KEY,
    loan_id UUID NOT NULL REFERENCES loan_accounts(loan_id),
    status_date DATE NOT NULL,
    loan_status VARCHAR(20) NOT NULL
        CHECK (loan_status IN ('Active', 'Closed', 'Defaulted')),
    UNIQUE (loan_id, status_date)
);

-- 10. Customer acquisition
CREATE TABLE customer_acquisition (
    acquisition_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    institution_id UUID NOT NULL REFERENCES financial_institutions(institution_id),
    acquisition_date DATE NOT NULL,
    acquisition_channel VARCHAR(50),
    campaign_name VARCHAR(100),
    UNIQUE (customer_id, institution_id)
);

-- 11. Marketing and sales expenses
CREATE TABLE marketing_expenses (
    expense_id UUID PRIMARY KEY,
    institution_id UUID NOT NULL REFERENCES financial_institutions(institution_id),
    expense_date DATE NOT NULL,
    expense_type VARCHAR(20) NOT NULL
        CHECK (expense_type IN ('Marketing', 'Sales')),
    acquisition_channel VARCHAR(50),
    campaign_name VARCHAR(100),
    amount NUMERIC(18,2) NOT NULL CHECK (amount >= 0)
);

-- 12. Customer surveys
CREATE TABLE customer_surveys (
    survey_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    survey_date DATE NOT NULL,
    nps_rating INTEGER NOT NULL CHECK (nps_rating BETWEEN 0 AND 10)
);
