# db.py

import sqlite3

def get_connection():
    conn = sqlite3.connect("data/database.db", check_same_thread=False,
                           timeout=10)   # 🔥 VERY IMPORTANT
    
    # 🔥 performance boost
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=OFF;")
    
    return conn