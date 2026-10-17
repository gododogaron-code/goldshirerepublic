import os
import json
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sock import Sock
from database import get_db, hash_password, verify_password, init_db

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
sock = Sock(app)

# Track active WebSocket connections
chat_sockets = set()
whisper_sockets = {}  # user_id -> set of ws connections

def broadcast_chat(message_data):
    dead = set()
    payload = json.dumps({"type": "chat_message", "message": message_data}, ensure_ascii=False)
    for ws in list(chat_sockets):
        try:
            ws.send(payload)
        except Exception:
            dead.add(ws)
    chat_sockets.difference_update(dead)

def send_whisper_notification(sender_id, receiver_id, message_data):
    payload = json.dumps({"type": "whisper_message", "message": message_data}, ensure_ascii=False)
    for uid in (sender_id, receiver_id):
        if uid in whisper_sockets:
            dead = set()
            for ws in list(whisper_sockets[uid]):
                try:
                    ws.send(payload)
                except Exception:
                    dead.add(ws)
            whisper_sockets[uid].difference_update(dead)

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db()
    user = conn.execute("SELECT id, username, character_name, faction, wow_class, race, avatar, status_quote, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        conn.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
    conn.close()
    return dict(user) if user else None

# --- WEB SOCKETS ---

@sock.route('/ws/chat')
def ws_chat(ws):
    chat_sockets.add(ws)
    try:
        while True:
            data = ws.receive()
            if not data:
                break
    except Exception:
        pass
    finally:
        chat_sockets.discard(ws)

@sock.route('/ws/whispers')
def ws_whispers(ws):
    user_id = session.get("user_id")
    if not user_id:
        return
    if user_id not in whisper_sockets:
        whisper_sockets[user_id] = set()
    whisper_sockets[user_id].add(ws)
    try:
        while True:
            data = ws.receive()
            if not data:
                break
    except Exception:
        pass
    finally:
        if user_id in whisper_sockets:
            whisper_sockets[user_id].discard(ws)
            if not whisper_sockets[user_id]:
                del whisper_sockets[user_id]

# --- PAGES ---

@app.route('/')
def index():
    return render_template('index.html')

# --- SETTINGS & COUNTDOWN ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    settings_dict = {row['key']: row['value'] for row in rows}
    return jsonify(settings_dict)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    user = get_current_user()
    if not user or not user.get('is_admin'):
        return jsonify({"error": "Только трактирщик (администратор) может менять настройки таверны!"}), 403
    
    data = request.json or {}
    conn = get_db()
    for key in ['server_title', 'server_subtitle', 'countdown_target', 'server_info', 'tavern_welcome']:
        if key in data:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(data[key]).strip()))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'avatars', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

VANILLA_CLASSES = {'warrior', 'paladin', 'hunter', 'rogue', 'priest', 'shaman', 'mage', 'warlock', 'druid'}
VANILLA_RACES = {'Человек', 'Дворф', 'Ночной эльф', 'Гном', 'Орк', 'Нежить', 'Таурен', 'Тролль'}

@app.route('/api/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "Файл аватара не передан"}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Поддерживаются форматы: PNG, JPG, JPEG, GIF, WEBP"}), 400
    
    unique_name = f"avatar_{uuid.uuid4().hex[:12]}.{ext}"
    dest_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(dest_path)
    avatar_url = f"/static/images/avatars/uploads/{unique_name}"
    return jsonify({"success": True, "avatar_url": avatar_url})

# --- AUTH ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    character_name = data.get('character_name', '').strip() or username
    faction = data.get('faction', 'the_world')
    if faction not in ('alliance', 'horde', 'the_world', 'tavern', 'none'):
        faction = 'the_world'
    if faction == 'tavern':
        faction = 'the_world'

    wow_class = data.get('wow_class', 'warrior')
    if wow_class not in VANILLA_CLASSES:
        wow_class = 'warrior'

    race = data.get('race')
    if not race or race not in VANILLA_RACES:
        race = 'Орк' if faction == 'horde' else 'Человек'

    avatar = data.get('avatar')
    if not avatar:
        avatar = 'orc' if faction == 'horde' else 'human_male'

    status_quote = data.get('status_quote', '').strip()

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Игрок с таким логином уже зарегистрирован!"}), 400

    pwd_hash = hash_password(password)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password_hash, character_name, faction, wow_class, race, avatar, status_quote)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, pwd_hash, character_name, faction, wow_class, race, avatar, status_quote))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session['user_id'] = user_id
    user = get_current_user()

    # Post an announcement in general chat
    faction_names = {'alliance': 'Альянс (тусить в Златоземье) 🦁', 'horde': 'Орда (контролировать Златоземье) ⚔️', 'the_world': 'Не буду играть (Златоземье) ⚪', 'no_play': 'Не буду играть (Златоземье) ⚪', 'tavern': 'Не буду играть (Златоземье) ⚪', 'none': 'раздумья'}
    welcome_text = f"✨ В Златоземье прибыл новый путник: **{character_name}** ({race} {wow_class.capitalize()})! Выбор: {faction_names.get(faction, 'не определился')}."
    
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, text) VALUES (?, ?)", (user_id, welcome_text))
    msg_id = c.lastrowid
    conn.commit()
    
    # Broadcast chat
    msg_row = conn.execute('''
    SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar
    FROM messages m JOIN users u ON m.user_id = u.id WHERE m.id = ?
    ''', (msg_id,)).fetchone()
    conn.close()
    if msg_row:
        broadcast_chat(dict(msg_row))

    return jsonify({"success": True, "user": user})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user or not verify_password(password, user['password_hash']):
        return jsonify({"error": "Неверное имя странника или пароль!"}), 401

    session['user_id'] = user['id']
    return jsonify({"success": True, "user": get_current_user()})

@app.route('/api/telegram_auth', methods=['POST'])
def telegram_auth():
    data = request.json or {}
    tg_user = data.get('tg_user') or {}
    tg_id = tg_user.get('id')
    if not tg_id:
        return jsonify({"error": "Данные Telegram не получены"}), 400

    first_name = (tg_user.get('first_name') or '').strip()
    last_name = (tg_user.get('last_name') or '').strip()
    char_name = f"{first_name} {last_name}".strip() or f"Путник #{tg_id}"
    tg_login = f"tg_{tg_id}"
    photo_url = tg_user.get('photo_url')

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (tg_login,)).fetchone()
    if user:
        session['user_id'] = user['id']
        if photo_url and user['avatar'] in ('human_male', 'orc'):
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (photo_url, user['id']))
            conn.commit()
        conn.close()
        return jsonify({"success": True, "user": get_current_user(), "is_new": False})

    # Create new user for Telegram
    pwd_hash = hash_password(secrets.token_hex(16))
    avatar = photo_url if photo_url else 'human_male'
    faction = 'the_world'
    wow_class = 'warrior'
    race = 'Человек'

    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password_hash, character_name, faction, wow_class, race, avatar, status_quote)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tg_login, pwd_hash, char_name, faction, wow_class, race, avatar, 'Путник из Telegram'))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session['user_id'] = user_id
    current_u = get_current_user()

    # Announce in general chat
    welcome_text = f"✨ В Златоземье прибыл путник из Telegram: **{char_name}**!"
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, text) VALUES (?, ?)", (user_id, welcome_text))
    msg_id = c.lastrowid
    conn.commit()

    msg_row = conn.execute('''
    SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar
    FROM messages m JOIN users u ON m.user_id = u.id WHERE m.id = ?
    ''', (msg_id,)).fetchone()
    conn.close()
    if msg_row:
        broadcast_chat(dict(msg_row))

    return jsonify({"success": True, "user": current_u, "is_new": True})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/api/me', methods=['GET'])
def me():
    user = get_current_user()
    return jsonify({"user": user})

@app.route('/api/profile', methods=['POST'])
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Необходима авторизация"}), 401

    data = request.json or {}
    character_name = data.get('character_name', user['character_name']).strip()
    faction = data.get('faction', user['faction'])
    wow_class = data.get('wow_class', user['wow_class'])
    race = data.get('race', user['race'])
    avatar = data.get('avatar', user['avatar'])
    status_quote = data.get('status_quote', user['status_quote']).strip()
    new_password = data.get('new_password', '').strip()

    if faction not in ('alliance', 'horde', 'the_world', 'tavern', 'none'):
        faction = user['faction']
    if faction == 'tavern':
        faction = 'the_world'

    conn = get_db()
    if new_password and len(new_password) >= 4:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user['id']))

    conn.execute('''
    UPDATE users SET character_name = ?, faction = ?, wow_class = ?, race = ?, avatar = ?, status_quote = ?
    WHERE id = ?
    ''', (character_name, faction, wow_class, race, avatar, status_quote, user['id']))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "user": get_current_user()})

# --- FACTIONS & VOTING ---

@app.route('/api/factions', methods=['GET'])
def get_factions():
    conn = get_db()
    users = conn.execute('''
    SELECT id, username, character_name, faction, wow_class, race, avatar, status_quote, last_seen, created_at
    FROM users
    ORDER BY last_seen DESC
    ''').fetchall()
    conn.close()

    alliance_list = []
    horde_list = []
    the_world_list = []
    undecided_list = []

    for u in users:
        u_dict = dict(u)
        f = u_dict['faction']
        if f == 'alliance':
            alliance_list.append(u_dict)
        elif f == 'horde':
            horde_list.append(u_dict)
        elif f in ('the_world', 'tavern'):
            u_dict['faction'] = 'the_world'
            the_world_list.append(u_dict)
        else:
            undecided_list.append(u_dict)

    total_votes = len(alliance_list) + len(horde_list) + len(the_world_list)
    alliance_pct = round((len(alliance_list) / total_votes * 100), 1) if total_votes > 0 else 0
    horde_pct = round((len(horde_list) / total_votes * 100), 1) if total_votes > 0 else 0
    the_world_pct = round((len(the_world_list) / total_votes * 100), 1) if total_votes > 0 else 0

    return jsonify({
        "total_votes": total_votes,
        "counts": {
            "alliance": len(alliance_list),
            "horde": len(horde_list),
            "the_world": len(the_world_list),
            "undecided": len(undecided_list)
        },
        "percentages": {
            "alliance": alliance_pct,
            "horde": horde_pct,
            "the_world": the_world_pct
        },
        "roster": {
            "alliance": alliance_list,
            "horde": horde_list,
            "the_world": the_world_list,
            "undecided": undecided_list
        }
    })

@app.route('/api/vote', methods=['POST'])
def vote():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Нужно войти или зарегистрироваться, чтобы отдать голос!"}), 401

    data = request.json or {}
    faction = data.get('faction')
    if faction == 'tavern':
        faction = 'the_world'
    if faction not in ('alliance', 'horde', 'the_world'):
        return jsonify({"error": "Неверная фракция"}), 400

    old_faction = user['faction']
    conn = get_db()
    conn.execute("UPDATE users SET faction = ? WHERE id = ?", (faction, user['id']))

    # System message in chat about vote
    faction_labels = {
        'alliance': 'За Альянс (тусить в Златоземье)! 🦁',
        'horde': 'За Орду (контролировать Златоземье)! ⚔️',
        'the_world': 'Не буду играть (остаюсь дома в Златоземье)! ⚪'
    }
    
    if old_faction != faction:
        c = conn.cursor()
        c.execute("INSERT INTO messages (user_id, text) VALUES (?, ?)", 
                  (user['id'], f"📢 **{user['character_name']}** объявляет свой выбор: **{faction_labels[faction]}**"))
        msg_id = c.lastrowid
        conn.commit()

        msg_row = conn.execute('''
        SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar
        FROM messages m JOIN users u ON m.user_id = u.id WHERE m.id = ?
        ''', (msg_id,)).fetchone()
        conn.close()
        if msg_row:
            broadcast_chat(dict(msg_row))
    else:
        conn.commit()
        conn.close()

    return jsonify({"success": True, "faction": faction})

# --- GENERAL CHAT ---

@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    last_id = request.args.get('last_id', 0, type=int)
    conn = get_db()
    if last_id > 0:
        rows = conn.execute('''
        SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar, u.id as user_id
        FROM messages m JOIN users u ON m.user_id = u.id
        WHERE m.id > ?
        ORDER BY m.id ASC
        LIMIT 100
        ''', (last_id,)).fetchall()
    else:
        rows = conn.execute('''
        SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar, u.id as user_id
        FROM messages m JOIN users u ON m.user_id = u.id
        ORDER BY m.id DESC
        LIMIT 60
        ''').fetchall()
        rows = list(reversed(rows))
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/chat/messages', methods=['POST'])
def post_chat_message():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Войдите или зарегистрируйтесь, чтобы писать в чат таверны!"}), 401

    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "Пустое послание нельзя отправить!"}), 400
    if len(text) > 1000:
        text = text[:1000]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, text) VALUES (?, ?)", (user['id'], text))
    msg_id = c.lastrowid
    conn.commit()

    msg_row = conn.execute('''
    SELECT m.id, m.text, m.created_at, u.username, u.character_name, u.faction, u.wow_class, u.avatar, u.id as user_id
    FROM messages m JOIN users u ON m.user_id = u.id WHERE m.id = ?
    ''', (msg_id,)).fetchone()
    conn.close()

    result = dict(msg_row)
    broadcast_chat(result)
    return jsonify({"success": True, "message": result})

# --- WHISPERS (PRIVATE MESSAGING) ---

@app.route('/api/whispers/conversations', methods=['GET'])
def get_whisper_conversations():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Необходима авторизация"}), 401

    conn = get_db()
    # Find all users with whom current user exchanged whispers
    query = '''
    SELECT 
        u.id, u.username, u.character_name, u.faction, u.wow_class, u.avatar, u.status_quote, u.last_seen,
        MAX(pm.created_at) as last_message_time,
        SUM(CASE WHEN pm.receiver_id = ? AND pm.is_read = 0 THEN 1 ELSE 0 END) as unread_count
    FROM users u
    JOIN private_messages pm ON (pm.sender_id = u.id AND pm.receiver_id = ?) OR (pm.sender_id = ? AND pm.receiver_id = u.id)
    WHERE u.id != ?
    GROUP BY u.id
    ORDER BY last_message_time DESC
    '''
    rows = conn.execute(query, (user['id'], user['id'], user['id'], user['id'])).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/whispers/<int:friend_id>', methods=['GET'])
def get_whispers_with_friend(friend_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Необходима авторизация"}), 401

    last_id = request.args.get('last_id', 0, type=int)
    conn = get_db()

    # Mark incoming as read
    conn.execute('''
    UPDATE private_messages SET is_read = 1
    WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
    ''', (friend_id, user['id']))
    conn.commit()

    if last_id > 0:
        rows = conn.execute('''
        SELECT pm.id, pm.sender_id, pm.receiver_id, pm.text, pm.is_read, pm.created_at,
               u_sender.character_name as sender_name, u_sender.avatar as sender_avatar,
               u_sender.faction as sender_faction, u_sender.wow_class as sender_class
        FROM private_messages pm
        JOIN users u_sender ON pm.sender_id = u_sender.id
        WHERE ((pm.sender_id = ? AND pm.receiver_id = ?) OR (pm.sender_id = ? AND pm.receiver_id = ?))
          AND pm.id > ?
        ORDER BY pm.id ASC
        ''', (user['id'], friend_id, friend_id, user['id'], last_id)).fetchall()
    else:
        rows = conn.execute('''
        SELECT pm.id, pm.sender_id, pm.receiver_id, pm.text, pm.is_read, pm.created_at,
               u_sender.character_name as sender_name, u_sender.avatar as sender_avatar,
               u_sender.faction as sender_faction, u_sender.wow_class as sender_class
        FROM private_messages pm
        JOIN users u_sender ON pm.sender_id = u_sender.id
        WHERE ((pm.sender_id = ? AND pm.receiver_id = ?) OR (pm.sender_id = ? AND pm.receiver_id = ?))
        ORDER BY pm.id DESC
        LIMIT 60
        ''', (user['id'], friend_id, friend_id, user['id'])).fetchall()
        rows = list(reversed(rows))

    friend = conn.execute("SELECT id, username, character_name, faction, wow_class, race, avatar, status_quote, last_seen FROM users WHERE id = ?", (friend_id,)).fetchone()
    conn.close()

    return jsonify({
        "friend": dict(friend) if friend else None,
        "messages": [dict(r) for r in rows]
    })

@app.route('/api/whispers/<int:friend_id>', methods=['POST'])
def send_whisper(friend_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Необходима авторизация"}), 401

    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    conn = get_db()
    friend = conn.execute("SELECT id, username, character_name FROM users WHERE id = ?", (friend_id,)).fetchone()
    if not friend:
        conn.close()
        return jsonify({"error": "Игрок не найден в таверне"}), 404

    c = conn.cursor()
    c.execute('''
    INSERT INTO private_messages (sender_id, receiver_id, text)
    VALUES (?, ?, ?)
    ''', (user['id'], friend_id, text))
    msg_id = c.lastrowid
    conn.commit()

    row = conn.execute('''
    SELECT pm.id, pm.sender_id, pm.receiver_id, pm.text, pm.is_read, pm.created_at,
           u_sender.character_name as sender_name, u_sender.avatar as sender_avatar,
           u_sender.faction as sender_faction, u_sender.wow_class as sender_class
    FROM private_messages pm
    JOIN users u_sender ON pm.sender_id = u_sender.id
    WHERE pm.id = ?
    ''', (msg_id,)).fetchone()
    conn.close()

    msg_data = dict(row)
    send_whisper_notification(user['id'], friend_id, msg_data)

    return jsonify({"success": True, "message": msg_data})

# --- TAVERN NOTICE BOARD (ДОСКА ОБЪЯВЛЕНИЙ) ---

@app.route('/api/board', methods=['GET'])
def get_board_posts():
    conn = get_db()
    posts = conn.execute('''
    SELECT p.id, p.title, p.content, p.category, p.created_at,
           u.id as user_id, u.username, u.character_name, u.faction, u.wow_class, u.avatar,
           (SELECT COUNT(*) FROM tavern_board_comments c WHERE c.post_id = p.id) as comment_count
    FROM tavern_board_posts p
    JOIN users u ON p.user_id = u.id
    ORDER BY p.id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(p) for p in posts])

@app.route('/api/board', methods=['POST'])
def create_board_post():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Только завсегдатаи таверны могут вешать свитки на доску!"}), 401

    data = request.json or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', 'plans')

    if not title or len(title) < 3:
        return jsonify({"error": "Заголовок свитка должен быть от 3 символов"}), 400
    if not content:
        return jsonify({"error": "Текст свитка не может быть пустым"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO tavern_board_posts (user_id, title, content, category)
    VALUES (?, ?, ?, ?)
    ''', (user['id'], title, content, category))
    post_id = c.lastrowid
    conn.commit()

    post = conn.execute('''
    SELECT p.id, p.title, p.content, p.category, p.created_at,
           u.id as user_id, u.username, u.character_name, u.faction, u.wow_class, u.avatar,
           0 as comment_count
    FROM tavern_board_posts p
    JOIN users u ON p.user_id = u.id
    WHERE p.id = ?
    ''', (post_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "post": dict(post)})

@app.route('/api/board/<int:post_id>/comments', methods=['GET'])
def get_board_comments(post_id):
    conn = get_db()
    comments = conn.execute('''
    SELECT c.id, c.content, c.created_at,
           u.id as user_id, u.username, u.character_name, u.faction, u.wow_class, u.avatar
    FROM tavern_board_comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.post_id = ?
    ORDER BY c.id ASC
    ''', (post_id,)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in comments])

@app.route('/api/board/<int:post_id>/comments', methods=['POST'])
def add_board_comment(post_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Авторизуйтесь, чтобы оставлять заметку на свитке!"}), 401

    data = request.json or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"error": "Текст комментария не может быть пустым"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO tavern_board_comments (post_id, user_id, content)
    VALUES (?, ?, ?)
    ''', (post_id, user['id'], content))
    comment_id = c.lastrowid
    conn.commit()

    comment = conn.execute('''
    SELECT c.id, c.content, c.created_at,
           u.id as user_id, u.username, u.character_name, u.faction, u.wow_class, u.avatar
    FROM tavern_board_comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.id = ?
    ''', (comment_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "comment": dict(comment)})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting WoW Forever Server on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=False)
