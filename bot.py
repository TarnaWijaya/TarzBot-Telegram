import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Konfigurasi logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Konfigurasi API
TELEGRAM_BOT_API = "7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ"
GEMINI_API_KEY = "AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Selamat datang! Saya adalah bot Telegram yang dibuat oleh TarnaWijaya.\n"
        "Gunakan /help untuk info grup dan /ask di grup untuk bertanya."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Link grup:\n\n"
        "Telegram: https://t.me/TarnaWijaya_grup\n"
        "WhatsApp: https://chat.whatsapp.com/Gomu4BhzluT3gaXRHmNs4n"
    )

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Cek jika digunakan di luar grup
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("❌ Perintah /ask hanya bisa digunakan di dalam grup!")
        return

    # Cek pertanyaan dari user
    if not context.args:
        await update.message.reply_text("⚠️ Format: /ask [pertanyaan_anda]")
        return

    # Proses pertanyaan dengan Gemini
    question = " ".join(context.args)
    try:
        response = gemini_model.generate_content(question)
        await update.message.reply_text(f"🔍 Pertanyaan: {question}\n\n💡 Jawaban:\n{response.text}")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text("❌ Gagal memproses pertanyaan, coba lagi nanti.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    
    if chat_type in ['group', 'supergroup']:
        await update.message.reply_text(
            "📝 Gunakan perintah /ask diikuti dengan pertanyaan Anda\n"
            "Contoh: /ask Bagaimana cara membuat website?"
        )
    else:
        await update.message.reply_text(
            "🤖 Saya hanya bisa menjawab pertanyaan di grup menggunakan perintah /ask\n"
            "Silakan gabung grup kami di /help"
        )

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_API).build()

    # Handler command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))

    # Handler pesan biasa
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
