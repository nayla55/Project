import cv2
import imutils
import numpy as np
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Token bot telegram anda
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Untuk menghindari spam chat, gunakan variabel berikut untuk menyimpan waktu saat proses deteksi terakhir berlangsung
LAST_UPDATE = None
TIME_TO_WAIT = 60 # Dalam detik, sehingga setiap 60 detik akan mengirimkan pesan hanya sekali

# Proses deteksi objek
def detect_objects(image):
    global LAST_UPDATE

    # Memanggil fungsi yang telah didefinisikan untuk melakukan proses deteksi objek
    # dan mengirimkan hasil deteksi ke telegram
    send_to_telegram(image)

    # Menyimpan waktu saat proses deteksi terakhir berlangsung
    LAST_UPDATE = time.time()


# Mengirimkan hasil deteksi ke telegram
def send_to_telegram(image):
    global updater

    # Memasukkan foto yang telah diberikan kedalam sebuah objek file yang akan kita kirim ke telegram
    image = cv2.imencode('.jpg', image)[1]
    image = open('image.jpg', 'wb')
    image.write(image.read())

    # Mengirimkan foto yang telah diberikan ke telegram
    # Note: Gunakan ID chat telegram anda
    updater.bot.send_photo(chat_id='YOUR_TELEGRAM_CHAT_ID', photo=open('image.jpg', 'rb'))


# Proses mengunduh foto dari telegram
def download_photo(update: Update, context: CallbackContext):
    global updater

    # Mengambil foto dari telegram dan menyimpannya dalam folder local anda
    # Note: Gunakan ID chat telegram anda
    file_id = update.message.photo[-1].file_id
    file = updater.bot.get_file(file_id)
    file.download('image.jpg')

    # Memanggil fungsi yang telah didefinisikan untuk melakukan proses deteksi objek
    image = cv2.imread('image.jpg')
    detect_objects(image)


# Menjalankan bot telegram
def run_bot():
    global updater

    # Memulai proses pencarian update yang datang dari telegram
    updater = Updater(TOKEN)

    # Menjalankan fungsi yang telah didefinisikan untuk melakukan proses deteksi objek ketika ada update yang datang
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, download_photo))

    # Menjalankan proses pencarian update yang datang dari telegram
    updater.start_polling()

    # Memulai loop untuk mengatur penghentian proses pencarian update yang datang dari telegram
    updater.idle()


if __name__ == '__main__':
    run_bot()