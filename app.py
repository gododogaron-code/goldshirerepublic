import os
import json
import secrets
from flask import Flask, render_template, request, jsonify, session
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

VANILLA_CLASSES = {'warrior', 'paladin', 'hunter', 'rogue', 'priest', 'shaman', 'mage', 'warlock', 'druid'}
FACTIONS = {'alliance', 'horde', 'the_world'}
BOT_TOKEN = "8931995816:AAEY6YuEGAR_vvPlIQSwlW6S2JMF2Aisjn4"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    settings_dict = {row['key']: row['value'] for row in rows}
    return jsonify(settings_dict)

@app.route('/api/factions', methods=['GET'])
def get_factions():
    conn = get_db()
    rows = conn.execute('''
        SELECT id, voter_token, character_name, faction, wow_class, created_at, updated_at
        FROM votes
        ORDER BY updated_at DESC
    ''').fetchall()
    conn.close()

    alliance_list = []
    horde_list = []
    the_world_list = []

    for r in rows:
        item = {
            "id": r['id'],
            "character_name": r['character_name'],
            "faction": r['faction'],
            "wow_class": r['wow_class'] or 'warrior'
        }
        f = r['faction']
        if f == 'alliance':
            alliance_list.append(item)
        elif f == 'horde':
            horde_list.append(item)
        elif f in ('the_world', 'tavern', 'no_play'):
            item['faction'] = 'the_world'
            the_world_list.append(item)

    total_votes = len(alliance_list) + len(horde_list) + len(the_world_list)
    alliance_pct = round((len(alliance_list) / total_votes * 100), 1) if total_votes > 0 else 0
    horde_pct = round((len(horde_list) / total_votes * 100), 1) if total_votes > 0 else 0
    the_world_pct = round((len(the_world_list) / total_votes * 100), 1) if total_votes > 0 else 0

    return jsonify({
        "total_votes": total_votes,
        "counts": {
            "alliance": len(alliance_list),
            "horde": len(horde_list),
            "the_world": len(the_world_list)
        },
        "percentages": {
            "alliance": alliance_pct,
            "horde": horde_pct,
            "the_world": the_world_pct
        },
        "roster": {
            "alliance": alliance_list,
            "horde": horde_list,
            "the_world": the_world_list
        }
    })

@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.json or {}
    character_name = data.get('character_name', '').strip()
    faction = data.get('faction', '').strip()
    wow_class = data.get('wow_class', 'warrior').strip().lower()
    voter_token = data.get('voter_token', '').strip()

    if not voter_token:
        voter_token = session.get('voter_token') or secrets.token_hex(16)
        session['voter_token'] = voter_token

    if not character_name or len(character_name) < 2:
        return jsonify({"error": "Имя или ник должно быть не короче 2 символов!"}), 400

    if faction not in FACTIONS:
        if faction in ('tavern', 'no_play'):
            faction = 'the_world'
        else:
            return jsonify({"error": "Выберите одну из трех сторон!"}), 400

    if wow_class not in VANILLA_CLASSES:
        wow_class = 'warrior'

    conn = get_db()
    cursor = conn.cursor()

    existing = conn.execute("SELECT id FROM votes WHERE voter_token = ?", (voter_token,)).fetchone()
    if existing:
        cursor.execute('''
            UPDATE votes
            SET character_name = ?, faction = ?, wow_class = ?, updated_at = CURRENT_TIMESTAMP
            WHERE voter_token = ?
        ''', (character_name, faction, wow_class, voter_token))
    else:
        cursor.execute('''
            INSERT INTO votes (voter_token, character_name, faction, wow_class)
            VALUES (?, ?, ?, ?)
        ''', (voter_token, character_name, faction, wow_class))

    conn.commit()
    conn.close()

    session['voter_token'] = voter_token

    return jsonify({
        "success": True,
        "voter_token": voter_token,
        "vote": {
            "character_name": character_name,
            "faction": faction,
            "wow_class": wow_class
        }
    })

# Telegram Webhook support
def send_telegram_bot_message(chat_id, text, web_app_url="https://goldshire-republic.onrender.com"):
    import urllib.request
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "⚔️ Войти в Златоземье",
                        "web_app": {"url": web_app_url}
                    }
                ]
            ]
        }
    }
    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("Telegram send error:", e)

@app.route('/api/tg_webhook', methods=['POST'])
def tg_webhook():
    update = request.json or {}
    message = update.get('message')
    if message:
        chat_id = message.get('chat', {}).get('id')
        if chat_id:
            welcome = (
                "🏰 *Добро пожаловать в Златоземье!*\n\n"
                "Гильдия: *the goldshire republick*\n"
                "Сервер: *WoW Forever 1.0 (Vanilla) х1*\n"
                "Открытие: *4 ноября в 15:00 МСК*\n\n"
                "Голосуйте за сторону и смотрите списки игроков:"
            )
            send_telegram_bot_message(chat_id, welcome)
    return jsonify({"ok": True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting WoW Forever Server on port {port} ...")
    app.run(host='0.0.0.0', port=port, debug=False)
