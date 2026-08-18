import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sabitrade.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_input TEXT,
            item_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            verified BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def log_transaction(raw_input, item_name, quantity, unit_price, total_price, verified):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (raw_input, item_name, quantity, unit_price, total_price, verified)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (raw_input, item_name, quantity, unit_price, total_price, verified))
    conn.commit()
    conn.close()
