from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "greta-price-bot production ready"})
    
    try:
        data = request.get_json()
        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        
        # /start 命令
        if text == '/start':
            send_message(chat_id, """🚀 *KAI行情小助手* 已启动！🎉

📊 *常用命令*：
/price BTC - 比特币实时价格
/price ETH - 以太坊实时价格  
/price SOL - Solana实时价格

💎 *KAI全球站* - 您的最佳交易平台！""")
        
        # /price 命令
        elif re.match(r'^/price\s+(\w+)$', text):
            coin = re.match(r'^/price\s+(\w+)$', text).group(1).upper()
            send_message(chat_id, f"⏳ 查询 *{coin}* 实时价格...")
            
            try:
                price_text = get_binance_price(coin)
                send_message(chat_id, price_text)
            except Exception as e:
                send_message(chat_id, f"❌ *{coin}* 查询失败，请稍后重试\n\n💡 尝试其他币种：`/price ETH`")
        
        # 其他消息
        else:
            send_message(chat_id, """📝 *使用说明*：

/start - 显示此帮助
/price BTC - 查询比特币价格
/price ETH - 查询以太坊价格

💎 *立即加入KAI全球站* 👇""")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_binance_price(symbol):
    """获取币安实时价格 + KAI三连推广链接"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    price = float(data['price'])
    
    return f"""💰 *{symbol}/USDT: ${price:,.2f}*

📈 *[立即交易 Trade Now](https://kai.com/register?inviteCode=G6D7B9)*
😇 *[合伙人计划 Ecological Partner](https://kai.com/kai-ambassador.html)*
👸 *[C2C商家招募 C2C Merchant](https://kai.com/register?inviteCode=G6D7B9)*

*实时价格 | 币安数据 | KAI全球站*"""

def send_message(chat_id, text):
    """稳定发送Telegram消息"""
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
