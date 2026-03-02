import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import aiohttp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("请设置 .env 文件中的 BOT_TOKEN")

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
            
             f"[😇 Ecological Partner（成为合伙人） ](https://kai.com/kai-ambassador.html)\n"

              f"[👸 C2C Merchant（成为C2C商家）](https://kai.com/register?inviteCode=G6D7B9)\n",   # ← 可点击链接！
            
            parse_mode = "Markdown"
        )
    except Exception as e:
        logger.error(f"价格查询错误: {e}")
        await update.message.reply_text("❌ 查询失败，请稍后重试")

def main():
    """主函数"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    
    logger.info("🤖 Bot 启动中...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
