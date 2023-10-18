from django.shortcuts import render
from pathlib import Path
import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr
import itertools
import re
from core.models import *
import winsound
from playsound import playsound
from twilio.rest import Client


account_sid = ''
auth_token = ''


def NMS(boxes, class_ids, confidences, overlapThresh = 0.5):

    boxes = np.asarray(boxes)
    class_ids = np.asarray(class_ids)
    confidences = np.asarray(confidences)

    # Return empty lists, if no boxes given
    if len(boxes) == 0:
        return [], [], []

    x1 = boxes[:, 0] - (boxes[:, 2] / 2)  # x coordinate of the top-left corner
    y1 = boxes[:, 1] - (boxes[:, 3] / 2)  # y coordinate of the top-left corner
    x2 = boxes[:, 0] + (boxes[:, 2] / 2)  # x coordinate of the bottom-right corner
    y2 = boxes[:, 1] + (boxes[:, 3] / 2)  # y coordinate of the bottom-right corner

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)

    indices = np.arange(len(x1))
    for i, box in enumerate(boxes):
        # Create temporary indices
        temp_indices = indices[indices != i]
        # Find out the coordinates of the intersection box
        xx1 = np.maximum(box[0] - (box[2] / 2), boxes[temp_indices, 0] - (boxes[temp_indices, 2] / 2))
        yy1 = np.maximum(box[1] - (box[3] / 2), boxes[temp_indices, 1] - (boxes[temp_indices, 3] / 2))
        xx2 = np.minimum(box[0] + (box[2] / 2), boxes[temp_indices, 0] + (boxes[temp_indices, 2] / 2))
        yy2 = np.minimum(box[1] + (box[3] / 2), boxes[temp_indices, 1] + (boxes[temp_indices, 3] / 2))

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / areas[temp_indices]
        # if overlapping greater than our threshold, remove the bounding box
        if np.any(overlap) > overlapThresh:
            indices = indices[indices != i]

    # return only the boxes at the remaining indices
    return boxes[indices], class_ids[indices], confidences[indices]


def get_outputs(net):

    layer_names = net.getLayerNames()

    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    outs = net.forward(output_layers)

    outs = [c for out in outs for c in out if c[4] > 0.1]

    return outs


def draw(bbox, img):

    xc, yc, w, h = bbox
    img = cv2.rectangle(img,
                        (xc - int(w / 2), yc - int(h / 2)),
                        (xc + int(w / 2), yc + int(h / 2)),
                        (0, 255, 0), 20)

    return img

def index_view(request):  

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # define constants
    model_cfg_path = os.path.join(BASE_DIR, 'media', 'model', 'cfg', 'darknet-yolov3.cfg')
    model_weights_path = os.path.join(BASE_DIR, 'media', 'model', 'weights', 'model.weights')
    class_names_path = os.path.join(BASE_DIR, 'media', 'model', 'class.names')

    video_capture = cv2.VideoCapture(0)

    capture = True
    process_this_frame = True

    with open(class_names_path, 'r') as f:
        class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
        f.close()

    net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

    plates=""
    country = "Not Zimbabwe"
    while capture:
        ret, img = video_capture.read()

        H, W, _ = img.shape
        blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)
        net.setInput(blob)
        detections = get_outputs(net)

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
        bboxes, class_ids, scores = NMS(bboxes, class_ids, scores)

        reader = easyocr.Reader(['en'])
        for bbox_, bbox in enumerate(bboxes):
            xc, yc, w, h = bbox
            license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)), int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

            img = cv2.rectangle(img,
                                (int(xc - (w / 2)), int(yc - (h / 2))),
                                (int(xc + (w / 2)), int(yc + (h / 2))),
                                (0, 255, 0),
                                5)
            license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

            _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

            output = reader.readtext(license_plate)

            number = ""

            for out in output:
                text_bbox, text, text_score = out
                
                number = number + text

            print(number)
            if (text_score > 0.5):
                number = number.replace(" ", "")
                pattern = r'^[a-zA-Z]{3}\d{4}$'
                
                if re.match(pattern, number):                  
                    print("Zim plate: "+number)
                    country = "Zimbabwe"
                    vehicle = None
                    try:
                        vehicle = Vehicle.objects.get(number_plate=number)
                    except:
                        continue
                    plates=number

                    if vehicle:
                        acc = Account.objects.get(owner = vehicle.owner.id)
                        amount = 2
                        if(vehicle.type_id != 4):
                            amount = 5

                        trans = Transaction.objects.create(amount=amount, account=acc, vehicle=vehicle)
                        
                        sound_file = BASE_DIR + '\\static\\sounds\\success.mp3'  # Path to your custom beep sound file
                        playsound(sound_file)
                        print(number)
                        trans.save()

                        acc.balance -= amount
                        acc.save()
                        client = Client(account_sid, auth_token)
                        message = client.messages.create(
                                body=f'Hello, ${amount} deducted using Smart Tolgate System. New account balance is ${acc.balance}',
                                from_='+12545874926',  # Your Twilio phone number
                                to='+263785731194'  # Recipient's phone number
                            )
                        
                else:
                    print("Not zim plate")
                    print(number)
                    plates = number
                    sound_file = BASE_DIR + '\\static\\sounds\\failure.mp3'  # Path to your custom beep sound file
                    playsound(sound_file)
                    
                    #capture = False
                
            
        cv2.imshow('Video', img)
        cv2.setWindowProperty('Video', cv2.WND_PROP_TOPMOST, 1)
        
        if cv2.waitKey(1) & 0xFF == 13:
            break
    video_capture.release()
    cv2.destroyAllWindows()

    '''
    
    number_plates =[]
    images = []
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # define constants
    model_cfg_path = os.path.join(BASE_DIR, 'media', 'model', 'cfg', 'darknet-yolov3.cfg')
    model_weights_path = os.path.join(BASE_DIR, 'media', 'model', 'weights', 'model.weights')
    class_names_path = os.path.join(BASE_DIR, 'media', 'model', 'class.names')

    input_dir = os.path.join(BASE_DIR, 'media', "data")

    for img_name in os.listdir(input_dir):

        img_path = os.path.join(input_dir, img_name)
        images.append(img_name)
        
        # load class names
        with open(class_names_path, 'r') as f:
            class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
            f.close()

        # load model
        net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

        # load image

        img = cv2.imread(img_path)

        H, W, _ = img.shape

        # convert image
        blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)

        # get detections
        net.setInput(blob)

        detections = get_outputs(net)

        # bboxes, class_ids, confidences
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

        # apply nms
        bboxes, class_ids, scores = NMS(bboxes, class_ids, scores)

        # plot
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
                                15)

            license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

            _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

            output = reader.readtext(license_plate_thresh)

            pred_plate_text = ""
            for out in output:
                text_bbox, text, text_score = out
                if text_score > 0.2:
                    print(text, text_score)
                    pred_plate_text = pred_plate_text + text
            number_plates.append(pred_plate_text)

    mylist = zip(images, number_plates)
    
    context = {
                'mylist': mylist
            }     
    '''

    return render(request, 'control/index.html', {'plates':plates, 'country': country})
