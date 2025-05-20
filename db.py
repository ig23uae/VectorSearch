import sqlite3
import os

DB_PATH = "storage/products.db"


def init_db():
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            text TEXT,
            page INTEGER
        )
    """)
    conn.commit()
    conn.close()


def insert_product(model, text, page):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (model, text, page) VALUES (?, ?, ?)", (model, text, page))
    conn.commit()
    conn.close()


def get_products_by_ids(ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, model FROM products WHERE id IN ({','.join(['?'] * len(ids))})
    """, ids)
    rows = cursor.fetchall()
    conn.close()
    return rows
