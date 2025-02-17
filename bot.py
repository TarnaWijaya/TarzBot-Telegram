import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Konfigurasi
GEMINI_API_KEY = "AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30" # ganti dengan api gemininya 
BOT_TOKEN = "7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ" # ganti dengan api bot dari @BotFather
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo! Saya Tarna(BOT), asisten kecerdasan buatan yang dibuat oleh @TarnaWijaya Layanan API Gemini. Untuk informasi lengkap tentang model dan produk kami, silakan lihat dokumentasi resmi kami.🙏🗿')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE): help_text = """
💫 **Tarna(BOT) Telegram Bot** 💫
📱 **Developer**: [Tarna Wijaya](https://t.me/TarnaWijaya)

✨ **Perintah yang Tersedia**:
/start - Mulai bot
/help - Tampilkan pesan bantuan
/ask [pertanyaan] - Ajukan pertanyaan ke AI

🚀 **Fitur**:
- Diskusi grup dengan command `/ask`
- Pencarian informasi real-time
- Kemampuan analisis data
- Percakapan kontekstual

🌐 **Organisasi**:
- Telegram: [Tarna Wijaya Grup](https://t.me/TarnaWijaya_grup)
- WhatsApp: [Papah Jerman 😃](https://chat.whatsapp.com/Gomu4BhzluT3gaXRHmNs4n)
"""

    await update.message.reply_text(help_text, parse_mode="Markdown")


def generate_content(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts":[{"text": prompt}]
        }]
    }
    
    response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Maaf, terjadi kesalahan dalam memproses respons."
    else:
        return f"Error: {response.status_code} - {response.text}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    
    # Handle group messages
    if message_type in ['group', 'supergroup']:
        if text.startswith('/ask'):
            query = text[5:].strip()
            if query:
                response = generate_content(query)
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Silakan tulis pertanyaan setelah /ask, contoh: /ask {pesan}")
    # Handle private messages
    else:
        response = generate_content(text)
        await update.message.reply_text(response)

if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('ask', handle_message))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
