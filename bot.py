import os
import re
import sqlite3
import logging
import pytesseract
from PIL import Image
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def extract_amount(text):
    patterns = [
        r"(R\$ ?[\d\.,]+)",
        r"(\$ ?[\d\.,]+)",
        r"(￥[\d\.,]+)",
        r"(€[\d\.,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def save_transaction(user_id, amount, currency, raw_text):
    with sqlite3.connect("transactions.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS records 
                     (user_id TEXT, amount TEXT, currency TEXT, raw_text TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        c.execute("INSERT INTO records (user_id, amount, currency, raw_text) VALUES (?, ?, ?, ?)",
                  (user_id, amount, currency, raw_text))
        conn.commit()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = await file.download_as_bytearray()

    image = Image.open(BytesIO(img_bytes))
    text = pytesseract.image_to_string(image)

    amount = extract_amount(text)
    if amount:
        await update.message.reply_text(f"识别成功 ✅\n金额：{amount}")
        save_transaction(update.effective_user.id, amount, "auto", text)
    else:
        await update.message.reply_text("⚠️ 未识别到金额，请检查图片")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("你好！请发送支付截图，我会帮你识别金额并入账。")

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ 请设置 BOT_TOKEN 环境变量")
        exit(1)
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.run_polling()