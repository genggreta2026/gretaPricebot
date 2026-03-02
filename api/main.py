import os
import asyncio
import logging
import aiohttp
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import json

# 配置
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("请设置 BOT_TOKEN 环境变量")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 你的原命令处理器（保持不变！）
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """启动命令"""
    await update.message.reply_text(
        "🚀 行情 Bot 已启动！\n"
        "📊 /price BTC - 查询比特币价格\n"
        "📊 /price ETH - 查询以太坊价格"
    )

async def get_price(symbol: str):
    """获取币安价格"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return float(data['price'])

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """价格查询"""
    try:
        if not context.args:
            await update.message.reply_text("❌ 请指定币种：/price BTC")
            return
        
        symbol = context.args[0].upper()
        await update.message.reply_text(f"⏳ 查询 {symbol} 价格...")
        
        price = await get_price(symbol)
        await update.message.reply_text(
            f"💰 {symbol}/USDT: **${price:,.2f}**\n\n"
            f"[📈 Trade Now（立即交易）](https://kai.com/register?inviteCode=G6D7B9)\n"
            f"[😇 Ecological Partner（成为合伙人）](https://kai.com/kai-ambassador.html)\n"
            f"[👸 C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"价格查询错误: {e}")
        await update.message.reply_text("❌ 查询失败，请稍后重试")

# Serverless Webhook端点
@app.route('/', methods=['POST', 'GET'])
def webhook():
    """Telegram Webhook + 健康检查"""
    if request.method == 'GET':
        return jsonify({"status": "greta-price-bot ok"})
    
    try:
        # 解析Telegram更新
        json_data = request.get_json()
        update = Update.de_json(json_data, bot)
        
        # 创建临时应用处理更新
        app_temp = Application.builder().token(BOT_TOKEN).build()
        app_temp.add_handler(CommandHandler("start", start))
        app_temp.add_handler(CommandHandler("price", price))
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app_temp.process_update(update))
        loop.close()
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        logger.error(f"Webhook错误: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
