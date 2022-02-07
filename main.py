#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: main.py
Author:
    Sergio de la Barrera García <alu0100953275@ull.edu.es>
    Francisco Jesus Mendes Gomez <alu0101163970@ull.edu.es>
    Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Winter 2021-2022
College: University of La Laguna - Computer Science - Intelligent Systems
Description: This program implements an Artificial Intelligence system capable
    of detecting pedestrians crossing the road when its traffic light is on red
    by using the YOLOv5 model, a convolutional neural network, for object
    detection on images.

Usage:
    ./main.py
'''

import base64
import io
import os.path

import cv2
import imutils
import numpy as np
import PIL.Image
import PySimpleGUI as sg

from ia import IMAGE_QUALITY
from img_processor import process_image, create_rois

DEFAULT_FRAME_RATE = 10


def main():
    '''Function to start the main gui window of the program.'''
    img_path = None
    video_path = None
    camera_id = None
    roi_cw = None
    roi_tl = None
    video_is_playing = False
    camera_is_playing = False
    fps_counter = 0
    video_frame_rate = None
    camera_frame_rate = None
    video_cap = None
    camera_cap = None
    net = cv2.dnn.readNet('./models/yolov5n.onnx')

    window = define_gui_layout()

    while True:  # Event Loop
        event, values = window.read(timeout=1)
        # print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        video_frame_rate = values['-VIDEO FRAME RATE SLIDER-']
        camera_frame_rate = values['-CAMERA FRAME RATE SLIDER-']

        # Folder name was filled in, make a list of files in the folder
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                file_list = os.listdir(folder)  # get list of files in folder
            except FileNotFoundError:
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
                window['-IMAGE-'].update(data=convert_to_bytes(
                    img_path, resize=(IMAGE_QUALITY, IMAGE_QUALITY)))
            except Exception as err:
                print(f'** Error {err} **')
                # something weird happened making the full filename

        if event == 'Start Checking':
            img = cv2.imread(img_path)
            img = imutils.resize(img, width=IMAGE_QUALITY)
            row, col, _ = img.shape

            warn_pedenstrian, processed_img = process_image(img, net)
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
            except FileNotFoundError:
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
                window['-VIDEO-'].update(source=None)
                window['Load/Reload Video'].update(disabled=False)
                window['Select Video ROIs'].update(disabled=True)
                window['Play/Pause Video'].update(disabled=True)
                window['Stop Video'].update(disabled=True)
                window['-VIDEO FRAME RATE SLIDER-'].update(disabled=True)
                window['-VIDEO WARNING-'].update('',
                                                 text_color=None,
                                                 background_color=None)
            except Exception as err:
                # something weird happened making the full filename
                print(f'** Error {err} **')

        if event == 'Load/Reload Video':
            video_is_playing = False
            video_cap = cv2.VideoCapture(video_path)
            fps_counter = 0
            window['-VIDEO FRAME RATE SLIDER-'].update(DEFAULT_FRAME_RATE)
            window['Select Video ROIs'].update(disabled=False)

        if event == 'Select Video ROIs':
            if video_cap.isOpened():
                ret, frame = video_cap.read()
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
                    window['Play/Pause Video'].update(disabled=False)
                    window['Stop Video'].update(disabled=False)
                    window['-VIDEO FRAME RATE SLIDER-'].update(disabled=False)

        if event == 'Play/Pause Video':
            video_is_playing = not video_is_playing
            window['Stop Video'].update(disabled=False)

        if event == 'Stop Video':
            video_is_playing = False
            window['Select Video ROIs'].update(disabled=True)
            window['Play/Pause Video'].update(disabled=True)
            window['Stop Video'].update(disabled=True)
            window['-VIDEO FRAME RATE SLIDER-'].update(disabled=True)
            video_cap.release()

        if video_is_playing:
            if roi_cw is None or roi_tl is None:
                print('Error: rois not defined.')
                video_is_playing = False
            else:
                if video_cap.isOpened():
                    ret, frame = video_cap.read()
                    if not ret:
                        print("Can't receive frame (stream end?). Exiting ...")
                        video_is_playing = False
                    else:
                        if fps_counter % video_frame_rate == 0:
                            frame = imutils.resize(frame, width=IMAGE_QUALITY)
                            row, col, _ = frame.shape
                            warn_pedenstrian, frame = process_image(
                                frame, net, roi_cw, roi_tl)

                            if warn_pedenstrian:
                                window['-VIDEO WARNING-'].update(
                                    'WARNING!!',
                                    text_color='black',
                                    background_color='yellow')
                            else:
                                window['-VIDEO WARNING-'].update(
                                    'No danger detected',
                                    text_color='orange',
                                    background_color='green')

                            resized_frame = np.zeros((row, col, 3), np.uint8)
                            resized_frame = frame[0:row, 0:col]
                            imgbytes = cv2.imencode('.png',
                                                    resized_frame)[1].tobytes()
                            window['-VIDEO-'].update(data=imgbytes)
                        fps_counter += 1
                else:
                    video_is_playing = False

        if event == '-CAMERA LIST-':  # A camera was chosen from the listbox
            try:
                camera_id = values['-CAMERA LIST-'][0]
                window['-CAMERA TOUT-'].update(f"Selected camera: {camera_id}")
                window['-CAMERA-'].update(source=None)
                window['Load/Reload Camera'].update(disabled=False)
                window['Select Camera ROIs'].update(disabled=True)
                window['Play/Pause Camera'].update(disabled=True)
                window['Stop Camera'].update(disabled=True)
                window['-CAMERA FRAME RATE SLIDER-'].update(disabled=True)
                window['-CAMERA WARNING-'].update('',
                                                 text_color=None,
                                                 background_color=None)
            except Exception as err:
                # something weird happened making the full filename
                print(f'** Error {err} **')

        if event == 'Load/Reload Camera':
            camera_is_playing = False
            camera_cap = cv2.VideoCapture(camera_id)
            fps_counter = 0
            window['-CAMERA FRAME RATE SLIDER-'].update(DEFAULT_FRAME_RATE)
            window['Select Camera ROIs'].update(disabled=False)

        if event == 'Select Camera ROIs':
            if camera_cap.isOpened():
                ret, frame = camera_cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    camera_is_playing = False
                else:
                    frame = imutils.resize(frame, width=IMAGE_QUALITY)
                    row, col, _ = frame.shape
                    roi_cw, roi_tl = create_rois(frame)

                    resized_frame = np.zeros((row, col, 3), np.uint8)
                    resized_frame = frame[0:row, 0:col]
                    imgbytes = cv2.imencode('.png', resized_frame)[1].tobytes()
                    window['-CAMERA-'].update(data=imgbytes)
                    window['Play/Pause Camera'].update(disabled=False)
                    window['Stop Camera'].update(disabled=False)
                    window['-CAMERA FRAME RATE SLIDER-'].update(disabled=False)

        if event == 'Play/Pause Camera':
            camera_is_playing = not camera_is_playing
            window['Stop Camera'].update(disabled=False)

        if event == 'Stop Camera':
            camera_is_playing = False
            window['Select Camera ROIs'].update(disabled=True)
            window['Play/Pause Camera'].update(disabled=True)
            window['Stop Camera'].update(disabled=True)
            window['-CAMERA FRAME RATE SLIDER-'].update(disabled=True)
            camera_cap.release()

        if camera_is_playing:
            if roi_cw is None or roi_tl is None:
                print('Error: rois not defined.')
                camera_is_playing = False
            else:
                if camera_cap.isOpened():
                    ret, frame = camera_cap.read()
                    if not ret:
                        print("Can't receive frame (stream end?). Exiting ...")
                        camera_is_playing = False
                    else:
                        if fps_counter % camera_frame_rate == 0:
                            frame = imutils.resize(frame, width=IMAGE_QUALITY)
                            row, col, _ = frame.shape
                            warn_pedenstrian, frame = process_image(
                                frame, net, roi_cw, roi_tl)

                            if warn_pedenstrian:
                                window['-CAMERA WARNING-'].update(
                                    'WARNING!!',
                                    text_color='black',
                                    background_color='yellow')
                            else:
                                window['-CAMERA WARNING-'].update(
                                    'No danger detected',
                                    text_color='orange',
                                    background_color='green')

                            resized_frame = np.zeros((row, col, 3), np.uint8)
                            resized_frame = frame[0:row, 0:col]
                            imgbytes = cv2.imencode('.png',
                                                    resized_frame)[1].tobytes()
                            window['-CAMERA-'].update(data=imgbytes)
                        fps_counter += 1
                else:
                    camera_is_playing = False

        if event.startswith('-TOGGLE SEC'):
            window['-SEC1-'].update(visible=values['-TOGGLE SEC1-RADIO-'])
            window['-SEC2-'].update(visible=values['-TOGGLE SEC2-RADIO-'])
            window['-SEC3-'].update(visible=values['-TOGGLE SEC3-RADIO-'])

    window.close()
    if video_cap is not None:
        video_cap.release()
    if camera_cap is not None:
        camera_cap.release()


def define_gui_layout():
    '''Function to define the gui layout.'''
    image_file_list_column = [
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
    ]

    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(auto_size_text=True, key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
        [
            sg.Button('Start Checking'),
            sg.Text(text="Result: ", auto_size_text=True),
            sg.Text(auto_size_text=True, key="-WARNING IMAGE-"),
        ],
    ]

    section1 = [[
        sg.Column(image_file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]]

    video_file_list_column = [
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
        [sg.Text(auto_size_text=True, key="-VIDEO TOUT-")],
        [sg.Image(key="-VIDEO-")],
        [
            sg.Button('Load/Reload Video', disabled=True),
            sg.Button('Select Video ROIs', disabled=True),
            sg.Button('Play/Pause Video', disabled=True),
            sg.Button('Stop Video', disabled=True),
        ],
        [
            sg.Text(text="Frame Rate: ", auto_size_text=True),
            sg.Slider(range=(1, 30),
                      default_value=DEFAULT_FRAME_RATE,
                      resolution=1,
                      orientation='h',
                      size=(40, 15),
                      disabled=True,
                      key='-VIDEO FRAME RATE SLIDER-')
        ],
        [
            sg.Text(text="Result: ", auto_size_text=True),
            sg.Text(auto_size_text=True, key="-VIDEO WARNING-"),
        ],
    ]

    section2 = [[
        sg.Column(video_file_list_column),
        sg.VSeperator(),
        sg.Column(video_viewer_column),
    ]]

    camera_list_column = [
        [
            sg.Listbox(values=get_camera_list(),
                       enable_events=True,
                       size=(40, 20),
                       key='-CAMERA LIST-')
        ],
    ]

    camera_viewer_column = [
        [sg.Text("Choose a camera from list on left:")],
        [sg.Text(auto_size_text=True, key="-CAMERA TOUT-")],
        [sg.Image(key="-CAMERA-")],
        [
            sg.Button('Load/Reload Camera', disabled=True),
            sg.Button('Select Camera ROIs', disabled=True),
            sg.Button('Play/Pause Camera', disabled=True),
            sg.Button('Stop Camera', disabled=True),
        ],
        [
            sg.Text(text="Frame Rate: ", auto_size_text=True),
            sg.Slider(range=(1, 30),
                      default_value=DEFAULT_FRAME_RATE,
                      resolution=1,
                      orientation='h',
                      size=(40, 15),
                      disabled=True,
                      key='-CAMERA FRAME RATE SLIDER-')
        ],
        [
            sg.Text(text="Result: ", auto_size_text=True),
            sg.Text(auto_size_text=True, key="-CAMERA WARNING-"),
        ],
    ]

    section3 = [[
        sg.Column(camera_list_column),
        sg.VSeperator(),
        sg.Column(camera_viewer_column),
    ]]

    layout = [
        [sg.Text('Choose between image or video')],
        [
            sg.Radio(' Image',
                     'Radio',
                     default=True,
                     enable_events=True,
                     key='-TOGGLE SEC1-RADIO-'),
            sg.Radio(' Video',
                     'Radio',
                     enable_events=True,
                     key='-TOGGLE SEC2-RADIO-'),
            sg.Radio(' Camera',
                     'Radio',
                     enable_events=True,
                     key='-TOGGLE SEC3-RADIO-'),
        ],
        [
            sg.Column(section1, key='-SEC1-'),
            sg.Column(section2, key='-SEC2-', visible=False),
            sg.Column(section3, key='-SEC3-', visible=False),
        ],
        [sg.Button('Exit')],
    ]

    window = sg.Window('BeSafeOnRoad', layout)
    return window


def get_camera_list():
    '''Function to get a list of available cameras.'''
    camera_ids = []

    for i in range(100):
        try:
            cap = cv2.VideoCapture(i)
            if cap is not None and cap.isOpened():
                camera_ids.append(i)
        except Warning:
            pass

    print(str(camera_ids))
    return camera_ids



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
        except Exception as _:
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


if __name__ == "__main__":
    main()
