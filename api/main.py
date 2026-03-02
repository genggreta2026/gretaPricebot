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
            return jsonify({"status": "ok"})
        
        # /price 命令（严格匹配）
        price_match = re.match(r'^/price\s+(\w+)$', text.strip())
        if price_match:
            coin = price_match.group(1).upper()
            send_message(chat_id, f"⏳ 查询 *{coin}* 实时价格...")
            
            price_text = get_price_safe(coin)
            send_message(chat_id, price_text)
            return jsonify({"status": "ok"})
        
        # 其他消息
        send_message(chat_id, """📝 *使用说明*：

🚀 /start - 显示帮助
💰 /price BTC - 比特币价格
💰 /price ETH - 以太坊价格
💰 /price SOL - Solana价格

💎 *立即加入KAI全球站* 👇""")
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"Error: {e}")  # Vercel日志
        return jsonify({"error": str(e)}), 500

def get_price_safe(symbol):
    """超稳定价格查询 + 容错"""
    try:
        # 主流币种列表
        valid_symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE']
        if symbol not in valid_symbols:
            return f"❌ *{symbol}* 暂不支持\n\n💡 试试：`/price BTC` `/price ETH` `/price SOL`"
        
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()  # HTTP错误抛异常
        
        data = resp.json()
        if 'price' not in data:
            raise ValueError("API返回格式异常")
            
        price = float(data['price'])
        return f"""💰 *{symbol}/USDT: ${price:,.2f}*

📈 *[立即交易](https://kai.com/register?inviteCode=G6D7B9)*
😇 *[合伙人计划](https://kai.com/kai-ambassador.html)*
👸 *[C2C商家招募](https://kai.com/register?inviteCode=G6D7B9)*"""
        
    except requests.exceptions.RequestException:
        return f"❌ *{symbol}* 网络查询失败\n\n💡 稍后重试：`/price {symbol}`"
    except (ValueError, KeyError):
        return f"❌ *{symbol}* 数据异常\n\n💡 尝试：`/price BTC` `/price ETH`"
    except Exception:
        return f"❌ *{symbol}* 查询失败\n\n💎 *KAI全球站等你来* 👇"

def send_message(chat_id, text):
    """稳定发送（纯文本降级）"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        # Markdown失败降级纯文本
        payload.pop("parse_mode", None)
        requests.post(url, json=payload, timeout=5)

if __name__ == '__main__':
    app.run(debug=True)
