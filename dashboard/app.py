
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.queries import (
    get_institutions,
    get_locations,
    get_product_categories,
    get_products,
    get_dashboard_data
)


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Financial Performance & Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =====================================================
# COLOR PALETTE
# =====================================================

COLORS = {
    "sky": "#8ecae6",
    "blue_green": "#219ebc",
    "deep_space": "#023047",
    "amber": "#ffb703",
    "orange": "#fb8500"
}

CHART_COLORS = [
    COLORS["blue_green"],
    COLORS["orange"],
    COLORS["sky"],
    COLORS["amber"],
    COLORS["deep_space"]
]

# Use Streamlit's active theme
theme_base = st.get_option("theme.base") or "light"
is_dark = theme_base.lower() == "dark"

TEXT_COLOR = "#8ecae6" if is_dark else COLORS["deep_space"]
MUTED_COLOR = "#8ecae6" if is_dark else "#219ebc"

CHART_TEMPLATE = "plotly_dark" if is_dark else "plotly_white"


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.stApp {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Main page spacing */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

/* Header */

.dashboard-header {
    background: linear-gradient(
        115deg,
        #023047 0%,
        #023047 65%,
        #219ebc 100%
    );
    padding: 30px 32px;
    border-radius: 16px;
    margin-bottom: 22px;
    overflow: hidden;
    box-sizing: border-box;
}

.dashboard-eyebrow,
.dashboard-title,
.dashboard-subtitle,
.header-meta {
    display: block;
    overflow-wrap: anywhere;
}

.dashboard-title {
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.3;
    margin: 0;
}

.dashboard-subtitle {
    color: #8ecae6;
    font-size: 14px;
    margin-top: 9px;
}

.dashboard-eyebrow {
    color: #8ecae6;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.dashboard-title {
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.25;
    margin: 0;
}

.dashboard-subtitle {
    color: #8ecae6;
    font-size: 14px;
    margin-top: 9px;
}

.header-meta {
    color: #ffffff;
    font-size: 12px;
    font-weight: 600;
    margin-top: 18px;
}

/* Section headings */

.section-heading {
    font-size: 19px;
    font-weight: 750;
    margin-top: 20px;
    margin-bottom: 3px;
    color: var(--text-color);
}

.section-description {
    font-size: 12px;
    color: var(--text-color);
    opacity: 0.65;
    margin-bottom: 15px;
}

/* Filter section */

.filter-heading {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 8px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}

/* KPI accent strips */

.kpi-accent {
    height: 4px;
    border-radius: 5px;
    margin-bottom: 12px;
}

.kpi-caption {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    opacity: 0.72;
}

.kpi-note {
    font-size: 11px;
    opacity: 0.65;
    margin-top: -5px;
}

/* Buttons */

.stButton button,
.stDownloadButton button {
    border-radius: 8px;
    font-weight: 600;
}

/* Chart containers */

div[data-testid="stPlotlyChart"] {
    width: 100%;
}

/* Data table */

div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Footer */

.dashboard-footer {
    text-align: center;
    font-size: 11px;
    opacity: 0.65;
    padding: 18px 0 5px 0;
}

/* Responsive headings */

@media (max-width: 768px) {
    .dashboard-title {
        font-size: 24px;
    }

    .dashboard-header {
        padding: 22px;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# HEADER
# =====================================================

with st.container():
    st.markdown("""
        <div class="dashboard-header">
            <div class="dashboard-eyebrow">
                FINANCIAL SERVICES ANALYTICS PLATFORM
            </div>

        </div>
    """, unsafe_allow_html=True)


# =====================================================
# FILTER DATA
# =====================================================

institutions = get_institutions()
locations = get_locations()
categories = get_product_categories()

institution_options = (
    ["All Institutions"]
    + institutions["institution_name"].tolist()
)

location_options = (
    ["All Locations"]
    + locations["location"].tolist()
)

category_options = (
    ["All Categories"]
    + categories["product_type"].tolist()
)


# =====================================================
# TOP FILTER PANEL
# =====================================================

st.markdown(
    '<div class="section-heading">Analysis Controls</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Select the reporting scope and period to explore financial performance.'
    '</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    filter1, filter2, filter3, filter4 = st.columns(4)

    with filter1:
        selected_institution = st.selectbox(
            "Financial Institution",
            institution_options,
            key="institution_filter"
        )

    with filter2:
        selected_location = st.selectbox(
            "Location",
            location_options,
            key="location_filter"
        )

    with filter3:
        selected_category = st.selectbox(
            "Product Category",
            category_options,
            key="category_filter"
        )

    with filter4:
        products = get_products(selected_category)

        product_options = (
            ["All Products"]
            + products["product_name"].tolist()
        )

        selected_product = st.selectbox(
            "Product",
            product_options,
            key="product_filter"
        )

    st.divider()

    date1, date2, refresh_col = st.columns([1, 1, 1])

    with date1:
        start_date = st.date_input(
            "Start Date",
            value=pd.to_datetime("2022-01-01").date(),
            min_value=pd.to_datetime("2022-01-01").date(),
            max_value=pd.to_datetime("2026-12-31").date(),
            key="start_date_filter"
        )

    with date2:
        end_date = st.date_input(
            "End Date",
            value=pd.to_datetime("2026-12-31").date(),
            min_value=pd.to_datetime("2022-01-01").date(),
            max_value=pd.to_datetime("2026-12-31").date(),
            key="end_date_filter"
        )

    with refresh_col:
        st.write("")
        st.write("")

        if st.button(
            "↻ Refresh Dashboard",
            use_container_width=True
        ):
            get_dashboard_data.clear()
            get_institutions.clear()
            get_locations.clear()
            get_product_categories.clear()
            get_products.clear()
            st.rerun()


if start_date > end_date:
    st.error("Start date cannot be after end date.")
    st.stop()


# =====================================================
# FETCH DASHBOARD DATA
# =====================================================

with st.spinner("Loading financial performance data..."):

    df = get_dashboard_data(
        selected_institution,
        selected_location,
        selected_category,
        selected_product,
        start_date,
        end_date
    )


if df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()


df = df.sort_values("report_month").copy()

latest = df.iloc[-1]

latest_month = pd.to_datetime(
    latest["report_month"]
).strftime("%B %Y")


# =====================================================
# REPORTING CONTEXT
# =====================================================

st.markdown(
    '<div class="section-heading">Performance Snapshot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Latest available KPI performance for the selected reporting scope.'
    '</div>',
    unsafe_allow_html=True
)

context1, context2 = st.columns([3, 1])

with context1:
    st.markdown(
        f"**{selected_institution}**  ·  "
        f"{selected_location}  ·  "
        f"{selected_category}  ·  "
        f"{selected_product}"
    )

with context2:
    st.markdown(
        f"<div style='text-align:right;'>"
        f"<span style='opacity:0.65;font-size:12px;'>"
        f"Latest reporting month</span><br>"
        f"<b style='color:{COLORS['blue_green']};'>"
        f"{latest_month}</b>"
        f"</div>",
        unsafe_allow_html=True
    )


# =====================================================
# KPI HELPER
# =====================================================

def get_delta(current, previous, suffix="", divisor=1):

    if pd.isna(current) or pd.isna(previous):
        return None

    difference = (current - previous) / divisor

    return f"{difference:+,.2f}{suffix} vs previous month"


def show_kpi(column, label, value, description, accent,
             delta=None, delta_color="normal"):

    with column:

        with st.container(border=True):

            st.markdown(
                f'<div class="kpi-accent" '
                f'style="background:{accent};"></div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="kpi-caption">{label}</div>',
                unsafe_allow_html=True
            )

            st.metric(
                label=" ",
                value=value,
                delta=delta,
                delta_color=delta_color,
                label_visibility="collapsed"
            )

            st.markdown(
                f'<div class="kpi-note">{description}</div>',
                unsafe_allow_html=True
            )


# =====================================================
# PREVIOUS MONTH DATA
# =====================================================

previous = df.iloc[-2] if len(df) > 1 else None


def previous_delta(column, suffix="", divisor=1):

    if previous is None:
        return None

    return get_delta(
        latest[column],
        previous[column],
        suffix,
        divisor
    )


# =====================================================
# KPI VALUES
# =====================================================

roi_value = (
    f"{latest['roi_percentage']:.2f}%"
    if pd.notna(latest["roi_percentage"])
    else "N/A"
)

aum_value = (
    f"₹{latest['total_aum'] / 10000000:.2f} Cr"
    if pd.notna(latest["total_aum"])
    else "N/A"
)

cac_value = (
    f"₹{latest['cac']:,.2f}"
    if pd.notna(latest["cac"])
    else "N/A"
)

nps_value = (
    f"{latest['nps_score']:.2f}"
    if pd.notna(latest["nps_score"])
    else "N/A"
)

default_value = (
    f"{latest['default_rate']:.2f}%"
    if pd.notna(latest["default_rate"])
    else "N/A"
)


# =====================================================
# KPI DISPLAY
# =====================================================

st.markdown(
    '<div class="section-heading">Key Performance Indicators</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Track profitability, asset growth, acquisition efficiency, '
    'customer loyalty and credit risk.'
    '</div>',
    unsafe_allow_html=True
)

kpi_columns = st.columns(5)

show_kpi(
    kpi_columns[0],
    "Return on Investment",
    roi_value,
    "Investment profitability",
    COLORS["blue_green"],
    previous_delta("roi_percentage", " pp"),
    "normal"
)

show_kpi(
    kpi_columns[1],
    "Assets Under Management",
    aum_value,
    "Total investment market value",
    COLORS["sky"],
    previous_delta("total_aum", " Cr", 10000000),
    "normal"
)

show_kpi(
    kpi_columns[2],
    "Customer Acquisition Cost",
    cac_value,
    "Cost per acquired customer",
    COLORS["amber"],
    previous_delta("cac", " ₹"),
    "inverse"
)

show_kpi(
    kpi_columns[3],
    "Net Promoter Score",
    nps_value,
    "Customer loyalty indicator",
    COLORS["orange"],
    previous_delta("nps_score", " pts"),
    "normal"
)

show_kpi(
    kpi_columns[4],
    "Loan Default Rate",
    default_value,
    "Portfolio credit risk",
    COLORS["deep_space"],
    previous_delta("default_rate", " pp"),
    "inverse"
)


# =====================================================
# CHART HELPER
# =====================================================

def show_chart(
    data,
    x,
    y,
    title,
    y_label,
    color,
    prefix="",
    suffix="",
    tickformat=None,
    y_range=None,
    zero_line=False
):

    chart_data = data.dropna(subset=[y]).copy()

    if chart_data.empty:
        st.info(f"No data available for {title}.")
        return

    fig = px.line(
        chart_data,
        x=x,
        y=y,
        markers=True,
        template=CHART_TEMPLATE
    )

    fig.update_traces(
        line=dict(
            color=color,
            width=3
        ),
        marker=dict(
            size=7,
            color=color,
            line=dict(
                width=1,
                color=COLORS["deep_space"]
            )
        ),
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            + y_label
            + ": "
            + prefix
            + "%{y:,.2f}"
            + suffix
            + "<extra></extra>"
        )
    )

    fig.update_layout(
        height=360,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Segoe UI, sans-serif",
            color=TEXT_COLOR,
            size=12
        ),
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(
                size=16,
                color=TEXT_COLOR
            )
        ),
        xaxis_title="Reporting Month",
        yaxis_title=y_label,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=45
        ),
        hovermode="x unified",
        showlegend=False
    )

    fig.update_xaxes(
        showgrid=False,
        tickformat="%b %Y",
        nticks=8,
        tickangle=-25,
        automargin=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS["sky"],
        gridwidth=0.6,
        zeroline=zero_line,
        zerolinecolor=COLORS["blue_green"],
        zerolinewidth=1,
        automargin=True,
        tickprefix=prefix,
        ticksuffix=suffix,
        tickformat=tickformat
    )

    if y_range is not None:
        fig.update_yaxes(range=y_range)

    with st.container(border=True):
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "responsive": True,
                "modeBarButtonsToRemove": [
                    "lasso2d",
                    "select2d"
                ]
            }
        )


# =====================================================
# INVESTMENT PERFORMANCE
# =====================================================

has_investment_data = (
    df["roi_percentage"].notna().any()
    or df["total_aum"].notna().any()
)

if has_investment_data:

    st.markdown(
        '<div class="section-heading">Investment Performance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Understand investment returns and the growth of managed assets.'
        '</div>',
        unsafe_allow_html=True
    )

    chart1, chart2 = st.columns(2)

    with chart1:
        show_chart(
            df,
            "report_month",
            "roi_percentage",
            "Monthly Return on Investment",
            "ROI",
            COLORS["blue_green"],
            suffix="%"
        )

    with chart2:

        aum_chart_df = df.copy()

        aum_chart_df["aum_crore"] = (
            aum_chart_df["total_aum"] / 10000000
        )

        show_chart(
            aum_chart_df,
            "report_month",
            "aum_crore",
            "Assets Under Management",
            "AUM (₹ Crore)",
            COLORS["sky"],
            prefix="₹",
            suffix=" Cr"
        )


# =====================================================
# CUSTOMER PERFORMANCE
# =====================================================

st.markdown(
    '<div class="section-heading">Customer Performance</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Evaluate acquisition efficiency and customer experience.'
    '</div>',
    unsafe_allow_html=True
)

chart3, chart4 = st.columns(2)

with chart3:
    show_chart(
        df,
        "report_month",
        "cac",
        "Customer Acquisition Cost",
        "CAC (₹)",
        COLORS["amber"],
        prefix="₹"
    )

with chart4:
    show_chart(
        df,
        "report_month",
        "nps_score",
        "Net Promoter Score",
        "NPS",
        COLORS["orange"],
        y_range=[-100, 100],
        zero_line=True
    )


# =====================================================
# LENDING RISK
# =====================================================

has_loan_data = df["default_rate"].notna().any()

if has_loan_data:

    st.markdown(
        '<div class="section-heading">Lending Risk Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Monitor changes in the loan portfolio default rate.'
        '</div>',
        unsafe_allow_html=True
    )

    show_chart(
        df,
        "report_month",
        "default_rate",
        "Monthly Loan Default Rate",
        "Default Rate",
        COLORS["deep_space"],
        suffix="%"
    )


# =====================================================
# MONTHLY KPI DETAILS
# =====================================================

st.markdown(
    '<div class="section-heading">Monthly KPI Details</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Review and export the underlying monthly KPI results.'
    '</div>',
    unsafe_allow_html=True
)

display_df = df.copy()

display_df["report_month"] = pd.to_datetime(
    display_df["report_month"]
).dt.strftime("%b %Y")

display_df = display_df.rename(
    columns={
        "report_month": "Reporting Month",
        "roi_percentage": "ROI (%)",
        "total_aum": "AUM (₹)",
        "cac": "CAC (₹)",
        "nps_score": "NPS",
        "default_rate": "Default Rate (%)"
    }
)

with st.container(border=True):

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "ROI (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "AUM (₹)": st.column_config.NumberColumn(
                format="₹%.2f"
            ),
            "CAC (₹)": st.column_config.NumberColumn(
                format="₹%.2f"
            ),
            "NPS": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Default Rate (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            )
        }
    )


# =====================================================
# CSV DOWNLOAD
# =====================================================

csv = df.to_csv(index=False).encode("utf-8")

download_col, info_col = st.columns([1, 3])

with download_col:
    st.download_button(
        label="↓ Download KPI Data",
        data=csv,
        file_name="financial_services_kpis.csv",
        mime="text/csv",
        use_container_width=True
    )

with info_col:
    st.caption(
        f"{len(df)} monthly records available for the selected filters."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    "**FINANCIAL PERFORMANCE & INTELLIGENCE**"
)

st.caption(
    "Built with Python · Streamlit · PostgreSQL · Plotly"
)

st.caption(
    "Synthetic data for analytical demonstration"
)
