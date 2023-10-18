import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr

import util
import cv2


# define constants
model_cfg_path = os.path.join('.', 'model', 'cfg', 'darknet-yolov3.cfg')
model_weights_path = os.path.join('.', 'model', 'weights', 'model.weights')
class_names_path = os.path.join('.', 'model', 'class.names')

input_dir = '../data'

video_capture = cv2.VideoCapture(0)

capture = True
process_this_frame = True

with open(class_names_path, 'r') as f:
    class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
    f.close()

net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)


while capture:
    ret, img = video_capture.read()

    H, W, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)
    net.setInput(blob)
    detections = util.get_outputs(net)

    bboxes = []
    class_ids = []
    scores = []

    for detection in detections:
        # [x1, x2, x3, x4, x5, x6, ..., x85]
        bbox = detection[:4]

        xc, yc, w, h = bbox
        bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]

        bbox_confidence = detection[4]

        class_id = np.argmax(detection[5:])
        score = np.amax(detection[5:])

        bboxes.append(bbox)
        class_ids.append(class_id)
        scores.append(score)
    bboxes, class_ids, scores = util.NMS(bboxes, class_ids, scores)

    reader = easyocr.Reader(['en'])
    for bbox_, bbox in enumerate(bboxes):
        xc, yc, w, h = bbox

        """
        cv2.putText(img,
                    class_names[class_ids[bbox_]],
                    (int(xc - (w / 2)), int(yc + (h / 2) - 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    7,
                    (0, 255, 0),
                    15)
        """

        license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)), int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

        img = cv2.rectangle(img,
                            (int(xc - (w / 2)), int(yc - (h / 2))),
                            (int(xc + (w / 2)), int(yc + (h / 2))),
                            (0, 255, 0),
                            5)
        license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

        _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

        output = reader.readtext(license_plate_thresh)

        number = ""

        for out in output:
            text_bbox, text, text_score = out
            
            number = number + text
            print(number)
         
        

    cv2.imshow('Video', img)
    cv2.setWindowProperty('Video', cv2.WND_PROP_TOPMOST, 1)
    
    if cv2.waitKey(1) & 0xFF == 13:
        break
video_capture.release()
cv2.destroyAllWindows()