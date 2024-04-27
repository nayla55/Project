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
#kirim data ke telegrambot
token = "6688881089:AAHKj0JhR46Lkhy_8qJa47kAJIKdLZzdv9U"
chat_id = "5348170657"
def send_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, data=data)
    if response.status_code==200:
        print("Berhasil.")
    else:
        print("Error.")
    return response.json()

# kirim data ke ubidots
TOKEN = "BBFF-pgbtE8o9zoPgl7PGTeFVF0xkyQOQYT"
DEVICE_LABEL = "Project"
def kirim_data(payload):
    print(payload)
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url,DEVICE_LABEL)
    headers = {"X-Auth-Token":TOKEN,"Content-Type":"application/json"}
    status = 400
    attempts = 0
    while status >= 400 and attempts<=5:
        req = requests.post(url=url,headers=headers,json=payload)
        status = req.status_code
        attempts +=1
        time.sleep(1)
    
    print(req.status_code, req.json())
    
    if status>=400:
        print("Error")
        return False
    print("berhasil")
    return True

def build_payload(Jumlah):
    dict_message = {}
    for key in Jumlah.keys():
        dict_message[key] = Jumlah[key]
    return dict_message
    # return {"Jumlah":Jumlah,"cara_masak":cara_masak}

# output deteksi
while True:
    _, img = cap.read()
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
    # Menghitung Jumlah Objek     
    dict_total_class = {
        'Wortel': 0,
        'Kubis': 0,
        'Telur': 0,
        'Tahu Putih': 0,
        'Bawang Putih': 0
    }

    dict_resep = {
        'Memasak_Bakwan':0,
        'Memasak_Sayur_Sop':0,
        'Memasak_Rolade_Tahu':0,
        'Memasak_Tumis_Tahu_Sayuran':0,
        'Memasak_Perkedel_Tahu':0,
        'Memasak_Telur_Manis_Pedas':0,
        'Memasak_Telur_Dadar':0
    }


    for i in range(len(class_ids_filter)):
        dict_total_class[names[class_ids_filter[i]]] += 1
    print(dict_total_class)
    payload = build_payload(dict_total_class)
    kirim_data(payload)

    # Resep Otomatis
    Memasak_Bakwan = """
    1. Iris sayuran
    2. Cuci sayuran yang telah diiris
    3. Masukkan 15 sdm tepung terigu ke dalam wadah yang berisi sayuran
    4. Tambahkan kaldu ayam bubuk
    5. Aduk semua bahan hingga tercampur merata
    6. Panaskan minyak
    7. Setelah itu, goreng adonan bakwan hingga kuning kecoklatan
    8. Setelah matang, tiriskan bakwan
    9. Bakwan siap untuk disantap
    """
    Memasak_Sayur_Sop = """
    1. Cuci bersih wortel, kubis, dan pastikan kamu juga telah 
       mengupas kulit wortel sampai benar-benar bersih.
    2. Lalu, potong wortel berukuran dadu. Iris juga kubis sesuai selera.
    3. Kemudian, iris tipis-tipis bawang merah dan bawang putih, 
       lalu tumis kedua jenis bawang tersebut hingga harum. 
    4. Masukkan air ke dalam wajan atau panci berisi bawang tumis tadi dan didihkan.
    5. Setelah air mendidih, tambahkan potongan sayuran, garam, 
       lada, dan kaldu bubuk. Aduk sampai merata, lalu koreksi rasa. 
    6. Nah, kamu bisa memasak semua bahan tersebut selama 
       kurang lebih 10-15 menit. Periksa keempukan wortel.
    7. Setelah sayur sop matang, kamu bsia mengangkat dan hidangkan. 
       Jika memiliki bawang merah goreng, kamu juga dapat menaburkannya sebagai topping.
    """
    Memasak_Rolade_Tahu ="""
    1. Haluskan 2 bawang putih, ¼ sdt merica bubuk, ¼ sdt garam
    2. Haluskan tahu putih
    3. Panaskan sedikit minyak
    4. Tumis bumbu yang sudah dihaluskan
    5. Masukkan tahu yang sudah dihaluskan
    6. Tambahkan garam dan kaldu ayam secukupnya, aduk hingga merata
    7. Panaskan kukusan dan masukkan adonan tahu dalam cetakan. 
       Atau buat memanjang seperti lontong, dan bungkus dengan plastik atau daun pisang.
    8. Kukuk selama 15 menit. Angkat dan dinginkan.
    9. Dadar telur dan bungkus rolade dengan telur.
    10.  Bisa langsung disajikan atau digoreng lebih dulu.
    """
    Memasak_Tumis_Tahu_Sayuran = """
    1. Potong-potong tahu segitiga tebal 1 cm. Goreng dalam minyak panas 
       dan banyak hingga kering kecokelatan. Angkat dan tiriskan. Sisihkan.
    2. Tumis bawang putih hingga layu.
    3. Tambahkan irisan kubis. Aduk hingga layu.
    4. Masukkan tahu, kecap, saus tiram, merica, garam dan kaldu lalu didihkan.
    5. Tuangi larutan kanji, aduk hingga kental.
    6. Angkat dan sajikan hangat.
    """   
    Memasak_Perkedel_Tahu ="""
    1. Haluskan 5 siung bawang putih dan 5 buah cabai 
    2. Hancurkan tahu
    3. Campur semua bahan dan tambahkan tepung terigu 
       serta kaldu ayam secukupnya
    4. Aduk sampai tercampur rata
    5. Bentuk adonan perkedel berbentuk bulat. 
       Buat dengan bantuan sendok. Ulangi sampai adonan habis.
    6. Panaskan minyak goreng dan masukkan adonan. 
       Cukup balik sekali saja saat warnanya kekuningan. 
    7. Angkat saat sudah kering di bagian luar dan  tiriskan.
    8. Perkedel tahu siap dimakan.
    """
    Memasak_Telur_Manis_Pedas="""
    1. Goreng telur berbentuk mata sapi
    2. Jika sudah matang tiriskan telur
    3. Iris 3 siung bawang putih
    4. Potong dadu tomat dan iris cabai (option)
    5. Panaskan 2 sdm minyak
    6. Tumis bawang dan cabai hingga harum
    7. Masukkan sedikit air, garam, penyedap rasa, 
       dan irisan tomat. Aduk sampai mengental.
    8. Masukkan telur aduk rata. Angkat dan sajikan.
    """
    Memasak_Telur_Dadar = """
    1. Kocok lepas telur. Masukkan garam, 
       dan merica bubuk Aduk rata. Bagi menjadi bagian.
    2. Tuang campuran telur di dalam teflon.
    3. Biarkan sampai matang.
    """
    resep = []
    cara_masak = []
    if dict_total_class["Wortel"] >= 1 and dict_total_class["Kubis"] >=1 and dict_total_class["Bawang Putih"] >=1:
        resep.append("Bakwan")
        cara_masak.append(Memasak_Bakwan)
        dict_resep["Memasak_Bakwan"]=1
        # dict_total_class["Wortel"]-=1
        # dict_total_class["Kubis"] -=1
        # dict_total_class["Bawang Putih"] -=1

    if dict_total_class["Wortel"] >= 1 and dict_total_class["Kubis"] >=1 and dict_total_class["Bawang Putih"] >=1:
        resep.append("Sayur Soup")
        cara_masak.append(Memasak_Sayur_Sop)
        dict_resep["Memasak_Sayur_Sop"]=1
        # dict_total_class["Wortel"]-=1
        # dict_total_class["Kubis"] -=1
        # dict_total_class["Bawang Putih"] -=1

    if dict_total_class["Telur"] >= 1 and dict_total_class["Bawang Putih"] >=1 and dict_total_class["Tahu Putih"] >=1:
        resep.append("Rolade Tahu")
        cara_masak.append(Memasak_Rolade_Tahu)
        dict_resep["Memasak_Rolade_Tahu"]=1
        # dict_total_class["Telur"]-=1
        # dict_total_class["Tahu Putih"]-=1
        # dict_total_class["Bawang Putih"] -=1

    if dict_total_class["Bawang Putih"] >= 1 and dict_total_class["Kubis"] >= 1 and dict_total_class["Tahu"] >= 1:
        resep.append("Tumis Tahu Sayuran")
        cara_masak.append(Memasak_Tumis_Tahu_Sayuran)
        dict_resep["Memasak_Tumis_Tahu_Sayuran"]=1
        # dict_total_class["Bawang putih"] -=1
        # dict_total_class["Kubis"] -=1
        # dict_total_class["Tahu"] -=1

    if dict_total_class["Tahu Putih"] >= 1 and dict_total_class["Bawang Putih"] >=1:
        resep.append("Perkedel Tahu")
        cara_masak.append(Memasak_Perkedel_Tahu)
        dict_resep["Memasak_Perkedel_Tahu"]=1
        # dict_total_class["Tahu Putih"]-=1
        # dict_total_class["Bawang Putih"]-=1

    if dict_total_class["Telur"] >= 1 and dict_total_class["Bawang Putih"] >=1:
        resep.append("Telur Manis Pedas")
        cara_masak.append(Memasak_Telur_Manis_Pedas)
        dict_resep["Memasak_Telur_Manis_Pedas"]=1
        # dict_total_class["Telur"]-=1
        # dict_total_class["Bawang Putih"]-=1
        
    if dict_total_class["Telur"] >=1:
        resep.append("Telur Dadar")
        cara_masak.append(Memasak_Telur_Dadar)
        dict_resep["Memasak_Telur_Dadar"]=1
        # dict_total_class["Telur"]-=1

    for i in range(len(resep)):
        print("Rekomendasi Masakan {} = {}".format(i+1,resep[i]))
        print("Cara memasaknya adalah:")
        print(cara_masak[i])
    response = send_message(token, chat_id, cara_masak)# Kirim resep ke Telegram
    print(response)

    cv2.imshow("img", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()