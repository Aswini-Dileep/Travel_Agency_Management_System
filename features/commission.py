# commission.py

from datetime import datetime
from database.db import get_connection
import pandas as pd

def calculate_commission_from_sales():

    conn = get_connection()

    query = """
    SELECT s.agent_name, s.agency_name, s.product_name, s.sold_date,
           p.product_type, p.season, p.base_commission, p.created_date
    FROM sales s
    JOIN products p 
    ON s.product_name = p.product_name
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Handle no data
    if df.empty:
        return pd.DataFrame({"message": ["No matching sales-product data found"]})

    results = []

    for _, row in df.iterrows():

        sold_date = datetime.strptime(row["sold_date"], "%Y-%m-%d")
        created_date = datetime.strptime(row["created_date"], "%Y-%m-%d")

        # 🚨 Invalid case
        if sold_date < created_date:
            continue

        # ✅ Valid case
        days = (sold_date - created_date).days

        # Base commission
        total_commission = row["base_commission"]

        # Season bonus
        if row["season"] == "Low":
            total_commission += 5

        # Speed bonus
        if days <= 5:
            total_commission += 5

        # 🔥 Commission Split
        agent_commission = round(total_commission * 0.6, 2)
        agency_commission = round(total_commission * 0.4, 2)

        results.append({
            "agent_name": row["agent_name"],
            "agency_name": row["agency_name"],
            "product": row["product_name"],
            "days_to_sell": days,
            "total_commission": total_commission,
            "agent_commission": agent_commission,
            "agency_commission": agency_commission
        })

    return pd.DataFrame(results)