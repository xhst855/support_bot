import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "data", "tickets.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            message_id INTEGER PRIMARY KEY,
            ticket_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(message_id, ticket_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO tickets (message_id, ticket_id) VALUES (?, ?)', (message_id, ticket_id))
    conn.commit()
    conn.close()

def get_ticket_by_message(message_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT ticket_id FROM tickets WHERE message_id = ?', (message_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
