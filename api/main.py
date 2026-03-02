from flask import Flask, request, jsonify
import os
import traceback

app = Flask(__name__)

# 调试：打印所有环境变量（确认TOKEN）
print("=== STARTUP ===")
print("BOT_TOKEN exists:", bool(os.getenv('BOT_TOKEN')))
print("BOT_TOKEN preview:", os.getenv('BOT_TOKEN', '***HIDDEN***')[:10] + "..." if os.getenv('BOT_TOKEN') else 'MISSING')

BOT_TOKEN = os.getenv('BOT_TOKEN')

@app.route('/', methods=['POST', 'GET'])
def webhook():
    print("=== REQUEST START ===")
    print("Method:", request.method)
    
    if request.method == 'GET':
        print("GET request - health check")
        return jsonify({"status": "alive", "token_ok": bool(BOT_TOKEN)})
    
    print("=== PROCESSING POST ===")
    
    # Step 1: 获取raw数据
    raw_data = request.get_data(as_text=True)
    print("Step 1 - Raw data:", raw_data[:200])
    
    # Step 2: 尝试JSON解析
    try:
        data = request.get_json()
        print("Step 2 - JSON OK, keys:", list(data.keys()) if data else 'NO DATA')
    except Exception as e:
        print("Step 2 - JSON ERROR:", str(e))
        return jsonify({"step": 2, "error": str(e)}), 400
    
    # Step 3: 检查message结构
    if 'message' not in data:
        print("Step 3 - No message field")
        return jsonify({"step": 3, "error": "No message"}), 400
    
    message = data['message']
    print("Step 3 - Message keys:", list(message.keys()))
    
    # Step 4: 提取chat_id和text
    try:
        chat_id = message['chat']['id']
        text = message.get('text', '')
        print(f"Step 4 - chat_id: {chat_id}, text: '{text}'")
    except Exception as e:
        print("Step 4 - Parse ERROR:", str(e))
        return jsonify({"step": 4, "error": str(e)}), 400
    
    # Step 5: 测试BOT_TOKEN
    if not BOT_TOKEN:
        print("Step 5 - NO BOT_TOKEN")
        return jsonify({"step": 5, "error": "No BOT_TOKEN"}), 500
    
    print("Step 5 - BOT_TOKEN OK")
    
    # Step 6: 发送最简单消息（无复杂逻辑）
    try:
        print("Step 6 - Sending simple message...")
        send_simple_message(chat_id, f"收到: {text[:50]}")
        print("Step 6 - Send SUCCESS")
    except Exception as e:
        print("Step 6 - Send ERROR:", str(e))
        return jsonify({"step": 6, "error": str(e)}), 500
    
    print("=== REQUEST SUCCESS ===")
    return jsonify({"status": "ok", "step": 7})

def send_simple_message(chat_id, text):
    """最简单的Telegram消息（无Markdown）"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    print(f"Sending: {payload}")
    
    import requests
    resp = requests.post(url, json=payload, timeout=10)
    print(f"Telegram API response: {resp.status_code} - {resp.text[:200]}")
    
    if resp.status_code != 200:
        raise Exception(f"Telegram API failed: {resp.status_code}")

if __name__ == '__main__':
    app.run(debug=True)
