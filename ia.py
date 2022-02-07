#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: ia.py
Author:
    Sergio de la Barrera García <alu0100953275@ull.edu.es>
    Francisco Jesus Mendes Gomez <alu0101163970@ull.edu.es>
    Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Winter 2021-2022
College: University of La Laguna - Computer Science - Intelligent Systems
Description: This script implements the use of the YOLOv5 model to detect the
    pedestrians for our program
'''

import cv2
import numpy as np

IMAGE_QUALITY = 640


def format_yolov5(frame):
    '''Function to extend the image to be on a 1:1 aspect ratio.'''
    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result


def detect_pedestrians(img, net):
    '''Function to detect the pedestrians and add their bounding boxes to the
    image.'''
    results = detect(img, net)
    class_ids, confidences, boxes = unwrap_detection(img, results[0])

    class_list = ['person']
    colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]
    pedestrians_boxes = []

    for (classid, confidence, box) in zip(class_ids, confidences, boxes):
        # YOLOv5 person class id is '0'
        if classid == 0 and confidence > 0.5:
            color = colors[int(classid) % len(colors)]
            cv2.rectangle(img, box, color, 2)
            cv2.rectangle(img, (box[0], box[1] - 20), (box[0] + box[2], box[1]),
                          color, -1)
            cv2.putText(img, f'{class_list[classid]} {confidence}',
                        (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5,
                        (0, 0, 0))
            pedestrians_boxes.append(box)

    return pedestrians_boxes, img


def detect(image, net):
    '''Function to detect objects on the image.'''
    # resize to 640x640, normalize to [0,1[ and swap Red and Blue channels
    blob = cv2.dnn.blobFromImage(image,
                                 1 / 255.0, (IMAGE_QUALITY, IMAGE_QUALITY),
                                 swapRB=True,
                                 crop=False)
    net.setInput(blob)
    preds = net.forward()
    return preds


def unwrap_detection(input_image, output_data):
    '''Function to filter the pedestrians and get its bounding boxes and
    detection confidence.'''
    class_ids = []
    confidences = []
    boxes = []

    rows = output_data.shape[0]

    image_width, image_height, _ = input_image.shape

    x_factor = image_width / IMAGE_QUALITY
    y_factor = image_height / IMAGE_QUALITY

    for index in range(rows):
        row = output_data[index]
        confidence = row[4]
        if confidence >= 0.4:

            classes_scores = row[5:]
            _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
            class_id = max_indx[1]
            if classes_scores[class_id] > 0.25:

                confidences.append(confidence)

                class_ids.append(class_id)

                x_c, y_c, width, height = (row[0].item(), row[1].item(),
                                           row[2].item(), row[3].item())
                left = int((x_c - 0.5 * width) * x_factor)
                top = int((y_c - 0.5 * height) * y_factor)
                width = int(width * x_factor)
                height = int(height * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)

    result_class_ids = []
    result_confidences = []
    result_boxes = []

    for i in indexes:
        result_confidences.append(confidences[i])
        result_class_ids.append(class_ids[i])
        result_boxes.append(boxes[i])

    return result_class_ids, result_confidences, result_boxes
