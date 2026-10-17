import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_goldshire.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_token TEXT UNIQUE NOT NULL,
        character_name TEXT NOT NULL,
        faction TEXT NOT NULL,
        wow_class TEXT DEFAULT 'warrior',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Default settings
    default_settings = {
        "server_title": "WoW Forever",
        "server_subtitle": "the goldshire republick",
        "countdown_target": "2026-11-04T15:00:00+03:00",
        "server_info": "WoW Forever • Версия 1.0 (Vanilla) • Рейты х1 • Открытие 4 ноября в 15:00 МСК",
        "guild_name": "the goldshire republick",
        "tavern_welcome": "Добро пожаловать в Златоземье! Сообщество the goldshire republick собирается здесь. 4 ноября в 15:00 МСК состоится открытие сервера WoW Forever 1.0!"
    }

    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
