#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: roi.py
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

import json

import cv2
import imutils
import numpy as np
# import joblib

pts = []  # para almacenar puntos


# Unificado: función de devolución de llamada del mouse
def draw_roi_tf(event, x, y, flags, params):
    img, pts = params
    img2 = img.copy()

    # Haga clic izquierdo para seleccionar el punto
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x, y))

    # Haga clic derecho para cancelar el último punto seleccionado
    if event == cv2.EVENT_RBUTTONDOWN:
        pts.pop()

    if event == cv2.EVENT_MBUTTONDOWN:  # Tecla central para dibujar el esquema
        mask = np.zeros(img.shape, np.uint8)
        points = np.array(pts, np.int32)
        points = points.reshape((-1, 1, 2))
        # Dibujar polígono
        mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
        # utilizado para encontrar el ROI
        mask2 = cv2.fillPoly(mask.copy(), [points], (255, 255, 255))
        # usado para mostrar la imagen en el escritorio
        mask3 = cv2.fillPoly(mask.copy(), [points], (0, 255, 0))

        show_image = cv2.addWeighted(src1=img,
                                     alpha=0.8,
                                     src2=mask3,
                                     beta=0.2,
                                     gamma=0)

        cv2.imshow("mask", mask2)
        cv2.imshow("show_img", show_image)

        roi = cv2.bitwise_and(mask2, img)
        cv2.imshow("ROI", roi)
        cv2.waitKey(0)

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

    cv2.imshow('image', img2)


def createROI_tf(filename):
    # Crear imagen y ventana y vincular ventana a función de devolución de llamada
    pts = []
    img = cv2.imread(filename)
    img = imutils.resize(img, width=500)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_roi_tf, (img, pts))
    print("[INFO] Clic izquierdo: seleccionar puntos, " +
          "clic derecho: borrar el último punto seleccionado, " +
          "clic medio: confirmar área de ROI")
    print("[INFO] Presione 'S' para confirmar el área seleccionada y guardar")
    print("[INFO] Presione ESC para salir")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == ord("s"):
            saved_data = {"ROI": pts}

            with open('TF.json', "w", encoding="utf-8") as file:
                json.dump(saved_data, file, indent=2)
                print(
                    "[INFO] Las coordenadas de ROI se han guardado localmente")

            break
    cv2.destroyAllWindows()
    return pts
