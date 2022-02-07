#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: roi.py
Author:
    Sergio de la Barrera García <alu0100953275@ull.edu.es>
    Francisco Jesus Mendes Gomez <alu0101163970@ull.edu.es>
    Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Winter 2021-2022
College: University of La Laguna - Computer Science - Intelligent Systems
Description: This script implements some methods to select the regions of
    interest on an given image
'''

import json

import cv2

pts = []  # list of selected region of interest points


def create_rois(img):
    '''Function to select the region of interest where the crosswalk and the
    traffic lights are on the image.'''
    roi_cw = create_roi(img, './temp/ROI_CW.json', 'Select Crosswalk ROI')
    # print('roi_cw', roi_cw)
    roi_tl = create_roi(img, './temp/ROI_TL.json', 'Select Traffic Light ROI')
    # print('roi_tl', roi_tl)

    return roi_cw, roi_tl


def create_roi(input_img, export_filename, window_name='image'):
    '''Function to select a region of interest on the image.'''
    pts = []
    img = input_img.copy()
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, draw_roi, (img, pts, window_name))
    print("[INFO] Left click: select points.")
    print("[INFO] Right click: delete last selected point.")
    print("[INFO] Press 'S' to confirm the selected area and save it.")
    print("[INFO] Press 'ESC' to exit.")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

        if key == ord("s"):
            saved_data = {"ROI": pts}

            with open(export_filename, "w", encoding="utf-8") as file:
                json.dump(saved_data, file, indent=2)
                print(
                    "[INFO] The ROI's coordinates have been saved correctly.")
            break

    cv2.destroyAllWindows()
    return pts


def draw_roi(event, x_c, y_c, _, params):
    '''Function to get the selected points on the image with the mouse.'''
    img, pts, window_name = params
    img2 = img.copy()

    # Haga clic izquierdo para seleccionar el punto
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x_c, y_c))

    # Haga clic derecho para cancelar el último punto seleccionado
    if event == cv2.EVENT_RBUTTONDOWN:
        pts.pop()

    if len(pts) > 0:
        # Dibuja el último punto en pts
        cv2.circle(img2, pts[-1], 3, (0, 0, 255), -1)

    if len(pts) > 1:
        # Dibuja una línea
        for i in range(len(pts) - 1):
            # x, y son las coordenadas del clic del mouse
            cv2.circle(img2, pts[i], 5, (0, 0, 255), -1)
            cv2.line(img=img2,
                     pt1=pts[i],
                     pt2=pts[i + 1],
                     color=(255, 0, 0),
                     thickness=2)
        cv2.line(img=img2,
                 pt1=pts[-1],
                 pt2=pts[0],
                 color=(255, 0, 0),
                 thickness=2)

    cv2.imshow(window_name, img2)
