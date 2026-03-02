from flask import Flask, request, jsonify
import requests
import os
import re
import time

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# CoinGecko币种映射
COIN_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin'
}

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "greta-price-bot CoinGecko PRODUCTION"})
    
    try:
        data = request.get_json()
        chat_id = data['message']['chat']['id']
        text = data['message']['text'].strip()
        
        # /start 命令
        if text == '/start':
            send_message(chat_id, get_start_message())
        # /price 命令
        elif re.match(r'^/price\s+(\w+)$', text):
            coin = re.match(r'^/price\s+(\w+)$', text).group(1).upper()
            send_message(chat_id, f"⏳ 查询 *{coin}* 实时价格...")
            price_text = get_coingecko_price(coin)
            send_message(chat_id, price_text)
        else:
            send_message(chat_id, get_help_message())
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "ok"}), 200

def get_start_message():
    """启动消息"""
    return """🚀 *KAI行情小助手* 实时上线！🎉

📊 `/price BTC` - 比特币实时价格
📊 `/price ETH` - 以太坊实时价格  
📊 `/price SOL` - Solana实时价格

💎 *KAI全球站* - 安全 • 快速 • 全球！"""

def get_help_message():
    """帮助消息"""
    return """📝 *使用说明*：

🚀 `/start` - 显示帮助
💰 `/price BTC` - 比特币价格
💰 `/price ETH` - 以太坊价格  
💰 `/price SOL` - Solana价格

💎 *立即加入KAI全球站* 👇"""

def get_coingecko_price(symbol):
    """CoinGecko API - 超稳定重试"""
    if symbol not in COIN_MAP:
        return f"""❌ *{symbol}* 暂不支持

💡 支持币种：BTC, ETH, SOL, BNB, XRP, ADA, DOGE

📈 [立即交易](https://kai.com/register?inviteCode=G6D7B9)"""
    
    coin_id = COIN_MAP[symbol]
    
    # 3次重试机制
    for attempt in range(3):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            
            data = resp.json()
            if coin_id in data and 'usd' in data[coin_id]:
                price = float(data[coin_id]['usd'])
                return format_price_message(symbol, price)
                
        except requests.exceptions.Timeout:
            time.sleep(2 ** attempt)
            continue
        except requests.exceptions.RequestException:
            time.sleep(1)
            continue
        except (KeyError, ValueError):
            break
    
    # 优雅降级 - 显示KAI链接
    return f"""💰 *{symbol}* 价格查询中...

📈 [Trade Now（立即交易）](https://kai.com/register?inviteCode=G6D7B9)
😇 [Ecological Partner（成为合伙人）](https://kai.com/kai-ambassador.html)
👸 [C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)

*全球聚合实时价格 | CoinGecko数据*"""

def format_price_message(symbol, price):
    """价格格式化"""
    return f"""💰 *{symbol}/USD: ${price:,.4f}*

📈 [Trade Now（立即交易）](https://kai.com/register?inviteCode=G6D7B9)
😇 [Ecological Partner（成为合伙人）](https://kai.com/kai-ambassador.html)
👸 [C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)

*全球聚合实时价格 | CoinGecko数据*"""

def send_message(chat_id, text):
    """稳定发送 - Markdown + 纯文本降级"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Markdown优先
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=12)
        return
    except:
        # 纯文本降级
        payload.pop("parse_mode", None)
        requests.post(url, json=payload, timeout=5)

if __name__ == '__main__':
    app.run(debug=True)
