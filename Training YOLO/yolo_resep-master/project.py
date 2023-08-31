import requests
import json

TOKEN = "BBFF-GQ3oWwWR1KPLgldycE0Eu2e4LH1bq8"
DEVICE_LABEL = "Project"

def kirim_data(payload):
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
        print("Ada Error")
        return False
    print("berhasil")
    return True

def build_payload(Jumlah_Objek,Resep):
    return {"Jumlah_Objek":Jumlah_Objek,"Resep":Resep}

