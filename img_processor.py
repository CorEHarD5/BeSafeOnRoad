#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: img_processor.py
Author:
    Sergio de la Barrera García <alu0100953275@ull.edu.es>
    Francisco Jesus Mendes Gomez <alu0101163970@ull.edu.es>
    Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Winter 2021
College: University of La Laguna
Computer Science - Intelligent Sistems
Description: Todo
'''

import itertools
import cv2
import numpy as np
from shapely.geometry import Polygon

from ia import format_yolov5, detect_pedestrians
from roi import create_roi


def process_image(img, net, roi_cw=None, roi_tl=None):
    '''Function to process an image to get if a pedestrian is crossing the
    street while the traffic light is red.'''
    pedestrian_boxes = None
    tl_is_red = None
    warn_pedenstrian = False
    img = format_yolov5(img)

    if roi_cw is None or roi_tl is None:
        roi_cw, roi_tl = create_rois(img)

    tl_is_red = check_light_red(roi_tl, img)
    # print('tl_is_red', tl_is_red)

    if tl_is_red:
        pedestrian_boxes, img = detect_pedestrians(img, net)
        # print('pedestrian_boxes', pedestrian_boxes)

        warn_pedenstrian = check_overlap(roi_cw, pedestrian_boxes)

    img = add_info_to_img(img, roi_cw, color=(0, 255, 0), beta=0.2)
    img = add_info_to_img(img, roi_tl, color=(255, 0, 0), beta=0.7)

    return warn_pedenstrian, img


def create_rois(img):
    '''Function to select the region of interest where the crosswalk and the
    traffic lights are on the image.'''
    roi_cw = create_roi(img, './temp/ROI_CW.json', 'Select Crosswalk ROI')
    # print('roi_cw', roi_cw)
    roi_tl = create_roi(img, './temp/ROI_TL.json', 'Select Traffic Light ROI')
    # print('roi_tl', roi_tl)

    return roi_cw, roi_tl


def check_light_red(roi_pts_tf, input_img):
    '''Function to check if a traffic light is on red for the pedestrians.'''
    roi_t = list(zip(*roi_pts_tf))
    img = input_img.copy()

    pt1 = (min(roi_t[0]), min(roi_t[1]))
    pt2 = (max(roi_t[0]), max(roi_t[1]))
    roi_tf = img[pt1[1]:pt2[1], pt1[0]:pt2[0], :].copy()

    red_bajo_1 = np.array([0, 100, 20], np.uint8)
    red_alto_1 = np.array([8, 255, 255], np.uint8)
    red_bajo_2 = np.array([175, 100, 20], np.uint8)
    red_alto_2 = np.array([179, 255, 255], np.uint8)

    frame_hsv = cv2.cvtColor(roi_tf, cv2.COLOR_BGR2HSV)
    mask_red_1 = cv2.inRange(frame_hsv, red_bajo_1, red_alto_1)
    mask_red_2 = cv2.inRange(frame_hsv, red_bajo_2, red_alto_2)
    mask_red = cv2.add(mask_red_1, mask_red_2)

    list_of_whites = list(itertools.chain(*mask_red))
    n_of_whites = list.count(list_of_whites, 255)
    percentage = (n_of_whites / roi_tf.size) * 100

    return percentage >= 10.0


def check_overlap(roi_cw, pedestrian_boxes):
    '''Function to check if the crosswalk's region of interest overlaps with any
    of the pedestrian's bounding boxes.'''
    crosswalk_poligon = Polygon(roi_cw)

    for pedestrian_box in pedestrian_boxes:
        pedestrian_box_vertex = [
            (pedestrian_box[0], pedestrian_box[1]),
            (pedestrian_box[0] + pedestrian_box[2], pedestrian_box[1]),
            (pedestrian_box[0] + pedestrian_box[2],
             pedestrian_box[1] + pedestrian_box[3]),
            (pedestrian_box[0], pedestrian_box[1] + pedestrian_box[3]),
        ]
        pedestrian_poligon = Polygon(pedestrian_box_vertex)
        intersection_area = crosswalk_poligon.intersection(
            pedestrian_poligon).area
        pedestian_box_area = pedestrian_box[2] * pedestrian_box[3]

        if intersection_area > pedestian_box_area * 0.2:
            return True
    return False


def add_info_to_img(img, pts, color=(0, 255, 0), beta=0.3):
    '''Function to add the region of interest poligons to the image.'''
    mask = np.zeros(img.shape, np.uint8)
    points = np.array(pts, np.int32)
    points = points.reshape((-1, 1, 2))
    # Dibujar polígono
    mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
    # usado para mostrar la imagen en el escritorio
    mask2 = cv2.fillPoly(mask.copy(), [points], color)

    show_image = cv2.addWeighted(src1=img,
                                 src2=mask2,
                                 alpha=1,
                                 beta=beta,
                                 gamma=0)
    return show_image
