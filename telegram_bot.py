# =============================
# IMPORT
# =============================
import os
import json
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from core import get_bot_reply


# =============================
# LOAD ENV
# =============================
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN belum diset")
    exit()

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY belum diset")
    exit()

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# =============================
# LOGGING
# =============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


# =============================
# INISIALISASI GROQ AI
# =============================
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3
)


# =============================
# MEMORY PER CHAT
# =============================
conversation_history = {}  # {chat_id: [{"user": "", "bot": ""}]}


# =============================
# COMMAND /START
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = []

    await update.message.reply_text(
        "Halo 👋 Saya Asisten Lucktees.id 👕\n"
        "Silakan tanya soal kaos, sablon, harga, atau cara order 😊"
    )


# =============================
# HANDLE PESAN USER
# =============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    # 1️⃣ Jawaban dari core.py
    reply = get_bot_reply(user_text)

    # 2️⃣ Jika core tidak paham → Groq AI
    if "belum memahami" in reply.lower() or "tidak tahu" in reply.lower():
        try:
            history_text = ""
            for h in conversation_history[chat_id][-3:]:
                history_text += f"User: {h['user']}\nBot: {h['bot']}\n"

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
Kamu adalah admin Lucktees.id.
Tugasmu:
1. Tangkap jenis kaos, jumlah, ukuran, alamat, dan nomor WhatsApp jika user ingin order.
2. Jika data belum lengkap, tanyakan dengan singkat dan ramah.
3. Jika user bertanya tentang harga, sablon, bahan, atau estimasi produksi, jawab sesuai konteks.
4. Gunakan bahasa chat yang santai, ramah, dan jelas.
5. Jangan mengulang pertanyaan jika user sudah menyebut detail order.
6. Fokus hanya pada produk dan layanan Lucktees.id.
"""
                ),
                ("human", "{history}\nUser: {input}")
            ])

            chain = prompt | llm
            ai_response = chain.invoke({
                "input": user_text,
                "history": history_text
            })

            reply = ai_response.content

        except Exception as e:
            logging.error("Groq AI Error: %s", e)
            reply = "Maaf kak 🙏 sistem sedang sibuk. Bisa ditanyakan lagi ya 😊"

    conversation_history[chat_id].append({
        "user": user_text,
        "bot": reply
    })

    await update.message.reply_text(reply)


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    print("🤖 Bot Lucktees.id sedang dijalankan...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
