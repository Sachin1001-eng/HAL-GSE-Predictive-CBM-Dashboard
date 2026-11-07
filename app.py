import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import io
import sqlite3

# PDF Generation Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ------------------------------------------------------------------
# 1. PAGE CONFIG & ENTERPRISE DARK THEME STYLING
# ------------------------------------------------------------------

st.set_page_config(
    page_title="HAL Aviation Telemetry & Officer Command",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>

    /* =========================================================
       MAIN DARK THEME
       ========================================================= */

    .stApp {
        background-color: #0B0E14 !important;
        color: #F8FAFC !important;
    }


    /* =========================================================
       SIDEBAR
       ========================================================= */

    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: #3B82F6 !important;
        font-weight: 700 !important;
    }


    /* =========================================================
       UPLOADER
       ========================================================= */

    div[data-testid="stFileUploader"] section {
        background-color: #1E293B !important;
        border: 1px dashed #3B82F6 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    div[data-testid="stFileUploader"] section * {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }


    /* =========================================================
       NORMAL INPUT FIELDS
       IMPORTANT:
       These rules are now scoped so they don't interfere
       with the multiselect search/input area.
       ========================================================= */

    div[data-baseweb="input"] > div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="textarea"] > div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }


    /* =========================================================
       MULTISELECT - FINAL FIX
       Removes the BLACK / BLANK GHOST BOX
       ========================================================= */

    div[data-baseweb="select"] {
        background-color: #1E293B !important;
        border-radius: 8px !important;
        width: 100% !important;
        box-shadow: none !important;
    }

    /* Main select control */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }

    /* BaseWeb input wrapper INSIDE multiselect */
    div[data-baseweb="select"] div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: 0 !important;
        width: 0 !important;
    }

    /* BaseWeb input inner wrapper INSIDE multiselect */
    div[data-baseweb="select"] div[data-baseweb="input"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: 0 !important;
        width: 0 !important;
    }

    /* Actual multiselect search input */
    div[data-baseweb="select"] input {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;

        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;

        padding: 0 !important;
        margin: 0 !important;
    }

    /* Hide search input when a selection exists */
    div[data-baseweb="select"]:has(span[data-baseweb="tag"])
    input {
        display: none !important;
    }

    /* Kill remaining input flex space */
    div[data-baseweb="select"]:has(span[data-baseweb="tag"])
    div[data-baseweb="input"] {
        display: none !important;
    }


    /* =========================================================
       SELECTED MULTISELECT TAGS
       ========================================================= */

    div[data-baseweb="select"] span[data-baseweb="tag"] {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        margin: 3px 2px !important;
        border: none !important;
    }

    div[data-baseweb="select"] span[data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }


    /* =========================================================
       MULTISELECT DROPDOWN
       ========================================================= */

    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background-color: #1E293B !important;
    }

    div[data-baseweb="option"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    div[data-baseweb="option"]:hover {
        background-color: #334155 !important;
    }


    /* =========================================================
       LABEL TEXT
       ========================================================= */

    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }


    /* =========================================================
       FORM SUBMIT & ACTION BUTTONS
       ========================================================= */

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100% !important;
        padding: 10px !important;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1D4ED8 !important;
        border-color: #60A5FA !important;
    }


    /* =========================================================
       TABLE
       ========================================================= */

    div[data-testid="stTable"] table {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
        border-radius: 8px !important;
    }

    div[data-testid="stTable"] th {
        background-color: #0F172A !important;
        color: #60A5FA !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #334155 !important;
    }

    div[data-testid="stTable"] td {
        color: #F8FAFC !important;
        border-bottom: 1px solid #334155 !important;
        font-weight: 500 !important;
    }


    /* =========================================================
       DOWNLOAD BUTTONS
       ========================================================= */

    div[data-testid="stDownloadButton"] button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }


    /* =========================================================
       ALERT BANNERS
       ========================================================= */

    .banner-critical {
        background: linear-gradient(135deg, #7F1D1D 0%, #450A0A 100%);
        border-left: 4px solid #EF4444;
        color: #F8FAFC;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        margin-bottom: 16px;
    }

    .banner-healthy {
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border-left: 4px solid #10B981;
        color: #F8FAFC;
        padding: 10px 16px;
        border-radius: 6px;
        font-weight: 600;
        margin-bottom: 16px;
    }


    /* =========================================================
       TYPOGRAPHY
       ========================================================= */

    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    .stCaption {
        color: #94A3B8 !important;
        font-size: 14px !important;
    }


    /* =========================================================
       CUSTOM CARDS
       ========================================================= */

    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }

    .metric-title {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 800;
        margin-top: 6px;
    }


    /* =========================================================
       OFFICER BOX
       ========================================================= */

    .officer-box {
        background-color: #1E293B;
        border-left: 5px solid #3B82F6;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 20px;
    }


    /* =========================================================
       STREAMLIT NATIVE METRICS
       ========================================================= */

    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 14px !important;
    }

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# 2. SQLITE DATABASE LAYER & INIT
# ------------------------------------------------------------------

def init_sqlite_db():
    conn = sqlite3.connect("hal_gse_maintenance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unit_id TEXT,
            officer_name TEXT,
            action_taken TEXT,
            status_override TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


init_sqlite_db()


def save_audit_log(unit_id, officer_name, action_taken, status_override, notes):
    conn = sqlite3.connect("hal_gse_maintenance.db")
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO audit_logs
        (timestamp, unit_id, officer_name, action_taken, status_override, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        now_str,
        unit_id,
        officer_name,
        action_taken,
        status_override,
        notes
    ))

    conn.commit()
    conn.close()


def fetch_audit_logs():
    conn = sqlite3.connect("hal_gse_maintenance.db")

    logs_df = pd.read_sql_query(
        "SELECT * FROM audit_logs ORDER BY id DESC",
        conn
    )

    conn.close()

    return logs_df


# ------------------------------------------------------------------
# 3. DATA PIPELINE WITH RUL ESTIMATION MODEL
# ------------------------------------------------------------------

@st.cache_data
def load_default_telemetry():

    np.random.seed(42)

    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)

    timestamps = pd.date_range(
        start=start_time,
        end=end_time,
        freq="1h"
    )

    units = {
        "GSE-HYD-01": {
            "type": "Hydraulic Power Unit",
            "base_temp": 72,
            "base_press": 3000,
            "base_vib": 1.8
        },

        "GSE-PWR-02": {
            "type": "Ground Power Unit",
            "base_temp": 80,
            "base_press": 115,
            "base_vib": 2.4
        },

        "GSE-ENG-03": {
            "type": "Jet Start Unit",
            "base_temp": 88,
            "base_press": 45,
            "base_vib": 3.1
        },

        "GSE-PNE-04": {
            "type": "Air Conditioning Unit",
            "base_temp": 65,
            "base_press": 200,
            "base_vib": 1.2
        }
    }

    records = []

    for eq_id, specs in units.items():

        for ts in timestamps:

            temp = np.random.normal(
                loc=specs["base_temp"],
                scale=4
            )

            press = np.random.normal(
                loc=specs["base_press"],
                scale=specs["base_press"] * 0.04
            )

            vib = np.random.normal(
                loc=specs["base_vib"],
                scale=0.3
            )

            if np.random.rand() < 0.04:

                temp += np.random.uniform(20, 35)

                vib += np.random.uniform(2.0, 3.8)

            records.append({
                "Timestamp": ts,
                "Unit_ID": eq_id,
                "Unit_Type": specs["type"],
                "Temperature_C": round(temp, 2),
                "Pressure_PSI": round(press, 2),
                "Vibration_mms": round(vib, 2)
            })

    return pd.DataFrame(records)


# ------------------------------------------------------------------
# DATA SOURCE
# ------------------------------------------------------------------

st.sidebar.markdown("### ⚙️ Data Pipeline Source")

data_source = st.sidebar.radio(
    "Select Ingestion Mode:",
    [
        "30-Day Automated Stream",
        "Upload Field CSV Log"
    ]
)


if data_source == "Upload Field CSV Log":

    uploaded_file = st.sidebar.file_uploader(
        "Upload Sensor Log (CSV)",
        type=["csv"]
    )

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        if "Timestamp" in df.columns:
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    else:
        df = load_default_telemetry()

else:

    df = load_default_telemetry()


# ------------------------------------------------------------------
# RISK SCORE
# ------------------------------------------------------------------

df["Risk_Score"] = (
    (df["Temperature_C"] > 90).astype(int) * 40
    +
    (df["Vibration_mms"] > 4.5).astype(int) * 40
    +
    (
        df["Pressure_PSI"]
        < df["Pressure_PSI"].mean() * 0.8
    ).astype(int) * 20
)

df["Status"] = np.where(
    df["Risk_Score"] >= 40,
    "CRITICAL",
    "HEALTHY"
)


# ------------------------------------------------------------------
# ESTIMATED RUL
# ------------------------------------------------------------------

df["Estimated_RUL_Hours"] = np.clip(
    500
    -
    (
        (df["Temperature_C"] - 65).clip(lower=0)
        * 3.5
    )
    -
    (
        df["Vibration_mms"] * 25
    ),
    12,
    500
).round(1)


# ------------------------------------------------------------------
# 4. HEADER & ALERT BANNER
# ------------------------------------------------------------------

st.title(
    "✈️ HAL Ground Equipment Telemetry & Diagnostic Architecture"
)

st.caption(
    "Condition-Based Maintenance (CBM) & Real-Time Predictive Diagnostics"
)


crit_units_df = df[df["Status"] == "CRITICAL"]

critical_count = len(
    crit_units_df["Unit_ID"].unique()
)


col_banner, _ = st.columns([4, 1])

with col_banner:

    if critical_count > 0:

        st.markdown(
            f"""
            <div class="banner-critical">
                🚨 &nbsp;
                <b>EXECUTIVE ALERT:</b>
                &nbsp;
                {critical_count}
                Ground Support Equipment Units Need Immediate Inspection!
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="banner-healthy">
                🟢 &nbsp;
                <b>SYSTEMS OPERATIONAL:</b>
                &nbsp;
                GSE Fleet Operating Within Normal Parameters
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------------------------------------------------------
# SIDEBAR DIAGNOSTIC SLICERS
# ------------------------------------------------------------------

st.sidebar.divider()

st.sidebar.markdown("### 🎛️ Diagnostic Slicers")


selected_units = st.sidebar.multiselect(
    "Select Equipment Units:",
    options=df["Unit_ID"].unique(),
    default=list(df["Unit_ID"].unique())
)


status_filter = st.sidebar.radio(
    "Filter Health Status:",
    options=[
        "All Fleet",
        "Healthy Only",
        "Critical Warnings Only"
    ]
)


filtered_df = df[
    df["Unit_ID"].isin(selected_units)
]


if status_filter == "Healthy Only":

    filtered_df = filtered_df[
        filtered_df["Status"] == "HEALTHY"
    ]

elif status_filter == "Critical Warnings Only":

    filtered_df = filtered_df[
        filtered_df["Status"] == "CRITICAL"
    ]


# ------------------------------------------------------------------
# 5. METRIC CARDS & ANALYST GRAPHS
# ------------------------------------------------------------------

total_telemetry = len(filtered_df)

crit_alerts = len(
    filtered_df[
        filtered_df["Status"] == "CRITICAL"
    ]
)

min_fleet_rul = (
    filtered_df["Estimated_RUL_Hours"].min()
    if not filtered_df.empty
    else 0
)


fleet_health_index = (
    (
        (total_telemetry - crit_alerts)
        / total_telemetry
    ) * 100
    if total_telemetry > 0
    else 0
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Total Logs Scanned
            </div>
            <div class="metric-value">
                {total_telemetry:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Fleet Reliability Index
            </div>
            <div class="metric-value"
                 style="color:#10B981;">
                {fleet_health_index:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Critical Anomalies
            </div>
            <div class="metric-value"
                 style="color:#EF4444;">
                {crit_alerts}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Min Fleet RUL (Life)
            </div>
            <div class="metric-value"
                 style="color:#3B82F6;">
                {min_fleet_rul:.0f} hrs
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ------------------------------------------------------------------
# DARK CHART STYLE
# ------------------------------------------------------------------

def apply_dark_chart_style(fig):

    fig.update_layout(
        paper_bgcolor="#0B0E14",
        plot_bgcolor="#111827",
        font=dict(
            color="#FFFFFF",
            size=12
        ),
        legend=dict(
            font=dict(
                color="#FFFFFF",
                size=12
            )
        ),
        xaxis=dict(
            gridcolor="#1E293B",
            tickfont=dict(
                color="#FFFFFF"
            )
        ),
        yaxis=dict(
            gridcolor="#1E293B",
            tickfont=dict(
                color="#FFFFFF"
            )
        )
    )

    return fig


# ------------------------------------------------------------------
# THERMAL GRAPH + RISK BREAKDOWN
# ------------------------------------------------------------------

col_left, col_right = st.columns([2, 1])


with col_left:

    st.subheader(
        "📊 Thermal Control Limits (UCL Monitor)"
    )

    fig_temp = px.line(
        filtered_df,
        x="Timestamp",
        y="Temperature_C",
        color="Unit_ID",
        template="plotly_dark",
        height=350
    )

    fig_temp.add_hline(
        y=90,
        line_dash="dash",
        line_color="#EF4444"
    )

    st.plotly_chart(
        apply_dark_chart_style(fig_temp),
        use_container_width=True
    )


with col_right:

    st.subheader(
        "⚠️ Risk Breakdown Index"
    )

    status_counts = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Count"
    ]

    fig_donut = px.pie(
        status_counts,
        names="Status",
        values="Count",
        hole=0.6,
        color="Status",
        color_discrete_map={
            "HEALTHY": "#10B981",
            "CRITICAL": "#EF4444"
        },
        template="plotly_dark",
        height=350
    )

    st.plotly_chart(
        apply_dark_chart_style(fig_donut),
        use_container_width=True
    )


# ------------------------------------------------------------------
# VIBRATION + FAILURE CLUSTERING
# ------------------------------------------------------------------

col_b1, col_b2 = st.columns(2)


with col_b1:

    st.subheader(
        "📉 Vibration Spectrum Analysis"
    )

    fig_vib = px.area(
        filtered_df,
        x="Timestamp",
        y="Vibration_mms",
        color="Unit_ID",
        template="plotly_dark",
        height=320
    )

    st.plotly_chart(
        apply_dark_chart_style(fig_vib),
        use_container_width=True
    )


with col_b2:

    st.subheader(
        "🎯 Parameter Failure Risk Clustering"
    )

    fig_scatter = px.scatter(
        filtered_df,
        x="Temperature_C",
        y="Vibration_mms",
        color="Status",
        size="Risk_Score",
        color_discrete_map={
            "HEALTHY": "#10B981",
            "CRITICAL": "#EF4444"
        },
        template="plotly_dark",
        height=320
    )

    st.plotly_chart(
        apply_dark_chart_style(fig_scatter),
        use_container_width=True
    )


st.divider()


# ------------------------------------------------------------------
# 6. GROUND OFFICER EXECUTIVE ACTION TABLE
# ------------------------------------------------------------------

st.subheader(
    "📋 Ground Officer Diagnostic Brief & Maintenance Directives"
)


critical_logs = filtered_df[
    filtered_df["Status"] == "CRITICAL"
]


if not critical_logs.empty:

    with st.container():

        st.markdown(
            """<div class="officer-box">
<h4 style="color:#60A5FA !important; margin-bottom:8px;">📌 Ground Operations Briefing Summary</h4>
<p style="color:#E2E8F0; margin-bottom:0;">High priority operational alerts detected. Ground Maintenance Teams must execute immediate targeted field inspections for the units listed below.</p>
</div>""",
            unsafe_allow_html=True
        )

        directives = []


        for unit in critical_logs["Unit_ID"].unique():

            unit_subset = critical_logs[
                critical_logs["Unit_ID"] == unit
            ]

            unit_data = unit_subset.iloc[0]

            max_temp = unit_subset[
                "Temperature_C"
            ].max()

            max_vib = unit_subset[
                "Vibration_mms"
            ].max()

            min_rul = unit_subset[
                "Estimated_RUL_Hours"
            ].min()


            action = (
                "Inspect Cooling Fans & Hydraulic Fluid"
                if max_temp > 90
                else
                "Check Mechanical Alignment & Bearings"
            )


            directives.append({

                "Unit ID": unit,

                "Equipment Type":
                    unit_data["Unit_Type"],

                "Max Temp Recorded":
                    f"{max_temp} °C",

                "Max Vibration":
                    f"{max_vib} mm/s",

                "Est. RUL Left":
                    f"{min_rul} hrs",

                "Assigned Priority":
                    "🔴 CRITICAL",

                "Required Field Action":
                    action
            })


        st.table(
            pd.DataFrame(directives)
        )


else:

    st.success(
        "✅ No critical alerts found. "
        "Fleet is cleared for normal runway operations."
    )


# ------------------------------------------------------------------
# 7. MAINTENANCE AUDIT LOGBOOK
# ------------------------------------------------------------------

st.divider()

st.subheader(
    "📝 Ground Officer Audit Logbook "
    "(SQLite Database Persistence)"
)


audit_col1, audit_col2 = st.columns([1, 1])


with audit_col1:

    st.markdown(
        "#### Submit Maintenance Action Entry"
    )

    with st.form(
        "audit_form",
        clear_on_submit=True
    ):

        form_unit = st.selectbox(
            "Select Unit ID:",
            options=df["Unit_ID"].unique()
        )

        form_officer = st.text_input(
            "Officer Name / ID:",
            value="Officer Sachin"
        )

        form_action = st.selectbox(
            "Action Executed:",
            [
                "Inspected & Cleared",
                "Replaced Cooling Fan",
                "Fluid Refill",
                "Scheduled Workshop Repair"
            ]
        )

        form_status = st.selectbox(
            "Set Unit Health Status:",
            [
                "RESOLVED / HEALTHY",
                "UNDER MAINTENANCE",
                "CRITICAL HOLD"
            ]
        )

        form_notes = st.text_area(
            "Field Maintenance Notes:"
        )

        submit_btn = st.form_submit_button(
            "💾 Save Entry to Database"
        )


        if submit_btn:

            save_audit_log(
                form_unit,
                form_officer,
                form_action,
                form_status,
                form_notes
            )

            st.success(
                f"Audit log saved successfully for {form_unit}!"
            )


with audit_col2:

    st.markdown(
        "#### Live SQLite Maintenance Logbook Records"
    )

    audit_data = fetch_audit_logs()


    if not audit_data.empty:

        st.dataframe(
            audit_data[
                [
                    "timestamp",
                    "unit_id",
                    "officer_name",
                    "action_taken",
                    "status_override",
                    "notes"
                ]
            ],
            height=280,
            use_container_width=True
        )

    else:

        st.info(
            "No audit logs found in the SQLite database yet."
        )


# ------------------------------------------------------------------
# 8. AUTOMATED PDF & EXCEL REPORT GENERATOR
# ------------------------------------------------------------------

st.divider()

st.subheader(
    "📑 Ground Maintenance Officer Export Center"
)


def generate_pdf_report(dataframe):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10
    )

    normal_style = styles["Normal"]


    elements.append(
        Paragraph(
            "HAL Ground Support Equipment (GSE) Diagnostic Report",
            title_style
        )
    )

    elements.append(
        Paragraph(
            f"Generated on: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )


    crit_df = dataframe[
        dataframe["Status"] == "CRITICAL"
    ].head(10)


    data = [
        [
            "Unit ID",
            "Type",
            "Temp (°C)",
            "Vib (mm/s)",
            "RUL (hrs)",
            "Status"
        ]
    ]


    for _, row in crit_df.iterrows():

        data.append([
            str(row["Unit_ID"]),
            str(row["Unit_Type"]),
            str(row["Temperature_C"]),
            str(row["Vibration_mms"]),
            str(row["Estimated_RUL_Hours"]),
            str(row["Status"])
        ])


    t = Table(
        data,
        colWidths=[
            80,
            140,
            70,
            70,
            70,
            70
        ]
    )


    t.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1E293B")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                8
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F8FAFC")
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.HexColor("#CBD5E1")
            )

        ])
    )


    elements.append(
        Paragraph(
            "Critical Equipment Alerts Summary:",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    elements.append(t)

    doc.build(elements)

    buffer.seek(0)

    return buffer.getvalue()


def generate_two_tab_excel(dataframe):

    output = io.BytesIO()

    critical_df = (
        dataframe[
            dataframe["Status"] == "CRITICAL"
        ]
        .sort_values(
            by="Timestamp",
            ascending=False
        )
    )

    all_df = (
        dataframe
        .sort_values(
            by="Timestamp",
            ascending=False
        )
    )


    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        critical_df.to_excel(
            writer,
            index=False,
            sheet_name="🔴 Critical Alerts Only"
        )

        all_df.to_excel(
            writer,
            index=False,
            sheet_name="📊 All Telemetry Data"
        )


    return output.getvalue()


col_exp1, col_exp2 = st.columns(2)


with col_exp1:

    st.download_button(
        label="📄 Download Official HAL Fleet PDF Brief",
        data=generate_pdf_report(filtered_df),
        file_name="HAL_GSE_Official_Diagnostic_Report.pdf",
        mime="application/pdf"
    )


with col_exp2:

    st.download_button(
        label="📥 Download Officer Maintenance Excel Report (.xlsx)",
        data=generate_two_tab_excel(filtered_df),
        file_name="HAL_GSE_Officer_Diagnostic_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ------------------------------------------------------------------
# 9. LIVE INTERACTIVE FAILURE SIMULATOR
# ------------------------------------------------------------------

st.divider()

st.sidebar.divider()

st.sidebar.markdown(
    "### 🧪 Live GSE Parameter Simulator"
)

st.sidebar.caption(
    "Manually tweak sensor values to simulate "
    "failure scenarios in real-time."
)


sim_temp = st.sidebar.slider(
    "Simulate Temperature (°C)",
    min_value=50.0,
    max_value=130.0,
    value=75.0,
    step=0.5
)


sim_vib = st.sidebar.slider(
    "Simulate Vibration (mm/s)",
    min_value=0.5,
    max_value=8.0,
    value=2.0,
    step=0.1
)


sim_press = st.sidebar.slider(
    "Simulate Pressure (PSI)",
    min_value=30.0,
    max_value=3500.0,
    value=2800.0,
    step=10.0
)


sim_risk = (
    (1 if sim_temp > 90 else 0) * 40
    +
    (1 if sim_vib > 4.5 else 0) * 40
    +
    (1 if sim_press < 1500 else 0) * 20
)


sim_status = (
    "CRITICAL"
    if sim_risk >= 40
    else
    "HEALTHY"
)


sim_rul = round(
    max(
        12.0,
        500
        -
        (
            max(0, sim_temp - 65)
            * 3.5
        )
        -
        (
            sim_vib * 25
        )
    ),
    1
)


st.subheader(
    "🔮 Predictive Machine Simulation Output"
)


sim_col1, sim_col2, sim_col3 = st.columns(3)


with sim_col1:

    st.metric(
        label="Calculated Risk Score",
        value=f"{sim_risk} / 100"
    )


with sim_col2:

    st.metric(
        label="Predicted RUL",
        value=f"{sim_rul} hrs"
    )


with sim_col3:

    if sim_status == "CRITICAL":

        st.error(
            "🚨 Status: CRITICAL FAILURE RISK"
        )

    else:

        st.success(
            "🟢 Status: SYSTEM HEALTHY"
        )