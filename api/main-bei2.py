
from flask import Flask, request, jsonify
import requests
import os
import re
import time

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

COIN_MAP = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'USDT': 'tether', 'BNB': 'binancecoin',
    'SOL': 'solana', 'USDC': 'usd-coin', 'XRP': 'ripple', 'DOGE': 'dogecoin',
    'TON': 'the-open-network', 'ADA': 'cardano', 'TRX': 'tron', 'AVAX': 'avalanche-2',
    'SHIB': 'shiba-inu', 'WBTC': 'wrapped-bitcoin', 'LINK': 'chainlink',
    'BCH': 'bitcoin-cash', 'DOT': 'polkadot', 'NEAR': 'near', 'LTC': 'litecoin',
    'UNI': 'uniswap', 'MATIC': 'polygon', 'ICP': 'internet-computer',
    'PEPE': 'pepe', 'KAS': 'kaspa', 'ETC': 'ethereum-classic', 'APT': 'aptos',
    'XMR': 'monero', 'STX': 'blockstack', 'HBAR': 'hedera-hashgraph',
    'VET': 'vechain', 'FIL': 'filecoin', 'CRO': 'crypto-com-chain',
    'ATOM': 'cosmos', 'ARB': 'arbitrum', 'OP': 'optimism'
}

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "greta-price-bot KAI PRODUCTION"})
    
    try:
        data = request.get_json()
        chat_id = data['message']['chat']['id']
        text = data['message']['text'].strip()
        
        if text == '/start':
            send_message(chat_id, get_start_message())
        elif re.match(r'^/price\s+(\w+)$', text):
            coin = re.match(r'^/price\s+(\w+)$', text).group(1).upper()
            send_message(chat_id, f"⏳ Query real-time price of *{coin}* ...")
            price_text = get_coingecko_price(coin)
            send_message(chat_id, price_text)
        else:
            send_message(chat_id, get_help_message())
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "ok"}), 200

def get_start_message():
    return """🚀 KAI行情小助手已启动！

📊 /price BTC - 比特币实时价格
📊 /price ETH - 以太坊实时价格  
📊 /price SOL - Solana实时价格"""

def get_help_message():
    return """📝 使用说明：

/price BTC - 比特币价格
/price ETH - 以太坊价格  
/price SOL - Solana价格

支持35种主流币种"""

def get_coingecko_price(symbol):
    if symbol not in COIN_MAP:
        return f"""❌ {symbol} 暂不支持

支持：BTC ETH SOL BNB XRP ADA DOGE等（35种）\n\n""" + get_kai_links()
    
    coin_id = COIN_MAP[symbol]
    
    for attempt in range(3):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if coin_id in data and 'usd' in data[coin_id]:
                price = float(data[coin_id]['usd'])
                return f"""💰 {symbol}/USD: ${price:,.4f}
""" + get_kai_links()
        except:
            time.sleep(2 ** attempt)
            continue
    
    return """💰 价格查询中...""" + get_kai_links()

def get_kai_links():
    """你的KAI三连链接"""
    return """
📈 [Trade Now（立即交易）](https://kai.com/register?inviteCode=G6D7B9)
😇 [Ecological Partner（成为合伙人）](https://kai.com/kai-ambassador.html)
👸 [C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)"""

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=12)
    except:
        payload.pop("parse_mode", None)
        requests.post(url, json=payload, timeout=5)

if __name__ == '__main__':
    app.run(debug=True)
