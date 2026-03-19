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

    if df.empty:
        return pd.DataFrame({"message": ["No matching sales-product data found"]})

    results = []

    for _, row in df.iterrows():

        sold_date = datetime.strptime(row["sold_date"], "%Y-%m-%d")
        created_date = datetime.strptime(row["created_date"], "%Y-%m-%d")

        # 🚨 Check invalid case
        if sold_date < created_date:
            results.append({
                "agent_name": row["agent_name"],
                "agency_name": row["agency_name"],
                "product": row["product_name"],
                "days_to_sell": "Invalid",
                "commission": "Invalid"
            })
            continue

        # ✅ Valid case
        days = (sold_date - created_date).days

        commission = row["base_commission"]

        if row["season"] == "Low":
            commission += 5

        if days <= 5:
            commission += 5

        results.append({
            "agent_name": row["agent_name"],
            "agency_name": row["agency_name"],
            "product": row["product_name"],
            "days_to_sell": days,
            "commission": commission
        })

    return pd.DataFrame(results)