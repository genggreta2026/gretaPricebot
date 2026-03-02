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
        return jsonify({"status": "KAI-price-bot PRODUCTION"})
    
    try:
        data = request.get_json()
        chat_id = data['message']['chat']['id']
        text = data['message']['text'].strip()
        
        if text == '/start':
            send_message(chat_id, get_start_message())
        elif re.match(r'^/price\s+(\w+)$', text):
            coin = re.match(r'^/price\s+(\w+)$', text).group(1).upper()
            send_message(chat_id, f"⏳ 查询 *{coin}* 实时价格...")
            price_text = get_price(coin)
            send_message(chat_id, price_text)
        elif text in ['/help', '/coins']:
            send_message(chat_id, get_coin_list())
        else:
            send_message(chat_id, get_help_message())
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "ok"}), 200

def get_start_message():
    return """🚀 *KAI行情小助手* 实时上线！

📊 `/price BTC` - 比特币实时价格
📊 `/price ETH` - 以太坊实时价格  
📊 `/price SOL` - Solana实时价格

📋 `/help` 查看全部35种支持币种"""

def get_help_message():
    return """📝 *快速使用*：

💰 `/price BTC` - 比特币价格
💰 `/price ETH` - 以太坊价格  
💰 `/price PEPE` - Pepe价格

📋 `/help` - 查看全部35币种
🚀 `/start` - 重置帮助"""

def get_coin_list():
    """35币种列表"""
    coins = list(COIN_MAP.keys())
    top10 = ', '.join(coins[:10])
    next15 = ', '.join(coins[10:25])
    last10 = ', '.join(coins[25:])
    
    return f"""📋 *支持35主流币种*

**Top10**: `{top10}`
**11-25**: `{next15}`
**26-35**: `{last10}`

💡 示例：`/price PEPE` `/price KAS`"""

def get_price(symbol):
    if symbol not in COIN_MAP:
        return f"""❌ *{symbol}* 暂不支持

📋 `/help` 查看35种支持币种""" + get_kai_buttons()
    
    coin_id = COIN_MAP[symbol]
    
    for attempt in range(3):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if coin_id in data and 'usd' in data[coin_id]:
                price = float(data[coin_id]['usd'])
                return f"""💰 *{symbol}/USD: ${price:,.4f}*

*实时行情数据*""" + get_kai_buttons()
        except:
            time.sleep(2 ** attempt)
            continue
    
    return f"""💰 *{symbol}* 价格查询中...""" + get_kai_buttons()

def get_kai_buttons():
    """🔥 KAI三连按钮超突出版！"""
    return """
━━━━━━━━━━━━━━━━━━━━━━━━
🚀 *KAI全球站三大机会*

🔥 **立即交易** 👉 https://kai.com/register?inviteCode=G6D7B9
💎 **合伙人计划** 👉 https://kai.com/kai-ambassador.html  
👑 **C2C商家招募** 👉 https://kai.com/register?inviteCode=G6D7B9

━━━━━━━━━━━━━━━━━━━━━━━━
*点击链接直达 | 安全 • 快速 • 全球*"""

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
