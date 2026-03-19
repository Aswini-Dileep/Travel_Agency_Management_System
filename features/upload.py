# upload.py

import pandas as pd
from database.db import get_connection

def upload_excel(file):
    df = pd.read_excel(file)

    conn = get_connection()
    cursor = conn.cursor()

    # 🔥 Clear old data
    cursor.execute("DELETE FROM sales")

    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO sales (agent_name, agency_name, product_name, sold_date) VALUES (?, ?, ?, ?)",
            (
                row["agent_name"],
                row["agency_name"],
                row["product_name"],
                row["sold_date"]
            )
        )

    conn.commit()
    conn.close()

    return df