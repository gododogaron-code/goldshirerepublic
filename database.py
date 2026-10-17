import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_goldshire.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}:{hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected_hash = stored_hash.split(":")
        calc_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return secrets.compare_digest(calc_hash, expected_hash)
    except Exception:
        return False

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        character_name TEXT NOT NULL,
        faction TEXT DEFAULT 'none',
        wow_class TEXT DEFAULT 'warrior',
        race TEXT DEFAULT 'Человек',
        avatar TEXT DEFAULT 'human_male',
        status_quote TEXT DEFAULT 'Готов к открытию!',
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tavern_board_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'plans',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tavern_board_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES tavern_board_posts(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    # Defaults in settings based on user request
    default_settings = {
        "server_title": "WoW Forever",
        "server_subtitle": "the goldshire republick",
        "countdown_target": "2026-11-04T15:00:00+03:00",
        "server_info": "WoW Forever • Версия 1.0 (Vanilla) • Рейты х1 • Открытие 4 ноября в 15:00 МСК",
        "guild_name": "the goldshire republick",
        "tavern_welcome": "Добро пожаловать в Златоземье! Сообщество the goldshire republick собирается здесь. 4 ноября в 15:00 МСК состоится открытие сервера WoW Forever 1.0!"
    }

    for k, v in default_settings.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # Create admin user if none exists
    cursor.execute("SELECT id FROM users WHERE is_admin = 1")
    admin_exists = cursor.fetchone()
    if not admin_exists:
        admin_pass = hash_password("Goldshire_Forever_2026!#")
        cursor.execute('''
        INSERT INTO users (username, password_hash, character_name, faction, wow_class, race, avatar, status_quote, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', ("admin", admin_pass, "Смотритель Златоземья", "the_world", "paladin", "Человек", "human_male", "the goldshire republick навсегда!"))

        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_id = cursor.fetchone()['id']
        cursor.execute('''
        INSERT INTO messages (user_id, text)
        VALUES (?, ?)
        ''', (admin_id, "Добро пожаловать в Златоземье! Мы не пьем, мы побеждаем. Гильдия: **the goldshire republick**. Открытие 4 ноября в 15:00 МСК! Выбирайте сторону или оставайтесь дома в Златоземье! ⚔️"))

        cursor.execute('''
        INSERT INTO tavern_board_posts (user_id, title, content, category)
        VALUES (?, ?, ?, ?)
        ''', (admin_id, "Старт WoW Forever: 4 ноября в 15:00 МСК (Версия 1.0, Рейты x1)", 
              "Друзья и согильдийцы the goldshire republick! \n\n"
              "Старт назначен на 4 ноября ровно в 15:00 по московскому времени. \n"
              "Версия клиента: 1.0 (Vanilla), рейты классические: x1. \n"
              "Здесь голосуем, координируем пати и составы на прокачку. Пишите свои мысли и ники персонажей в комментариях!", "plans"))

    conn.commit()
    conn.close()

def migrate_existing_db():
    conn = get_db()
    cursor = conn.cursor()
    # Update settings
    cursor.execute("UPDATE settings SET value = 'the goldshire republick' WHERE key = 'server_subtitle'")
    cursor.execute("UPDATE settings SET value = 'Добро пожаловать в Златоземье! Сообщество the goldshire republick собирается здесь. 4 ноября в 15:00 МСК состоится открытие сервера WoW Forever 1.0!' WHERE key = 'tavern_welcome'")
    
    # Update admin user to unbreached strong password and clean name
    new_admin_pass = hash_password("Goldshire_Forever_2026!#")
    cursor.execute('''
    UPDATE users 
    SET password_hash = ?, character_name = 'Смотритель Златоземья' 
    WHERE username = 'admin'
    ''', (new_admin_pass,))
    
    # Clean up any messages mentioning Бордель
    cursor.execute('''
    UPDATE messages 
    SET text = 'Добро пожаловать в Златоземье! Сообщество the goldshire republick собирается здесь. 4 ноября в 15:00 МСК состоится открытие сервера WoW Forever 1.0! Выбирайте сторону: Альянс, Орда или оставайтесь дома в Златоземье! ⚔️'
    WHERE text LIKE '%Бордель%'
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    migrate_existing_db()
    print("Database updated and migrated successfully!")

