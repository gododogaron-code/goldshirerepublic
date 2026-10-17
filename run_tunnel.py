import subprocess
import re
import sys
import time
import urllib.request
import json

BOT_TOKEN = "8931995816:AAEY6YuEGAR_vvPlIQSwlW6S2JMF2Aisjn4"

def setup_telegram_menu_button(web_app_url):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
    payload = {
        "menu_button": {
            "type": "web_app",
            "text": "⚔️ Златоземье",
            "web_app": {
                "url": web_app_url
            }
        }
    }
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            print("Telegram Menu Button set response:", res_data)
            return res_data.get('ok', False)
    except Exception as e:
        print("Failed to set menu button:", e)
        return False

def main():
    print("Starting Cloudflare Tunnel for http://127.0.0.1:5000 ...")
    cmd = [r".\cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:5000"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace'
    )

    tunnel_url = None
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

    start_time = time.time()
    while time.time() - start_time < 35:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                print("Process terminated prematurely")
                break
            time.sleep(0.1)
            continue
        print(line.strip())
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if tunnel_url:
        print("\n" + "="*50)
        print(f"SUCCESS! Tunnel URL: {tunnel_url}")
        print("="*50 + "\n")
        with open("tunnel_url.txt", "w", encoding="utf-8") as f:
            f.write(tunnel_url)

        # Set up Telegram menu button
        success = setup_telegram_menu_button(tunnel_url)
        if success:
            print("Telegram menu button successfully configured!")
        else:
            print("Warning: could not set menu button automatically.")
    else:
        print("Could not find trycloudflare.com URL in output.")

    # Keep running
    try:
        for line in proc.stdout:
            # Silent keepalive
            pass
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()
