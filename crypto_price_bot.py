
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توکن دریافتی از BotFather
BOT_TOKEN = "7914986131:AAFstwdFk-OAy3EfT-PKUlUPVchF5-vy3aM"

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# نرخ تبدیل دلار به تومان (از api می‌گیریم یا دستی می‌زنیم، اینجا فعلاً ثابت)
USD_TO_TOMAN = 58000  # نرخ بازار آزاد به‌روز (می‌شه با API همزمان کرد)


# گرفتن قیمت ارز دیجیتال از CoinGecko
def get_crypto_price(symbol: str):
    symbol = symbol.lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if symbol in data:
            usd_price = data[symbol]['usd']
            toman_price = usd_price * USD_TO_TOMAN
            return usd_price, toman_price
    return None, None


# پیدا کردن ID ارز از CoinGecko بر اساس نماد یا اسم
def find_coin_id(query: str):
    query = query.lower()
    coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
    for coin in coins:
        if coin["id"] == query or coin["symbol"] == query or coin["name"].lower() == query:
            return coin["id"]
    return None


# وقتی کاربر پیام بفرسته
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    coin_id = find_coin_id(query)
    if coin_id:
        usd_price, toman_price = get_crypto_price(coin_id)
        if usd_price:
            response = (
                f"قیمت {query.upper()}:
"
                f"دلار: ${usd_price:,.4f}
"
                f"تومان: {toman_price:,.0f} تومان

"
                f"عضو کانال ما شو: @BitmoneyAirdrop"
            )
        else:
            response = "نتونستم قیمت رو پیدا کنم، دوباره امتحان کن."
    else:
        response = "رمزارز مورد نظر پیدا نشد. لطفاً نماد یا اسم دقیق وارد کن."

    await update.message.reply_text(response)


# پیام استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! اسم یا نماد هر رمزارزی رو بفرست تا قیمت لحظه‌ایشو بهت بگم (دلار و تومان).
"
        "مثلاً بنویس: BTC یا SHIBA

"
        "عضو کانال ایردراپ شو: @BitmoneyAirdrop"
    )


# اجرای برنامه
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
