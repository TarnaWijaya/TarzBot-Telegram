import logging
import os
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import requests
from langdetect import detect, LangDetectException
from collections import defaultdict

# Konfigurasi
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",
"AIzaSyC0Cjd5U_kIM9tvqxfjjvQ_MlhabjtxA30")
BOT_TOKEN = os.getenv("BOT_TOKEN",
"7648169616:AAG-xCt_l_BHkhGcJ9bTtQpeCrz7tv7t0cQ")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Konfigurasi memori percakapan
MAX_HISTORY_LENGTH = 6  # Menyimpan 3 pasang tanya-jawab terakhir
conversation_history = defaultdict(list)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /start"""
    try:
        welcome_msg = (
            "🌟 **Selamat datang di TarnaBot!** 🌟\n\n"
            "Saya asisten AI canggih dengan teknologi Gemini. Bagaimana saya bisa membantu Anda hari ini?\n\n"
            "Beberapa contoh yang bisa Anda coba:\n"
            "- Jelaskan teori relativitas secara sederhana\n"
            "- Buatkan kode Python untuk sorting array\n"
            "- Terjemahkan kalimat ini ke bahasa Inggris: 'Hari ini cuaca sangat cerah'\n\n"
            "Ketik /help untuk bantuan lebih lanjut"
        )
        await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in /start: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk command /help"""
    help_text = """
    🧠 **TarnaBot - Pusat Bantuan** 🧠

    **Fitur Utama:**
    - 💬 Percakapan kontekstual
    - 🌍 Dukungan multibahasa
    - 📚 Pengetahuan umum & spesialis
    - 💻 Bantuan pemrograman
    - ✍️ Koreksi tata bahasa

    **Perintah:**
    `/start` - Memulai percakapan
    `/help` - Menampilkan menu bantuan
    `/ask [pertanyaan]` - Ajukan pertanyaan langsung

    **Format Respons:**
    ```markdown
    # Judul [🔍]
    - Poin penting 1
    - Poin penting 2
    > Catatan penting
    ```
    
    📌 Tips: Gunakan reply ke pesan bot untuk melanjutkan percakapan
    """
    try:
        await update.message.reply_text(
            help_text,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"Error in /help: {str(e)}")

async def generate_ai_response(prompt: str, chat_id: int) -> Optional[str]:
    """Generate response dari Gemini API dengan gaya Google Gemini"""
    try:
        history = conversation_history.get(chat_id, [])[-MAX_HISTORY_LENGTH:]
        
        system_prompt = """Anda adalah asisten AI canggih bernama TarnaBot yang menggunakan teknologi Gemini. 
        Format respons Anda harus mengikuti pola berikut:

        1. **Analisis Pertanyaan**: Jelaskan konteks pertanyaan secara singkat
        2. **Inti Jawaban**: Berikan jawaban utama dengan struktur jelas
        3. **Poin Tambahan** (jika perlu):
            - Gunakan bullet points
            - Sertakan contoh kode dalam ``` jika relevan
        4. **Kesimpulan**: Ringkas jawaban dalam 1 kalimat
        5. **Catatan**: Sertakan informasi tambahan yang berguna

        Aturan:
        - Gunakan emoji relevan untuk visualisasi
        - Format dengan Markdown
        - Pertahankan bahasa pengguna
        - Maksimal 500 karakter
        - Sertakan credit kecil di akhir: `~ TarnaBot 🤖`
        """

        payload = {
            "contents": [
                *[{"parts": [{"text": msg}]} for msg in history],
                {"parts": [{"text": prompt}]}
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            }
        }

        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()

        response_data = response.json()
        if not response_data.get("candidates"):
            raise ValueError("Empty response from API")

        result = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Formatting cleanup
        result = result.replace("** ", "**").replace(" **", "**")
        result += "\n\n---\n_Powered by Gemini AI_ 🌐"
        
        # Update history
        conversation_history[chat_id].extend([prompt, result])
        if len(conversation_history[chat_id]) > MAX_HISTORY_LENGTH:
            conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY_LENGTH:]

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {str(e)}")
        return "⚠️ Gangguan jaringan. Silakan coba beberapa saat lagi..."
    except (KeyError, IndexError) as e:
        logger.error(f"Parsing Error: {str(e)}")
        return "⚠️ Terjadi kesalahan dalam memproses respons. Silakan coba pertanyaan lain."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk semua pesan"""
    try:
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat.id
        text = message.text.strip()
        
        if message.chat.type in ["group", "supergroup"]:
            if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
                query = text
            elif text.startswith("/ask"):
                query = text[4:].strip()
            else:
                return
        else:
            query = text

        # Typing indicator
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        response = await generate_ai_response(query, chat_id)
        
        if response:
            await message.reply_text(
                response,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            await message.reply_text("🔄 Sedang mengalami kendala teknis. Silakan coba lagi dalam beberapa menit.")

    except Exception as e:
        logger.error(f"Global error: {str(e)}")
        try:
            await message.reply_text("⚠️ Terjadi kesalahan sistem. Tim kami telah diberitahu.")
        except:
            pass

def main() -> None:
    """Jalankan bot"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("ask", handle_message))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

        logger.info("🔌 Bot starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.critical(f"❌ Failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main()