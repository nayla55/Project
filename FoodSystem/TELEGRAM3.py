import cv2
import time
import requests 
import math
import random 
import numpy as np
import telebot


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

bot = telebot.TeleBot("6872870949:AAFhef34tOcgkNoUuK9ZXSZqpdBzpqYC6mQ")
chat_id = "5348170657"

def send_text_to_telegram(bot, chat_id, message):
    bot.send_message(bot, chat_id, message)

def send_image_to_telegram(bot, chat_id, image):
   photo = open(image, 'rb')
   bot.send_photo(bot, chat_id, photo)

#fungsi menangani pesan dari Telegram
@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    chat_id = message.chat.id 
    if message == '/start':
        bot.send_text_to_telegram(bot, chat_id, "Selamat Datang di Food System!")
    elif message == '/show':
        bot.send_image_to_telegram(bot, chat_id)
        bot.send_text_to_telegram(bot, chat_id, dict_total_class)
    elif message == '/resep':
        bot.send_text_to_telegram(bot, chat_id, cara_masak)
    else:
        bot.send_text_to_telegram(bot, chat_id, "Error")

    bot.polling()
    
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
            cv2.imwrite('img.jpg', img)
            class_ids_filter.append(class_ids[index])     
            bot.send_image_to_telegram(bot, chat_id, 'img.jpg')

    # Menghitung Jumlah Objek     
    dict_total_class = {
        'Wortel': 0,
        'Kubis': 0,
        'Telur': 0,
        'Tahu Putih': 0,
        'Bawang Putih': 0
    }

    dict_resep = {
        'resep_1':0,
        'resep_2':0,
        'resep_3':0,
        'resep_4':0,
        'resep_5':0
    }

    for i in range(len(class_ids_filter)):
        dict_total_class[names[class_ids_filter[i]]] += 1
    print(dict_total_class)
    bot.send_text_to_telegram(bot, chat_id, dict_total_class)

    # Resep Otomatis
    Resep_1 = """
    1. Bakwan
        Cara memasak :
        - Iris sayuran
        - Cuci sayuran yang telah diiris
        - Masukkan 15 sdm tepung terigu ke dalam wadah yang berisi sayuran
        - Tambahkan kaldu ayam bubuk
        - Aduk semua bahan hingga tercampur merata
        - Panaskan minyak
        - Setelah itu, goreng adonan bakwan hingga kuning kecoklatan
        - Setelah matang, tiriskan bakwan
        - Bakwan siap untuk disantap

    2. Sayur Soup
        Cara memasak :
        - Potong sayuran hingga berukuran kecil,
        - Cuci sayuran tersebut,
        - Masak air hingga mendidih,
        - Setelah air mendidih, masukkan sayuran,
        - Tambahkan kaldu ayam dan pedas bubuk secukupnya dan aduk hingga merata,
        - Tunggu hingga sayur matang,
        - Sayur soup pun siap dihidangkan
    """
    Resep_2 ="""
    1. Rolade Tahu
        Cara memasak :
        - Haluskan 2 bawang putih, ¼ sdt merica bubuk, ¼ sdt garam
        - Haluskan tahu putih
        - Panaskan sedikit minyak
        - Tumis bumbu yang sudah dihaluskan
        - Masukkan tahu yang sudah dihaluskan
        - Tambahkan garam dan kaldu ayam secukupnya, aduk hingga merata
        - Panaskan kukusan dan masukkan adonan tahu dalam cetakan. Atau buat memanjang seperti lontong, dan bungkus dengan plastik atau daun pisang.
        - Kukuk selama 15 menit. Angkat dan dinginkan.
        - Dadar telur dan bungkus rolade dengan telur.
        - Bisa langsung disajikan atau digoreng lebih dulu.
    """
    Resep_3 ="""
    1. Perkedel Tahu
        Cara memasak : 
        - Haluskan 5 siung bawang putih dan 5 buah cabai 
        - Hancurkan tahu
        - Campur semua bahan dan tambahkan tepung terigu serta kaldu ayam secukupnya
        - Aduk sampai tercampur rata
        - Bentuk adonan perkedel berbentuk bulat. Buat dengan bantuan sendok. Ulangi sampai adonan habis.
        - Panaskan minyak goreng dan masukkan adonan. Cukup balik sekali saja saat warnanya kekuningan. 
        - Angkat saat sudah kering di bagian luar dan  tiriskan.
        - Perkedel tahu siap dimakan.

    2. Tahu Saus Tiram
        Cara memasak : 
        - Potong tahu kecil-kecil, balur dengan tepung serba guna.
        - Panaskan minyak goreng
        - Goreng tahu sampai matang dan agak kering, Angkat lalu tiriskan.
        - Tumis  cabai dan bawang bombai sampai harum.
        - Kemudian masukkan tahu goreng dan saus tiram.
        - Aduk sampai rata. Tambahkan air dan matikan api saat air sudah mengental.
    """
    Resep_4 ="""
    1. Telur Manis Pedas
        Cara memasak : 
        - Goreng telur berbentuk mata sapi
        - Jika sudah matang tiriskan telur
        - Iris 3 siung bawang putih dan bawang merah
        - Potong dadu tomat dan iris cabai
        - Panaskan 2 sdm minyak
        - Tumis bawang dan cabai hingga harum
        - Masukkan sedikit air, garam, penyedap rasa, dan irisan tomat. Aduk sampai mengental.
        - Masukkan telur aduk rata. Angkat dan sajikan.
    """
    Resep_5 ="""
    1. Telur Gulung Saus Asam Manis
        Cara memasak : 
        Membuat telur : 
        - Kocok telur
        - Panaskan sedikit minyak ke dalam wajan
        - Goreng telur tersebut 
        - Jika telur sudah matang, gulung telur tersebut
        - Pindahkan telur ke dalam piring 
        - Potong telur tersebut menjadi beberapa bagian 
        Membuat saus : 
        - Iris bawang putih dan bawang bombay (option)
        - Panaskan sedikit minyak
        - Tumis bawang hingga harum
        - Masukkan saus pedas, saus tomat, dan sedikit garam, aduk hingga merata
        - Tunggu hingga matang
        - Siramkan saus tersebut di atas telur gulung yang sudah dipotong 
        - Telur pun siap dihidangkan 
    """
    resep = []
    cara_masak = []
    if dict_total_class["Wortel"] >= 1 and dict_total_class["Kubis"] >=1 and dict_total_class["Bawang Putih"] >=1:
        resep.append(" ")
        cara_masak.append(Resep_1)
        dict_resep["resep_1"]=1
        # dict_total_class["Wortel"]-=1
        # dict_total_class["Kubis"] -=1
        # dict_total_class["Bawang Putih"] -=1

    if dict_total_class["Telur"] >= 1 and dict_total_class["Bawang Putih"] >=1 and dict_total_class["Tahu Putih"] >=1:
        resep.append(" ")
        cara_masak.append(Resep_2)
        dict_resep["resep_2"]=1
        # dict_total_class["Telur"]-=1
        # dict_total_class["Tahu Putih"]-=1
        # dict_total_class["Bawang Putih"] -=1

    if dict_total_class["Tahu Putih"] >= 1 and dict_total_class["Bawang Putih"] >=1:
        resep.append(" ")
        cara_masak.append(Resep_3)
        dict_resep["resep_3"]=1
        # dict_total_class["Tahu Putih"]-=1
        # dict_total_class["Bawang Putih"]-=1

    if dict_total_class["Telur"] >= 1 and dict_total_class["Bawang Putih"] >=1:
        resep.append(" ")
        cara_masak.append(Resep_4)
        dict_resep["resep_4"]=1
        # dict_total_class["Telur"]-=1
        # dict_total_class["Bawang Putih"]-=1
        
    if dict_total_class["Telur"] >=1:
        resep.append(" ")
        cara_masak.append(Resep_5)
        dict_resep["resep_5"]=1
        # dict_total_class["Telur"]-=1

    for i in range(len(resep)):
        print ("Resep : ")
        print(cara_masak[i])
        bot.send_text_to_telegram(bot, chat_id, cara_masak)

    cv2.imshow("img", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()