import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Konfigurasi logging untuk memudahkan debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# API token Bot Telegram dan API key Gemini (sesuaikan dengan kebutuhan dan simpan secara aman)
TELEGRAM_BOT_API = "7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ"
GEMINI_API_KEY = "AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fungsi handler untuk perintah /start.
    Menampilkan pesan selamat datang beserta informasi pembuat bot.
    """
    welcome_message = (
        "Selamat datang!\n"
        "Saya adalah bot Telegram yang dibuat oleh TarnaWijaya.\n\n"
        "Untuk mulai mengobrol, cukup kirim pesan ke saya.\n"
        "Gunakan perintah /help untuk melihat info grup."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fungsi handler untuk perintah /help.
    Mengirimkan link grup Telegram dan WhatsApp.
    """
    help_message = (
        "Berikut adalah link grup:\n\n"
        "Telegram: https://t.me/TarnaWijaya_grup\n"
        "WhatsApp: https://chat.whatsapp.com/Gomu4BhzluT3gaXRHmNs4n"
    )
    await update.message.reply_text(help_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk pesan teks biasa.
    Jika pesan berkaitan dengan pembuat, bot akan menjawab sesuai perintah.
    Jika tidak, bot akan melakukan echo sederhana (di sini bisa dikembangkan dengan integrasi Gemini API).
    """
    user_text = update.message.text
    lower_text = user_text.lower()

    # Cek apakah pesan berkaitan dengan pertanyaan tentang pembuat/dev
    if any(keyword in lower_text for keyword in ["siapa pembuat", "siapa yang membuat", "dev", "pembuat", "tarna"]):
        reply = "TarnaWijaya membuat saya."
    else:
        # Placeholder untuk integrasi Gemini API atau logika AI lainnya
        # Contoh: Anda bisa memanggil fungsi yang mengirim request ke Gemini API di sini.
        # response = call_gemini_api(user_text, GEMINI_API_KEY)
        # reply = response.get("reply", "Maaf, terjadi kesalahan.")
        
        # Untuk contoh saat ini, kita gunakan respon echo sederhana
        reply = f"Kamu berkata: {user_text}"

    await update.message.reply_text(reply)

def main() -> None:
    """
    Fungsi utama untuk menjalankan bot.
    Mengatur command handler dan message handler, kemudian menjalankan bot dengan polling.
    """
    # Buat instance aplikasi dengan token bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_API).build()

    # Daftarkan handler untuk perintah /start dan /help
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Daftarkan handler untuk pesan teks non-perintah
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Mulai polling (untuk deployment real-time)
    application.run_polling()

if __name__ == "__main__":
    main()
