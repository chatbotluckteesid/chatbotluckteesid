import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =====================
# SETUP
# =====================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq_toko.json"

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# =====================
# UTIL
# =====================
def clean_text(text: str) -> str:
    return text.replace("*", "").replace("<", "").replace(">", "")

# =====================
# FAQ HANDLER
# =====================
def get_faq_answer(message: str):
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            faqs = json.load(f)

        msg = message.lower()
        for faq in faqs:
            for keyword in faq.get("keywords", []):
                if keyword in msg:
                    return faq.get("jawaban")
    except Exception as e:
        print("FAQ error:", e)

    return None

# =====================
# BOT CORE
# =====================
def get_bot_reply(user_message: str) -> str:
    user_message = user_message.strip().lower()

    if not user_message:
        return "Halo kak 😊 Ada yang bisa kami bantu?"

    # 1️⃣ FILTER KATA KASAR (FAQ PRIORITAS)
    faq = get_faq_answer(user_message)
    if faq:
        return faq

    # 2️⃣ SAPAAN
    greetings = ["halo", "hai", "hi", "p", "assalamualaikum"]
    if any(greet == user_message for greet in greetings):
        return (
            "Halo kak 👋😊\n"
            "Selamat datang di *Lucktees.id*\n\n"
            "Kami melayani:\n"
            "• Kaos polos CC 30s Grade A\n"
            "• Custom kaos & hoodie\n"
            "• Jersey printing\n"
            "• Long sleeve & workshirt\n\n"
            "Silakan tanya produk, harga, alamat, atau cara order ya kak."
        )

    # 3️⃣ SYSTEM PROMPT (AI-FIRST)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Kamu adalah chatbot resmi Lucktees.id (konveksi & sablon).

TUGAS UTAMA:
- Customer service
- Menjawab pertanyaan pelanggan
- Mengarahkan ke admin manusia jika diperlukan

GAYA BAHASA:
- Bahasa Indonesia santai (WhatsApp)
- Ramah, sopan, profesional
- Jawaban singkat & jelas
- Emoji secukupnya 😊

ATURAN JAWABAN:
1. Jika ditanya HARGA → arahkan ke admin
2. Jika ditanya PEMBAYARAN / BAYAR →
   "Pembayaran bisa via transfer, QRIS, atau tunai. Silakan hubungi admin Lucktees.id 👇
    +62882003848423"
3. Jika ditanya DESAIN →
   "Desain bisa custom. Silakan kirim desain ke admin Lucktees.id 👇
    62882003848423"
4. Jika ingin ORDER →
   Jelaskan alur pemesanan:
   - Tentukan produk
   - Tentukan jumlah & ukuran
   - Kirim desain (jika ada)
   - Konfirmasi ke admin
5. Jika tidak yakin menjawab → arahkan ke admin

LARANGAN:
- Jangan mengarang harga
- Jangan bahas politik, agama, atau topik sensitif
- Jangan keluar dari konteks usaha
"""
        ),
        ("human", "{input}")
    ])

    chain = prompt | llm
    result = chain.invoke({"input": user_message})

    return clean_text(result.content)

# =====================
# WRAPPER
# =====================
def get_response(message: str, user_id: str | None = None) -> str:
    return get_bot_reply(message)