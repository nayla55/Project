import cv2 
import time
import requests 
import math
import random 
import numpy as np


# Deteksi objek
model: cv2.dnn.Net = cv2.dnn.readNetFromONNX("training.onnx")
namess = {0: 'Wortel', 1: 'Kubis', 2: 'Telur', 3: 'Tahu Putih', 4: 'Bawang Putih'}
names = []
for n in namess.keys():
    names.append(namess[n])

cap = cv2.VideoCapture(0)

colors = [
    [0, 255, 0],
    [0, 0, 255],
    [255, 0, 0],
    [255,255,0],
    [0,255,255],
    [255,0,255],
    [255,255,255],
    [0,0,0],
    [128,128,128],
    [128,0,0],    
]

# output deteksi
while True:
    ret, img = cap.read()
    height, width, _ = img.shape
    length = max((height, width))
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = img
    scale = length / 640
    

    blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(640, 640), swapRB=True)
    model.setInput(blob)
    outputs = model.forward()
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
    
    class_ids_filter = []

    for index in result_boxes:
        box = boxes[index]
        box_out = [round(box[0]*scale), round(box[1]*scale),
                round((box[0] + box[2])*scale), round((box[1] + box[3])*scale)]
        if scores[index] > 0.25:
            cv2.rectangle(img, (box_out[0], box_out[1]), (box_out[2], box_out[3]), colors[class_ids[index]], 2)
            cv2.putText(img, names[class_ids[index]], (box_out[0], box_out[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[class_ids[index]], 2)
            class_ids_filter.append(class_ids[index])
                
    # Check if no object is detected
    if len(class_ids_filter) == 0:
        cv2.putText(img, "Tidak ada objek" , (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
        
    # Menghitung Jumlah Objek     
    dict_total_class = {
        'Wortel': 0,
        'Kubis': 0,
        'Telur': 0,
        'Tahu Putih': 0,
        'Bawang Putih': 0
    }

    for i in range(len(class_ids_filter)):
        dict_total_class[names[class_ids_filter[i]]] += 1
    for name, count in dict_total_class.items():
        print(f"{name}: {count}")
    
    cv2.imshow("img", img)
    if cv2.waitKey(1) == ord("q"):
        break
    time.sleep(3)
    
cap.release()
cv2.destroyAllWindows()
    
    
    
        





