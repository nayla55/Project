import cv2
import numpy as np
from pyzbar import pyzbar
from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ChosenInlineResultHandler
import os

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

def read_barcode(image):
    barcodes = pyzbar.decode(image)
    return barcodes

def detect_objects(image):
    barcodes = read_barcode(image)
    if barcodes:
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            barcode_info = barcode.data.decode('utf-8')
            cv2.putText(image, barcode_info, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

def main():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detected_frame = detect_objects(frame)
        cv2.imshow('Video', detected_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def handle(update, context):
    img = open('last_frame.jpg', 'rb')
    img = InputMediaPhoto(img)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=img)

def handle_text(update, context):
    text = update.message.text
    img = open('last_frame.jpg', 'rb')
    img = InputMediaPhoto(img, caption=text)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=img)

if __name__ == '__main__':
    last_frame = None

    def video_frame(update, context):
        nonlocal last_frame
        current_frame = np.frombuffer(update.message.video.as_buffer(), dtype=np.uint8)
        current_frame = cv2.imdecode(current_frame, 1)
        current_frame = detect_objects(current_frame)
        _, jpeg = cv2.imencode('.jpg', current_frame)
        last_frame = jpeg.tobytes()

    def handle_video(update, context):
        nonlocal last_frame
        img = last_frame
        img = InputMediaPhoto(img)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=img)

    def error(update, context):
        print(f'Update {update} caused error {context.error}')

    def main():
        updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", handle))
        dp.add_handler(MessageHandler(Filters.text, handle_text))
        dp.add_handler(MessageHandler(Filters.video, video_frame))
        dp.add_handler(CommandHandler("show", handle_video))
        dp.add_error_handler(error)

        updater.start_polling()

        updater.idle()

    main()