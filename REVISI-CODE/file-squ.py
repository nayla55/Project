import cv2
import onnxruntime
from PIL import Image
import numpy as np
from io import BytesIO
import telegram

def yolo_detection(onnx_session, input_image, conf_thresh, nms_thresh):
    """Apply YOLOv4 object detection to the input image.
    """
    input_image = input_image.resize((416, 416), Image.ANTIALIAS)
    img_mean = np.array([0, 0, 0])
    img_std = np.array([255, 255, 255])

    # Normalize and convert image to tensor
    input_image = (np.array(input_image) - img_mean) / img_std
    input_image = np.transpose(input_image, (2, 0, 1))
    input_image = np.expand_dims(input_image, axis=0)
    input_image = input_image.astype(np.float32)

    # Perform inference
    input_name = onnx_session.get_inputs()[0].name
    output_name = onnx_session.get_outputs()[0].name
    outputs = onnx_session.run([output_name], {input_name: input_image})

    # Extract bounding boxes, scores, and classes
    boxes, scores, classes = outputs[0][0], outputs[0][1], outputs[0][2]

    # Apply non-maximum suppression to filter out overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), conf_thresh, nms_thresh)

    return boxes, scores, classes, indices

def main():
    # Initialize Telegram bot and OpenCV webcam
    bot = telegram.Bot(token='<YOUR-BOT-TOKEN>')
    cap = cv2.VideoCapture(0)

    # Load ONNX model and create inference session
    onnx_session = onnxruntime.InferenceSession('yolov4.onnx')

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Convert frame to PIL Image
        img = Image.fromarray(frame)

        # Perform object detection
        boxes, scores, classes, indices = yolo_detection(onnx_session, img, conf_thresh=0.5, nms_thresh=0.4)

        # Draw bounding boxes on the frame
        for i in indices:
            box = boxes[i]
            x, y, w, h = int(box[0]), int(box[1]), int(box[2] - box[0]), int(box[3] - box[1])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Real-Time Food Detection', frame)

        # Exit the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close the output window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()