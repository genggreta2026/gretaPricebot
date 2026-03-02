from flask import Flask, request, jsonify
import requests
import os
import json
import re

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

@app.route('/', methods=['POST', 'GET'])
def webhook():
    """Telegram Webhook + 健康检查"""
    if request.method == 'GET':
        return jsonify({"status": "greta-price-bot ok"})
    
    try:
        # 解析Telegram消息
        data = request.get_json()
        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        
        # 处理命令
        if text == '/start':
            send_message(chat_id, get_start_message())
        elif re.match(r'/price\s+\w+', text):
            coin = text.split(' ', 1)[1].upper()
            send_message(chat_id, f"⏳ 查询 {coin} 价格...")
            price_text = get_price_response(coin)
            send_message(chat_id, price_text)
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_start_message():
    """启动消息"""
    return """🚀 行情 Bot 已启动！
📊 /price BTC - 查询比特币价格
📊 /price ETH - 查询以太坊价格"""

def get_price_response(symbol):
    """获取币安价格 + KAI链接"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        price = float(data['price'])
        
        return f"""💰 {symbol}/USDT: **${price:,.4f}**

📈 [Trade Now（立即交易）](https://kai.com/register?inviteCode=G6D7B9)
😇 [Ecological Partner（成为合伙人）](https://kai.com/kai-ambassador.html)
👸 [C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)"""
    except:
        return f"❌ {symbol} 查询失败，请稍后重试"

def send_message(chat_id, text):
    """发送Telegram消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=10)

if __name__ == '__main__':
    app.run(debug=True)
