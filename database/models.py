# models.py

from streamlit import cursor

from database.db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Agents table (KEEP THIS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT,
        agency_name TEXT
    )
    """)

    # ✅ Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        product_type TEXT,
        season TEXT,
        base_commission INTEGER,
        created_date TEXT
    )
    """)

    # ✅ Sales table (NEW)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT,
        agency_name TEXT,
        product_name TEXT,
        sold_date TEXT
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent ON sales(agent_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agency ON sales(agency_name)")

    conn.commit()
    conn.close()