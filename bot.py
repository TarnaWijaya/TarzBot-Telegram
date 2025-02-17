import logging
import google.generativeai as genai
from telegram import Update, InputFile
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

# Fungsi untuk memulai bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya adalah asisten AI yang siap membantu Anda. "
        "Untuk memulai, gunakan /help untuk informasi lebih lanjut atau tanyakan sesuatu menggunakan /ask."
    )

# Fungsi untuk memberikan informasi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Grup kami ada di:\n\n"
        "Telegram: https://t.me/TarnaWijaya_grup\n"
        "WhatsApp: https://chat.whatsapp.com/Gomu4BhzluT3gaXRHmNs4n\n"
        "Gunakan /ask diikuti pertanyaan untuk bertanya di grup."
    )

# Fungsi untuk menangani perintah /ask
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Cek apakah digunakan di grup
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("❌ Perintah /ask hanya bisa digunakan di grup.")
        return

    # Cek apakah ada pertanyaan
    if not context.args:
        await update.message.reply_text("⚠️ Format: /ask [pertanyaan]")
        return

    question = " ".join(context.args)
    
    # Memproses pertanyaan dengan Gemini
    try:
        response = gemini_model.generate_content(question)
        await update.message.reply_text(f"🔍 Pertanyaan: {question}\n\n💡 Jawaban: {response.text}")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text("❌ Gagal memproses pertanyaan, coba lagi nanti.")

# Fungsi untuk menangani pesan lainnya di grup
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type

    # Hanya balas di grup atau supergroup dengan format yang benar
    if chat_type in ['group', 'supergroup']:
        if not update.message.text.startswith('/ask'):
            await update.message.delete()
        return

    # Balasan untuk pesan non-grup
    await update.message.reply_text(
        "🤖 Saya hanya bisa menjawab pertanyaan di grup menggunakan perintah /ask. "
        "Gabung grup kami di /help."
    )

# Fungsi untuk memproses gambar
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type not in ['group', 'supergroup']:
        return

    file = update.message.photo[-1].file_id  # Ambil foto dengan resolusi tertinggi
    photo = await context.bot.get_file(file)
    
    # Jika perlu, bisa diproses lebih lanjut
    await update.message.reply_text("📸 Foto berhasil diterima. Saya sedang memprosesnya...")

    # Contoh balasan bisa dilakukan di sini setelah memproses foto
    await update.message.reply_text("Gambar sudah diterima, coba gunakan perintah /ask untuk bertanya.")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_API).build()

    # Handler command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))

    # Handler pesan biasa
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handler gambar
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
