# app.py

import streamlit as st
import pandas as pd
import plotly.express as px


from database.models import create_tables
from database.db import get_connection
from features.upload import upload_excel
from features.search import search_agents
from features.commission import calculate_commission_from_sales
from features.ai_advisor import get_ai_advice
from utils.generate_products import generate_products, products_exist

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Travel Agency App", layout="wide")

# =========================
# 🎨 GLOBAL UI STYLE
# =========================
st.markdown("""
<style>

/* SECTION HEADER */
.section-header {
    text-align: center;
    color: #0077b6;
    font-weight: bold;
    font-size: 52px;
    margin-top: 20px;
}
            
/* SECTION TITLE */
.section-title {
    text-align: center;
    color: #0077b6;
    font-weight: bold;
    font-size: 28px;
    margin-top: 50px;
    margin-bottom: 20px
}

/* DESCRIPTION */
.description {
    text-align: center;
    color: black;
    font-size: 16px;
    margin-bottom: 30px;
}

/* CARD */
.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 30px;
}

/* INPUT */
.stTextInput input {
    background-color: #caf0f8;
    border-radius: 10px;
}

/* FILE UPLOADER */
.stFileUploader {
    background-color: #caf0f8;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(to right, #90e0ef, #48cae4);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    text-align: center;
}

/* TABLE HEADER */
thead tr th {
    background-color: #caf0f8 !important;
    color: black !important;
    font-weight: bold;
}

/* TABLE BODY */
tbody tr td {
    color: black !important;
}

/* RADIO */
.stRadio > div {
    display: flex;
    justify-content: center;
}

/* METRIC CARDS */
[data-testid="stMetric"] {
    background-color: #caf0f8;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE + DESCRIPTION
# =========================
st.markdown('<div class="section-header">Travel Agency Management System</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Smart commission tracking and AI insights for travel agencies</div>', unsafe_allow_html=True)
st.divider()

# =========================
# SETUP
# =========================
create_tables()

if not products_exist():
    generate_products(1000)

# =========================
# 📤 UPLOAD SECTION
# =========================
st.markdown('<div class="section-title">Upload Sales Data</div>', unsafe_allow_html=True)

with st.container():
    #st.markdown('<div class="card">', unsafe_allow_html=True)

    file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if file is not None:
        df = upload_excel(file)
        st.success("Data uploaded successfully!")
        st.dataframe(df)

    st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# =========================
# 🔍 SEARCH SECTION
# =========================
st.markdown('<div class="section-title">Search Agent / Agency</div>', unsafe_allow_html=True)

with st.container():
    #st.markdown('<div class="card">', unsafe_allow_html=True)

    search_query = st.text_input("Search by Agent or Agency")

    if search_query:
        results = search_agents(search_query)

        if not results.empty:
            st.dataframe(results)
        else:
            st.warning("No results found")

    st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# =========================
# 💰 COMMISSION SECTION
# =========================
st.markdown('<div class="section-title">Sales Commission</div>', unsafe_allow_html=True)

with st.container():
   # st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.button("Calculate Commission from Sales"):
        df = calculate_commission_from_sales()
        st.success("Commission calculated successfully!")
        st.dataframe(df.head(50))

    st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# =========================
# 🤖 AI ADVISOR
# =========================
st.markdown('<div class="section-title">AI Advisor</div>', unsafe_allow_html=True)

with st.container():
    #st.markdown('<div class="card">', unsafe_allow_html=True)

    search_type = st.radio("Search Type", ["Agent", "Agency"], horizontal=True)
    search_input = st.text_input(f"Search {search_type}")

    if search_input:

        conn = get_connection()

        if search_type == "Agent":
            query = """
                SELECT DISTINCT s.agent_name, s.agency_name, s.product_name, s.sold_date,
                       p.product_type, p.season, p.created_date
                FROM sales s
                JOIN products p ON s.product_name = p.product_name
                WHERE LOWER(s.agent_name) LIKE LOWER(?)
                GROUP BY s.agent_name, s.agency_name, s.product_name, s.sold_date
                LIMIT 50
            """
        else:
            query = """
                SELECT DISTINCT s.agent_name, s.agency_name, s.product_name, s.sold_date,
                       p.product_type, p.season, p.created_date
                FROM sales s
                JOIN products p ON s.product_name = p.product_name
                WHERE LOWER(s.agency_name) LIKE LOWER(?)
                GROUP BY s.agent_name, s.agency_name, s.product_name, s.sold_date
                LIMIT 50
            """

        df = pd.read_sql_query(query, conn, params=(f"%{search_input}%",))
        conn.close()

        if not df.empty:

            selected_index = st.selectbox(
                "Choose record",
                df.index,
                format_func=lambda i: f"{df.iloc[i]['agent_name']} ({df.iloc[i]['agency_name']}) - {df.iloc[i]['product_name']}"
            )

            row = df.iloc[selected_index]

            if st.button("Get AI Advice"):

                from datetime import datetime

                sold_date = datetime.strptime(row["sold_date"], "%Y-%m-%d")
                created_date = datetime.strptime(row["created_date"], "%Y-%m-%d")

                if sold_date < created_date:
                    st.warning("Invalid data")
                else:
                    days = (sold_date - created_date).days

                    advice = get_ai_advice(
                        row["product_type"],
                        row["season"],
                        days
                    )

                    st.info(advice)

        else:
            st.warning("No records found")

    st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# =========================
# 📊 DASHBOARD
# =========================


st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)

with st.container():

    df_dashboard = calculate_commission_from_sales()

    if df_dashboard.empty or "message" in df_dashboard.columns:
        st.warning("No data available")
    else:
        col1, col2, col3 = st.columns(3)

        total_sales = len(df_dashboard)

        valid = df_dashboard[df_dashboard["total_commission"] != "Invalid"]

        avg = valid["total_commission"].astype(float).mean() if not valid.empty else 0
        invalid = (df_dashboard["days_to_sell"] == "Invalid").sum()

        col1.metric("Total Sales", total_sales)
        col2.metric("Avg Commission", round(avg, 2))
        col3.metric("Invalid Records", invalid)

        # =========================
        # 📊 GRAPHS
        # =========================

        col4, col5 = st.columns(2)

        # 🔹 Product Distribution
        product_counts = df_dashboard["product"].value_counts().head(10)

        fig1 = px.bar(
            product_counts,
            title="Top 10 Products",
            labels={"value": "Sales Count", "index": "Product"},
        )
        fig1.update_layout(title_x=0.5)
        fig1.update_traces(marker_color="#0077b6")

        col4.plotly_chart(fig1, use_container_width=True)

        # 🔹 Top Agents
        top_agents = (
            valid.groupby("agent_name")["agent_commission"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        fig2 = px.bar(
            top_agents,
            title="Top Performing Agents",
            labels={"value": "Commission", "agent_name": "Agent"},
        )
        fig2.update_layout(title_x=0.5)
        fig2.update_traces(marker_color="#0077b6")

        col5.plotly_chart(fig2, use_container_width=True)

        # 🔹 Commission Distribution
        commission_counts = valid["total_commission"].value_counts()

        fig3 = px.bar(
            commission_counts,
            title="Commission Distribution",
            labels={"value": "Frequency", "index": "Commission"},
        )
        fig3.update_layout(title_x=0.5)
        fig3.update_traces(marker_color="#0077b6")

        st.plotly_chart(fig3, use_container_width=True)