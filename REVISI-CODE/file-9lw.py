import cv2
import torch
from torchvision import transforms
from yolov8 import YOLOv8, non_max_suppression
from PIL import Image
import requests
import os
import time

def get_webcam_feed():
    # Webcam feed
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam feed")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame

def prepare_image(frame):
    # Convert the image from BGR to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Transform the image for the model
    image = Image.fromarray(image)
    transform = transforms.Compose([transforms.Resize((640, 640)),
                                    transforms.ToTensor(),
                                    transforms.Normalize([0.485, 0.456, 0.406],
                                                         [0.229, 0.224, 0.225])])
    image = transform(image).unsqueeze(0)

    return image

def send_to_telegram(img_path):
    bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
    chat_id = 'YOUR_TELEGRAM_CHANNEL_ID'

    # Upload the image to Telegram
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    files = {'photo': open(img_path, 'rb')}
    params = {'chat_id': chat_id}
    response = requests.post(url, files=files, params=params)

    # Delete the local image after sending it to Telegram
    os.remove(img_path)

    return response.json()

if __name__ == '__main__':
    model = YOLOv8(1)
    model.load_state_dict(torch.load('yolov8.pth', map_location='cpu'))
    model.eval()

    # Dummy prediction for first frame
    _, _, h, w = model(torch.zeros(1, 3, 640, 640)).shape

    with torch.no_grad():
        for frame in get_webcam_feed():
            image = prepare_image(frame)
            output = model(image)
            predictions = non_max_suppression(output, 80, h, w)

            # Check if predictions are valid and send to Telegram
            if predictions[0] is not None:
                img_path = 'detection.jpg'
                cv2.imwrite(img_path, frame)
                send_to_telegram(img_path)

            # Show the image in the window
            cv2.imshow('Real-time object detection', frame)

            # Stop the program if the user presses the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

   