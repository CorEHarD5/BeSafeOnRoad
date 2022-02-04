#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: versionConROI.py
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

import base64
import io
import os.path

import cv2
import imutils
import numpy as np
import PIL.Image
import PySimpleGUI as sg
# import PySimpleGUIQt as sg

from IA import *
from roi import *
from roivideo import *
# from trafficLight import *


def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            data_bytes_io = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(data_bytes_io)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height / cur_height, new_width / cur_width)
        img = img.resize(
            (int(cur_width * scale), int(cur_height * scale)),
            PIL.Image.ANTIALIAS,
        )
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()


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


def main():
    file_list_column = [
        [
            sg.Text('Folder'),
            sg.In(size=(25, 1), enable_events=True, key='-FOLDER-'),
            sg.FolderBrowse()
        ],
        [
            sg.Listbox(values=[],
                       enable_events=True,
                       size=(40, 20),
                       key='-FILE LIST-')
        ],
        [
            sg.Text('Resize to'),
            sg.In(default_text=640, key='-W-', size=(5, 1)),
            sg.In(default_text=640, key='-H-', size=(5, 1))
        ],
    ]

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
        [
            sg.Button('Select Crosswalk'),
            sg.Button('Select Traffic Light'),
            sg.Button('Detect pedestrians'),
        ],
        [
            sg.Button('Check Light Color'),
            sg.Button('Check overlap'),
        ],
    ]

    section1 = [[
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]]

    file_list_column_video = [
        [
            sg.Text('Folder'),
            sg.In(size=(25, 1), enable_events=True, key='-VIDEO FOLDER-'),
            sg.FolderBrowse()
        ],
        [
            sg.Listbox(values=[],
                       enable_events=True,
                       size=(40, 20),
                       key='-FILE VIDEO LIST-')
        ],
    ]

    video_viewer_column = [
        [sg.Text("Choose an video from list on left:")],
        [sg.Text(size=(40, 1), key="-VIDEO TOUT-")],
        [sg.Image(key="-VIDEO-")],
        [sg.Button('Run Video')],
    ]

    section2 = [[
        sg.Column(file_list_column_video),
        sg.VSeperator(),
        sg.Column(video_viewer_column),
    ]]

    layout = [
        [sg.Text('Choose between image or video')],
        [
            sg.Radio(' Image',
                     'Radio',
                     default=True,
                     enable_events=True,
                     key='-TOGGLE SEC1-RADIO'),
            sg.Radio(' Video',
                     'Radio',
                     enable_events=True,
                     key='-TOGGLE SEC2-RADIO')
        ],
        [
            sg.Column(section1, key='-SEC1-'),
            sg.Column(section2, key='-SEC2-', visible=False)
        ],
        [sg.Button('Exit')],
    ]

    window = sg.Window('BeSafeOnRoad', layout)

    toggle_section = True
    img_path = None
    roi_cw = None
    roi_tf = None
    pedestrian_boxes = None
    is_red = None

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        # Folder name was filled in, make a list of files in the folder
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                file_list = os.listdir(folder)  # get list of files in folder
            except:
                file_list = []
            fnames = [
                f for f in file_list
                if os.path.isfile(os.path.join(folder, f)) and
                f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))
            ]
            window['-FILE LIST-'].update(fnames)
        elif event == '-FILE LIST-':  # A file was chosen from the listbox
            try:
                img_path = os.path.join(values['-FOLDER-'],
                                        values['-FILE LIST-'][0])
                window['-TOUT-'].update(img_path)
                if values['-W-'] and values['-H-']:
                    new_size = int(values['-W-']), int(values['-H-'])
                else:
                    new_size = None
                window['-IMAGE-'].update(
                    data=convert_to_bytes(img_path, resize=new_size))
            except Exception as err:
                print(f'** Error {err} **')
                # something weird happened making the full filename

        if event == 'Select Crosswalk':
            print("Button clicked")
            img = values['-FILE LIST-']
            path = values['-FOLDER-'] + '/' + str(img[0])
            roi_cw = create_roi(path, './temp/ROI_CW.json')

        if event == 'Select Traffic Light':
            print("Button clicked")
            img = values['-FILE LIST-']
            path = values['-FOLDER-'] + '/' + str(img[0])
            roi_tf = create_roi(path, './temp/ROI_TF.json')

        if event == 'Detect pedestrians':
            pedestrian_boxes = detect_pedestrians(img_path)
            print(pedestrian_boxes)

        if event == 'Check Light Color':
            is_red = check_light_red(roi_tf, img_path)
            print(is_red)

        if event == 'Check overlap':
            warn_pedenstrian = check_overlap(
                roi_cw, pedestrian_boxes, img_path)
            print(warn_pedenstrian)

        # Folder name was filled in, make a list of files in the folder
        if event == '-VIDEO FOLDER-':
            folder = values['-VIDEO FOLDER-']
            try:
                file_list = os.listdir(folder)  # get list of files in folder
            except:
                file_list = []
            fnames = [
                f for f in file_list if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".avi", ".mp4", ".mkv"))
            ]
            window['-FILE VIDEO LIST-'].update(fnames)
        elif event == '-FILE VIDEO LIST-':  # A file was chosen from the listbox
            try:
                img_path = os.path.join(values['-VIDEO FOLDER-'],
                                        values['-FILE VIDEO LIST-'][0])
                window['-VIDEO TOUT-'].update(img_path)
                window['-VIDEO-'].update(
                    data=convert_to_bytes(img_path, resize=new_size))
            except Exception as err:
                # something weird happened making the full filename
                print(f'** Error {err} **')

        if event == 'Run Video':
            print("Button clicked")
            img = values['-FILE VIDEO LIST-']
            path = values['-VIDEO FOLDER-'] + '/' + str(img[0])
            print(path)
            videoPlay(path)

        if event.startswith('-TOGGLE SEC'):
            toggle_section = not toggle_section

            window['-TOGGLE SEC1-RADIO'].update(toggle_section)
            window['-TOGGLE SEC2-RADIO'].update(not toggle_section)

            window['-SEC1-'].update(visible=toggle_section)
            window['-SEC2-'].update(visible=(not toggle_section))

    window.close()


if __name__ == "__main__":
    main()
