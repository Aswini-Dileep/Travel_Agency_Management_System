# generate_products.py

import random
from datetime import datetime, timedelta
from database.db import get_connection

def products_exist():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    conn.close()

    return count > 0


def generate_products(n=1000):
    conn = get_connection()
    cursor = conn.cursor()

    product_types = ["Flight", "Hotel", "Cruise"]
    seasons = ["Low", "Peak"]

    for i in range(n):
        product_type = random.choice(product_types)
        season = random.choice(seasons)

        product_name = f"{product_type} Package {random.randint(1,1000)}"

        base_commission = random.randint(3, 10)

        created_date = datetime.now() - timedelta(days=random.randint(1, 30))

        cursor.execute("""
        INSERT INTO products (product_name, product_type, season, base_commission, created_date)
        VALUES (?, ?, ?, ?, ?)
        """, (product_name, product_type, season, base_commission, created_date.strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()