# CARA MEMBUAT TELEGRAM BOT OTOMATIS

1. BUAT BOT DI @BOTFATHER
   - Buka Telegram, cari @BotFather
   - Ketik /newbot
   - Ikuti instruksi sampai selesai
   - Salin API Key yang diberikan (Contoh: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)

2. INSTAL SOFTWARE PENDUKUNG (Untuk Termux/Android)
   Jalankan ini di Termux:
   ```
   pkg update && pkg upgrade
   pkg install python
   pkg install python-pip
   pip install python-telegram-bot requests
   ```

3. DOWNLOAD KODE BOT
   ```
   git clone https://github.com/TarnaWijaya/TarzBot-Telegram.git
   cd TarzBot-Telegram
   ```

4. EDIT BOT
   - Buka file `bot.py` dengan text editor
   - Cari bagian API KEY (biasanya tertulis "YOUR_API_KEY")
   - Ganti dengan API Key dari @BotFather
   - Simpan perubahan

5. JALANKAN BOT
   ```
   python bot.py
   ```

# PENTING!
- Pastikan API Key rahasia tidak dibagikan ke siapapun
- Bot akan berhenti saat Termux ditutup
- Untuk 24/7 aktif, gunakan server/VPS
```

Contoh edit API Key:
```python
# Sebelum
API_KEY = 'MASUKKAN_API_KEY_DISINI'

# Sesudah
API_KEY = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
```

Jika ada error:
1. Cek apakah semua package sudah terinstall
2. Pastikan tidak ada typo di API Key
3. Restart Termux dan ulangi dari awal

Untuk pertanyaan lebih lanjut bisa hubungi [Mas Tarna](https://t.me/TarnaWijaya) 🤖
