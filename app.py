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
st.header("📤 Upload Agent Data")

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
# 🤖 AI ADVISOR (SCALABLE)
# =========================
st.header("🤖 AI Commission Advisor")

agent_search = st.text_input("Search Agent for AI Advice")

if agent_search:

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT s.agent_name, s.product_name, s.sold_date,
               p.product_type, p.season, p.created_date
        FROM sales s
        JOIN products p ON s.product_name = p.product_name
        WHERE LOWER(s.agent_name) LIKE LOWER(?)
    """, conn, params=(f"%{agent_search}%",))

    conn.close()

    if df.empty:
        st.warning("No sales found for this agent")
    else:
        st.write("Select a sale record:")

        selected_index = st.selectbox(
            "Choose record",
            df.index,
            format_func=lambda i: f"{df.loc[i, 'agent_name']} - {df.loc[i, 'product_name']}"
        )

        row = df.loc[selected_index]

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