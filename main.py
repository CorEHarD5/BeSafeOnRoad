#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: main.py
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
import imutils
import io
import os.path

import numpy as np
import PIL.Image
import PySimpleGUI as sg

from IA import *
from roi import *
from roivideo import *
from img_processor import *


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


def main():
    toggle_section = True
    img_path = None
    video_path = None
    roi_cw = None
    roi_tl = None
    video_is_playing = False
    cap = None
    net = cv2.dnn.readNet('yolov5n.onnx')

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
            sg.In(default_text=IMAGE_QUALITY, key='-W-', size=(5, 1)),
            sg.In(default_text=IMAGE_QUALITY, key='-H-', size=(5, 1))
        ],
    ]

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
        [
            sg.Button('Start Checking'),
            sg.Text(text="Result: ", auto_size_text=True),
            sg.Text(auto_size_text=True, key="-WARNING IMAGE-"),
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

    video_buttons = [[
        sg.Button('Run Video'),
        sg.Button('Stop Video'),
    ]]

    video_viewer_column = [
        [sg.Text("Choose an video from list on left:")],
        [sg.Text(size=(40, 1), key="-VIDEO TOUT-")],
        [sg.Image(key="-VIDEO-")],
        [
            sg.Button('Load Video'),
            sg.Button('Select ROIs'),
            sg.Column(video_buttons, key='-VIDEO BUTTONS-', visible=False)
        ],
        [
            sg.Text(text="Result: ", auto_size_text=True),
            sg.Text(auto_size_text=True, key="-WARNING VIDEO-"),
        ],
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

    while True:  # Event Loop
        event, values = window.read(timeout=1)
        # print(event, values)
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
            fnames.sort()
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

        if event == 'Start Checking':
            img = cv2.imread(img_path)
            img = imutils.resize(img, width=IMAGE_QUALITY)
            row, col, _ = img.shape

            warn_pedenstrian, processed_img = process_image(img, net)
            print('warn_pedenstrian', warn_pedenstrian)
            if warn_pedenstrian:
                window['-WARNING IMAGE-'].update('WARNING!!',
                                                 text_color='black',
                                                 background_color='yellow')
            else:
                window['-WARNING IMAGE-'].update('No danger detected',
                                                 text_color='orange',
                                                 background_color='green')

            resized_img = np.zeros((row, col, 3), np.uint8)
            resized_img = processed_img[0:row, 0:col]
            imgbytes = cv2.imencode('.png', resized_img)[1].tobytes()
            window['-IMAGE-'].update(data=imgbytes)

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
                video_path = os.path.join(values['-VIDEO FOLDER-'],
                                        values['-FILE VIDEO LIST-'][0])
                window['-VIDEO TOUT-'].update(video_path)
                window['-VIDEO BUTTONS-'].update(visible=False)
            except Exception as err:
                # something weird happened making the full filename
                print(f'** Error {err} **')

        if event == 'Select ROIs':
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    video_is_playing = False
                else:
                    frame = imutils.resize(frame, width=IMAGE_QUALITY)
                    row, col, _ = frame.shape
                    roi_cw, roi_tl = create_rois(frame)

                    resized_frame = np.zeros((row, col, 3), np.uint8)
                    resized_frame = frame[0:row, 0:col]
                    imgbytes = cv2.imencode('.png', resized_frame)[1].tobytes()
                    window['-VIDEO-'].update(data=imgbytes)
                    window['-VIDEO BUTTONS-'].update(visible=True)

        if event == 'Load Video':
            video_is_playing = False
            cap = cv2.VideoCapture(video_path)

        if event == 'Run Video':
            video_is_playing = True

        if event == 'Stop Video':
            video_is_playing = False
            cap.release()

        if video_is_playing == True:
            if roi_cw is None or roi_tl is None:
                print('Error: rois not defined.')
                video_is_playing = False
            else:
                if cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        print("Can't receive frame (stream end?). Exiting ...")
                        video_is_playing = False
                    else:
                        frame = imutils.resize(frame, width=IMAGE_QUALITY)
                        row, col, _ = frame.shape
                        warn_pedenstrian, frame = process_image(frame, net, roi_cw, roi_tl)

                        if warn_pedenstrian:
                            window['-WARNING VIDEO-'].update('WARNING!!',
                                                             text_color='black',
                                                             background_color='yellow')
                        else:
                            window['-WARNING VIDEO-'].update('No danger detected',
                                                             text_color='orange',
                                                             background_color='green')

                        resized_frame = np.zeros((row, col, 3), np.uint8)
                        resized_frame = frame[0:row, 0:col]
                        imgbytes = cv2.imencode('.png', resized_frame)[1].tobytes()
                        window['-VIDEO-'].update(data=imgbytes)
                        window['-VIDEO BUTTONS-'].update(visible=True)
                else:
                    video_is_playing = False

        if event.startswith('-TOGGLE SEC'):
            toggle_section = not toggle_section

            window['-TOGGLE SEC1-RADIO'].update(toggle_section)
            window['-TOGGLE SEC2-RADIO'].update(not toggle_section)

            window['-SEC1-'].update(visible=toggle_section)
            window['-SEC2-'].update(visible=(not toggle_section))

    window.close()
    cap.release()


if __name__ == "__main__":
    main()
