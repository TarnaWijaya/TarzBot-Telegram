import os
import logging
import aiohttp
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

# Konfigurasi API (sebaiknya simpan token/API key di environment variables atau GitHub Secrets)
TELEGRAM_BOT_API = os.environ.get("TELEGRAM_BOT_API", "7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30")

async def generate_answer(query: str) -> str:
    """
    Memanggil endpoint Gemini 1.5 Flash untuk menghasilkan jawaban.
    Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": query}]
            }
        ]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()
                logger.info(f"Gemini API response: {data}")
                # Asumsi format respons: {"candidates": [{"text": "jawaban"}], ...}
                answer = data.get("candidates", [{}])[0].get("text", "")
                return answer
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda."

async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question: str) -> None:
    """Memproses pertanyaan dengan memanggil Gemini API dan mengirim jawaban."""
    answer = await generate_answer(question)
    await update.message.reply_text(f"🔍 Pertanyaan: {question}\n\n💡 Jawaban: {answer}")

# Perintah /start (tersedia di grup dan chat pribadi)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya adalah asisten AI yang siap membantu Anda.\n"
        "Di grup, gunakan perintah /ask [pertanyaan] untuk bertanya.\n"
        "Di chat pribadi, Anda bisa langsung mengirimkan pertanyaan tanpa perintah.\n"
        "Gunakan /help untuk informasi lebih lanjut."
    )

# Perintah /help (tersedia di grup dan chat pribadi)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Informasi Grup:\n"
        "Telegram: https://t.me/TarnaWijaya_grup\n"
        "WhatsApp: https://chat.whatsapp.com/Gomu4BhzluT3gaXRHmNs4n\n\n"
        "Di grup, gunakan perintah /ask [pertanyaan] untuk bertanya.\n"
        "Di chat pribadi, cukup kirimkan pertanyaan Anda secara langsung."
    )

# Perintah /ask (untuk grup dan chat pribadi)
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ Format: /ask [pertanyaan]")
        return
    question = " ".join(context.args)
    await process_question(update, context, question)

# Handler untuk pesan di chat pribadi (pesan teks tanpa perintah)
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text and not update.message.text.startswith('/'):
        question = update.message.text
        await process_question(update, context, question)

# Handler untuk pesan di grup (hapus pesan yang bukan perintah /ask, /start, atau /help)
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text and not (update.message.text.startswith('/ask') or
                                    update.message.text.startswith('/start') or
                                    update.message.text.startswith('/help')):
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

# Handler untuk foto (di grup)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type in ['group', 'supergroup']:
        file_id = update.message.photo[-1].file_id  # Ambil foto dengan resolusi tertinggi
        photo = await context.bot.get_file(file_id)
        await update.message.reply_text("📸 Foto berhasil diterima. Saya sedang memprosesnya...")
        await update.message.reply_text("Gambar sudah diterima, silakan tanyakan pertanyaan menggunakan /ask.")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_API).build()

    # Handler perintah (tersedia di grup dan chat pribadi)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))

    # Handler pesan untuk chat pribadi: pesan teks (selain perintah) dianggap sebagai pertanyaan
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, handle_private_message))

    # Handler pesan untuk grup: hapus pesan yang tidak menggunakan perintah /ask, /start, atau /help
    application.add_handler(MessageHandler((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & filters.TEXT & ~filters.COMMAND, handle_group_message))

    # Handler untuk foto di grup
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
