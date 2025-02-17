import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
from langdetect import detect
from collections import defaultdict

# Konfigurasi
GEMINI_API_KEY = "AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30"
BOT_TOKEN = "7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Penyimpanan memori percakapan
conversation_history = defaultdict(list)  # Diubah dari conversation_history ke conversasi_history

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo! Saya Tarna(BOT). Ketik /help untuk bantuan')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    💫 **Tarna(BOT) Telegram Bot** 💫
    
    Dibuat dengan ❤️ oleh: [TarnaWijaya](https://t.me/TarnaWijaya)
    Grup Resmi: [@TarnaWijaya_grup](https://t.me/TarnaWijaya_grup)
    
    /start - Mulai bot
    /help - Tampilkan pesan bantuan
    /ask [pertanyaan] - Ajukan pertanyaan ke AI
    
    Fitur:
    - Respons emosional dan empati
    - Bisa di-reply di grup
    - Memori percakapan terbatas
    - Deteksi bahasa otomatis
    """
    await update.message.reply_text(help_text, parse_mode='Markdown', disable_web_page_preview=True)

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'id'

def generate_emotional_response(prompt, chat_id):
    # Ambil riwayat percakapan
    history = conversasi_history[chat_id][-4:]  # Diperbaiki penamaan variabel
    
    # Deteksi bahasa
    lang = detect_language(prompt)
    
    system_instruction = {
        "parts": [{
            "text": f"""Anda adalah asisten AI yang dibuat oleh TarnaWijaya. Analisis emosi pesan pengguna dan:
            1. Respon dengan bahasa yang sama dengan pertanyaan
            2. Tunjukkan pemahaman emosional
            3. Berikan respons yang mendukung
            4. Jika netral, berikan jawaban faktual
            5. SELALU sertakan credit developer di akhir jawaban
            Format respons: [EMOJI_RELEVAN] Respons emosional\n\n~ TarnaWijaya"""
        }]
    }

    headers = {'Content-Type': 'application/json'}
    data = {
        "systemInstruction": system_instruction,
        "contents": [
            *[{"parts": [{"text": msg}]} for msg in history],
            {"parts": [{"text": prompt}]}
        ]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()['candidates'][0]['content']['parts'][0]['text']
            conversasi_history[chat_id].extend([prompt, result])
            return result
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return "Maaf, sedang ada gangguan teknis. Silakan coba lagi nanti."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id
    text = message.text
    
    if not text:
        return
    
    # Handle group messages
    if message.chat.type in ['group', 'supergroup']:
        is_reply_to_bot = (
            message.reply_to_message and 
            message.reply_to_message.from_user.id == context.bot.id
        )
        
        if is_reply_to_bot or text.startswith('/ask'):
            query = text[4:].strip() if text.startswith('/ask') else text.strip()
            if query:
                try:
                    response = generate_emotional_response(query, chat_id)
                    await message.reply_text(response)
                except Exception as e:
                    logging.error(f"Error: {str(e)}")
                    await message.reply_text("Terjadi kesalahan saat memproses permintaan")
            else:
                await message.reply_text("Silakan tulis pertanyaan setelah /ask")
        return
    
    # Handle private messages
    try:
        response = generate_emotional_response(text, chat_id)
        await message.reply_text(response)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await message.reply_text("Terjadi kesalahan internal")

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('ask', handle_message))
    
    # Message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE,
        handle_message
    ))
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)