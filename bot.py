import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Mengambil API_ID, API_HASH, BOT_TOKEN, dan PHONE_NUMBER dari environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# Setup logging untuk error/debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Client Telethon dengan sesi pengguna
client = TelegramClient('user_session', API_ID, API_HASH)

# Fungsi untuk login ke akun pengguna
async def user_login():
      # Pastikan client terhubung
      await client.connect()

      if not await client.is_user_authorized():
            try:
                await client.sign_in(PHONE_NUMBER)
            except SessionPasswordNeededError:
                password = input("Masukkan password 2FA Anda: ")
                await client.sign_in(password=password)
        print("Login berhasil!")
    else:
        print("Sudah login menggunakan sesi yang tersimpan.")

# Fungsi untuk auto forward pesan terbaru menggunakan user account
async def auto_forward(update: Update, context: CallbackContext):
    try:
        # Mendapatkan ID channel asal dan tujuan dari argument
        args = context.args
        if len(args) < 2:
            update.message.reply_text('Usage: /forward <source_channel_id> <destination_chat_id>')
            return
        
        source_channel = int(args[0])
        destination_chat = int(args[1])

        # Mengambil pesan terakhir dari channel asal
        async with client:
            latest_message = await client.get_messages(source_channel, limit=1)
            if latest_message:
                await client.forward_messages(destination_chat, latest_message)

        update.message.reply_text('Message forwarded successfully!')

    except Exception as e:
        update.message.reply_text(f'Error: {e}')

# Fungsi untuk menyalin pesan sebelumnya berdasarkan message ID menggunakan user account
async def clone_message(update: Update, context: CallbackContext):
    try:
        # Mendapatkan ID channel dan ID pesan dari argument
        args = context.args
        if len(args) < 3:
            update.message.reply_text('Usage: /clone <source_channel_id> <message_id> <destination_chat_id>')
            return
        
        source_channel = int(args[0])
        message_id = int(args[1])
        destination_chat = int(args[2])

        # Menyalin pesan berdasarkan ID
        async with client:
            message = await client.get_messages(source_channel, ids=message_id)
            if message:
                await client.send_message(destination_chat, message.text, file=message.media)

        update.message.reply_text('Message cloned successfully!')

    except Exception as e:
        update.message.reply_text(f'Error: {e}')

# Fungsi utama untuk menjalankan bot
def main():
    # Membuat Updater dan bot
    updater = Updater(BOT_TOKEN, use_context=True)

    # Menambahkan command handler untuk auto forward dan clone
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('forward', auto_forward))
    dp.add_handler(CommandHandler('clone', clone_message))

    # Login ke akun pengguna
    client.loop.run_until_complete(user_login())

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()