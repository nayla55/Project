import cv2
import numpy as np

def classify_image(img, labels):
    """ Returns the index of the detected object in labels. """
    net = cv2.dnn.readNetFromONNX('training.onnx')

    # Create a 4D blob from a frame.
    blob = cv2.dnn.blobFromImage(img, 0.00392, (320, 320), (0, 0, 0), True, crop=False)

    # Run a model.
    net.setInput(blob)
    out = net.forward()

    # Find the most probable classes for the detected objects.
    class_ids = []
    confidences = []
    for out_idx in range(out.shape[0]):
        for det_idx in range(out.shape[2]):
            confidence = out[out_idx, 0, det_idx, 2]
            if confidence > .5: # .5 is a threshold
                class_id = int(out[out_idx, 0, det_idx, 1])
                cx = out[out_idx, 0, det_idx, 3] * img.shape[1]
                cy = out[out_idx, 0, det_idx, 4] * img.shape[0]
                class_ids.append(class_id)
                confidences.append(confidence)

    # Class with the highest confidence
    if len(class_ids) > 0:
        return np.argmax(confidences)
    else:
        return None

def main():
    labels = ["tidak ada objek", "objek menghadap kamera"]

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        result = classify_image(frame, labels)

        if result is not None:
            cv2.putText(frame, labels[result], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Tidak Ada Objek", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cap.release()
        cv2.destroyAllWindows()
