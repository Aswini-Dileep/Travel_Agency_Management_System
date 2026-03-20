# app.py

import streamlit as st
import pandas as pd

from database.models import create_tables
from database.db import get_connection
from features.upload import upload_excel
from features.search import search_agents
from features.commission import calculate_commission_from_sales
from features.ai_advisor import get_ai_advice
from utils.generate_products import generate_products, products_exist

# Page config
st.set_page_config(page_title="Travel Agency App", layout="wide")

# Title
st.title("✈️ Travel Agency Management System")

# Create DB tables
create_tables()

# Generate products ONLY ONCE
if not products_exist():
    generate_products(1000)


# =========================
# 📤 UPLOAD SECTION
# =========================
st.header("📤 Upload Sales Data")

file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file is not None:
    df = upload_excel(file)
    st.success("Data uploaded successfully!")
    st.dataframe(df)

# =========================
# 🔍 SEARCH SECTION
# =========================
st.header("🔍 Search Agents")

search_query = st.text_input("Search by Agent or Agency")

if search_query:
    results = search_agents(search_query)

    if not results.empty:
        st.dataframe(results)
    else:
        st.warning("No results found")

# =========================
# 💰 SALES-BASED COMMISSION
# =========================
st.header("💰 Commission from Sales Data")

if st.button("Calculate Commission from Sales"):
    df = calculate_commission_from_sales()
    st.success("Commission calculated successfully!")
    st.dataframe(df.head(50))

# =========================
# 🤖 AI ADVISOR (ADVANCED + SCALABLE)
# =========================
st.header("🤖 AI Commission Advisor")

search_type = st.radio("Search Type", ["Agent", "Agency"])
search_input = st.text_input(f"Search {search_type} for AI Advice")

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

    if df.empty:
        st.warning(f"No records found for this {search_type.lower()}")
    else:
        st.write("Select a sale record:")

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
                st.warning("Invalid data: sold before product creation")
            else:
                days = (sold_date - created_date).days

                advice = get_ai_advice(
                    row["product_type"],
                    row["season"],
                    days
                )

                st.info(advice)

# =========================
# 📊 DASHBOARD
# =========================
st.header("📊 Dashboard")

df_dashboard = calculate_commission_from_sales()

if df_dashboard.empty or "message" in df_dashboard.columns:
    st.warning("No data available for dashboard. Please upload data.")
else:
    col1, col2, col3 = st.columns(3)

    total_sales = len(df_dashboard)

    valid_commission = df_dashboard[df_dashboard["total_commission"] != "Invalid"]

    avg_commission = valid_commission["total_commission"].astype(float).mean() if not valid_commission.empty else 0
    invalid_count = (df_dashboard["days_to_sell"] == "Invalid").sum()

    col1.metric("Total Sales", total_sales)
    col2.metric("Avg Commission", round(avg_commission, 2))
    col3.metric("Invalid Records", invalid_count)

    st.subheader("📦 Product Distribution")
    product_counts = (
    df_dashboard["product"]
    .value_counts()
    .sort_values(ascending=False)
    .head(10)
    )
    st.bar_chart(product_counts)

    st.subheader("💰 Commission Distribution")
    st.bar_chart(valid_commission["total_commission"].value_counts())

    st.subheader("🏆 Top Performing Agents")
    top_agents = (
        valid_commission
        .groupby("agent_name")["agent_commission"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    st.bar_chart(top_agents)
