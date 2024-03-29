import cv2
import time
import numpy as np

model: cv2.dnn.Net = cv2.dnn.readNetFromONNX("training.onnx")
# names = "person;bicycle;car;motorbike;aeroplane;bus;train;truck;boat;traffic light;fire hydrant;stop sign;parking meter;bench;bird;" \
#         "cat;dog;horse;sheep;cow;elephant;bear;zebra;giraffe;backpack;umbrella;handbag;tie;suitcase;frisbee;skis;snowboard;sports ball;kite;" \
#         "baseball bat;baseball glove;skateboard;surfboard;tennis racket;bottle;wine glass;cup;fork;knife;spoon;bowl;banana;apple;sandwich;" \
#         "orange;broccoli;carrot;hot dog;pizza;donut;cake;chair;sofa;pottedplant;bed;diningtable;toilet;tvmonitor;laptop;mouse;remote;keyboard;" \
#         "cell phone;microwave;oven;toaster;sink;refrigerator;book;clock;vase;scissors;teddy bear;hair dryer;toothbrush".split(";")
namess = {0: 'Wortel', 1: 'Kubis', 2: 'Telur', 3: 'Tahu Putih', 4: 'Bawang Putih'}
names = []
for n in namess.keys():
    names.append(namess[n])

img = cv2.imread('image.jpg')
height, width, _ = img.shape
length = max((height, width))
image = np.zeros((length, length, 3), np.uint8)
image[0:height, 0:width] = img
scale = length / 640

# First run to 'warm-up' the model
blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
model.setInput(blob)
model.forward()

# Second run
t1 = time.monotonic()
blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
model.setInput(blob)
outputs = model.forward()
print("dT:", time.monotonic() - t1)

# Show results
outputs = np.array([cv2.transpose(outputs[0])])
rows = outputs.shape[1]

boxes = []
scores = []
class_ids = []
output = outputs[0]
for i in range(rows):
    classes_scores = output[i][4:]
    minScore, maxScore, minClassLoc, (x, maxClassIndex) = cv2.minMaxLoc(classes_scores)
    if maxScore >= 0.25:
        box = [output[i][0] - 0.5 * output[i][2], output[i][1] - 0.5 * output[i][3],
               output[i][2], output[i][3]]
        boxes.append(box)
        scores.append(maxScore)
        class_ids.append(maxClassIndex)

result_boxes = cv2.dnn.NMSBoxes(boxes, scores, 0.25, 0.45, 0.5)
for index in result_boxes:
    box = boxes[index]
    box_out = [round(box[0]*scale), round(box[1]*scale),
               round((box[0] + box[2])*scale), round((box[1] + box[3])*scale)]
    if scores[index] > 0.25:
        cv2.rectangle(img, (box_out[0], box_out[1]), (box_out[2], box_out[3]), (0, 255, 0), 2)
        cv2.putText(img, names[class_ids[index]], (box_out[0], box_out[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imwrite("result.jpg", img)

        print("Rect:", names[class_ids[index]], scores[index], box_out)