import json
import cv2
import easyocr
import re
import requests
import multiprocessing

###
reader = easyocr.Reader(['ru'])
cars = cv2.CascadeClassifier('cars.xml')
###

def screenShot(cap):
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    return frame

def readNumber(place, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    url = 'http://89.108.71.234:8000/api/car/'  # Если сервер стоит не на этой же машине, то надо указать ip

    res = cars.detectMultiScale(gray, scaleFactor=1.4, minNeighbors=3)

    crop_img = []
    for (x, y, w, h) in res:
        crop_img = (gray[y:y + h, x:x + w])

    if crop_img != []:
        cv2.imshow('res', frame) #
        cv2.waitKey(2000) #

        text = reader.readtext(crop_img, allowlist='0123456789АВЕКМНОРСТУХавекмнорстух')
        if text:
            s = str(text[0][-2].replace(" ", "").upper())
            print(s)
            result = re.findall(r'[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}', s)
            if result != []:
                print(result[0])  # Возвращает номер по регулярке
                data = {"number": str(result[0]), "place": str(place)}
                headers = {'Content-type': 'application/json'}
                response = requests.post(url, data=json.dumps(data), headers=headers)
                print(response.status_code)

def handler(camera):
    num = int(camera['count'])
    cap = cv2.VideoCapture(num, cv2.CAP_DSHOW)
    frame = screenShot(cap)
    if frame is None:
        print("camera №" + str(num) + " on place \"" + str(camera['place']) + " \"is not allowed")
    else:
        readNumber(camera['place'], frame)


def main():
    with open('camersconf.json', 'r', encoding='utf-8') as f:
        camers = json.load(f)
    while True:
        with multiprocessing.Pool(len(camers['v_stream'])) as process:
            process.map(handler, camers['v_stream'])


if __name__ == '__main__':
    main()
