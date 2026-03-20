# search.py

import pandas as pd
from database.db import get_connection

def search_agents(query):
    conn = get_connection()

    sql = """
    SELECT DISTINCT agent_name, agency_name
    FROM sales
    WHERE LOWER(agent_name) LIKE LOWER(?) 
       OR LOWER(agency_name) LIKE LOWER(?)
    """

    df = pd.read_sql_query(sql, conn, params=(f"%{query}%", f"%{query}%"))

    conn.close()

    return df