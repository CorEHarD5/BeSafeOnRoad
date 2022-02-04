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

Use case:
    Todo
'''


import cv2
import numpy as np
import PySimpleGUI as sg
# import PySimpleGUIQt as sg

from IA import *
from roi import *
from roivideo import *
# from trafficLight import *

def process_image(img_path):
    roi_cw = None
    roi_tl = None
    pedestrian_boxes = None
    tl_is_red = None

    roi_cw = create_roi(img_path, './temp/ROI_CW.json', 'Select Crosswalk ROI')
    print(roi_cw)
    roi_tl = create_roi(img_path, './temp/ROI_TL.json', 'Select Traffic Light ROI')
    print(roi_tl)
    tl_is_red = check_light_red(roi_tl, img_path)
    print(tl_is_red)

    if tl_is_red:
        pedestrian_boxes = detect_pedestrians(img_path)
        print(pedestrian_boxes)

        warn_pedenstrian = check_overlap(
            roi_cw, pedestrian_boxes, img_path)
        print(warn_pedenstrian)

        return warn_pedenstrian
    return False

def check_light_red(roi_pts_tf, img_path):
    print(roi_pts_tf, img_path)

    tf_image = cv2.imread(img_path)
    # tf_image = imutils.resize(tf_image, width=500)
    tf_image = format_yolov5(tf_image)
    roi_t = list(zip(*roi_pts_tf))

    pt1 = (min(roi_t[0]), min(roi_t[1]))
    pt2 = (max(roi_t[0]), max(roi_t[1]))
    roi_tf = tf_image[pt1[1]:pt2[1], pt1[0]:pt2[0], :].copy()

    red_bajo_1 = np.array([0, 100, 20], np.uint8)
    red_alto_1 = np.array([8, 255, 255], np.uint8)
    red_bajo_2 = np.array([175, 100, 20], np.uint8)
    red_alto_2 = np.array([179, 255, 255], np.uint8)

    frame_hsv = cv2.cvtColor(roi_tf, cv2.COLOR_BGR2HSV)
    mask_red_1 = cv2.inRange(frame_hsv, red_bajo_1, red_alto_1)
    mask_red_2 = cv2.inRange(frame_hsv, red_bajo_2, red_alto_2)
    mask_red = cv2.add(mask_red_1, mask_red_2)
    # mask_red_vis = cv2.bitwise_and(roi_tf, roi_tf, mask= mask_red)
    # cv2.imshow('frame', roi_tf)
    # cv2.imshow('maskRed', mask_red)
    # cv2.imshow('maskRedvis', mask_red_vis)

    list_of_whites = [pixel for line in mask_red for pixel in line]
    n_of_whites = list.count(list_of_whites, 255)
    percentage = (n_of_whites / roi_tf.size) * 100
    # cv2.destroyAllWindows()

    return percentage >= 10.0


def check_overlap(roi_cw, pedestrian_boxes, img_path):
    img = cv2.imread(img_path)
    # img = imutils.resize(img, width=500)
    img = format_yolov5(img)
    dst = np.zeros((len(img), len(img[1])), dtype=np.int8)

    for pedestian_box in pedestrian_boxes:
        src1 = dst.copy()
        src2 = dst.copy()

        src1[pedestian_box[1]:pedestian_box[1]+pedestian_box[3],
             pedestian_box[0]:pedestian_box[0]+pedestian_box[2]] = 1

        mask = np.zeros(img.shape, np.uint8)
        points = np.array(roi_cw, np.int32).reshape((-1, 1, 2))
        mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
        mask2 = cv2.fillPoly(mask.copy(), [points], (255, 255, 255))
        src2 = np.array([[1 if pixel[0] == 255 else 0 for pixel in line]
                         for line in mask2])

        overlap = src1 + src2  # sum of both *element-wise*
        overlap_list = [pixel for line in overlap for pixel in line]
        overlap_area = list.count(overlap_list, 2)

        pedestian_box_area = pedestian_box[2] * pedestian_box[3]
        if overlap_area > pedestian_box_area*0.2:
            return True

    return False


if __name__ == "__main__":
    process_image()
