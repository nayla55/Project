import cv2
import numpy as np
from telebot import TeleBot

API_TOKEN = 'YOUR_API_TOKEN'
bot = TeleBot(API_TOKEN)

cap = cv2.VideoCapture(0)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am a Webcam Controller bot. You can control me by sending the following commands:\n/start: to start the bot\n/stop: to stop the bot\n/photo: to take a photo")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global keep_streaming
    keep_streaming = False
    bot.reply_to(message, 'The bot is stopped.')

@bot.message_handler(commands=['photo'])
def take_photo(message):
    _, frame = cap.read()
    cv2.imwrite('frame.jpg', frame)
    bot.send_photo(message.chat.id, open('frame.jpg', 'rb'))

def stream():
    while keep_streaming:
        _, frame = cap.read()
        bot.send_photo(message.chat.id, frame)
        if cv2.waitKey(1) == ord('q'):
            break

keep_streaming = True

bot.polling()

stream()

cap.release()
cv2.destroyAllWindows()