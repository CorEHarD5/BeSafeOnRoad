import PySimpleGUI as sg
# import PySimpleGUIQt as sg
import os.path
import PIL.Image
import io
import base64
import numpy as np
import cv2
from roi import *
from roivideo import *

"""
    Demo - "Collapsible" sections of windows

    This demo shows one techinique for creating a collapsible section (Column) within your window.

    It uses the "pin" function so you'll need version 4.28.0+

    A number of "shortcut aliases" are used in the layouts to compact things a bit.
    In case you've not encountered these shortcuts, the meaning are:
    B = Button, T = Text, I = Input = InputText, k = key
    Also, both methods for specifying Button colors were used (tuple / single string)
    Section #2 uses them the most to show you what it's like to use more compact names.

    To open/close a section, click on the arrow or name of the section.
    Section 2 can also be controlled using the checkbox at the top of the window just to
    show that there are multiple way to trigger events such as these.

    Copyright 2020 PySimpleGUI.org
"""
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
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()


def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))

def check_overlap(roi):
    # if len(rois) < 2:
    #     print('Error: Not enough rois to check overlaping')
    #     return

    img = cv2.imread(filename)
    img = imutils.resize(img, width=500)

    dst = np.zeros((len(img),len(img[1])),dtype=np.int8)
    src1 = dst.copy()
    src2 = dst.copy()

    src1[:len(img)//2,:] = 1 # ToDo aquí se seleccionaría la roi con la bounding box del peatón

    mask = np.zeros(img.shape, np.uint8)
    points = np.array(roi, np.int32).reshape((-1, 1, 2))
    mask = cv2.polylines(mask, [points], True, (255, 255, 255), 2)
    mask2 = cv2.fillPoly (mask.copy (), [points], (255, 255, 255)) # utilizado para encontrar el ROI
    src2 = [[1 if pixel[0] == 255 else 0 for pixel in line] for line in mask2]

    overlap = src1 + src2 #sum of both *element-wise*
    overlap_list = [pixel for line in overlap for pixel in line]
    n_of_doeses = list.count(overlap_list, 2)
    print(n_of_doeses)


file_list_column = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))]]


image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    [sg.Button('Run Image')],
    [sg.Button('Check overlap')],
]

section1 = [
            [sg.Column(file_list_column),
             sg.VSeperator(),
             sg.Column(image_viewer_column),
             ]
            ]


# Coger el image name {values[0]}
            # [sg.Input('Input sec 1', key='-IN1-')],
            # [sg.Input(key='-IN11-')],
            # [sg.Button('Button section 1',  button_color='yellow on green'),
            #  sg.Button('Button2 section 1', button_color='yellow on green'),
            #  sg.Button('Button3 section 1', button_color='yellow on green')]]


file_list_column_video = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-VIDEO FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE VIDEO LIST-')]]


video_viewer_column = [
    [sg.Text("Choose an video from list on left:")],
    [sg.Text(size=(40, 1), key="-VIDEO TOUT-")],
    [sg.Image(key="-VIDEO-")],
    [sg.Button('Run Video')],
]

section2 = [
            [sg.Column(file_list_column_video),
             sg.VSeperator(),
             sg.Column(video_viewer_column),
             ]
            ]
            # [sg.I('Input sec 2', k='-IN2-')],
            # [sg.I(k='-IN21-')],
            # [sg.B('Button section 2',  button_color=('yellow', 'purple')),
            #  sg.B('Button2 section 2', button_color=('yellow', 'purple')),
            #  sg.B('Button3 section 2', button_color=('yellow', 'purple'))]]


layout = [[sg.Text('Choose between image or video')],
          [sg.Radio(' Image', 'Radio', default=True, enable_events=True, key='-TOGGLE SEC1-RADIO'),
           sg.Radio(' Video', 'Radio', enable_events=True, key='-TOGGLE SEC2-RADIO')],
          [sg.Column(section1, key='-SEC1-'), sg.Column(section2, key='-SEC2-', visible=False)],
          [sg.Button('Exit')], ]

window = sg.Window('BeSafeOnRoad', layout)

toggle_section = True

while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)
            if values['-W-'] and values['-H-']:
                new_size = int(values['-W-']), int(values['-H-'])
            else:
                new_size = None
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename

    if event == 'Run Image':
        print("Button clicked")
        img = values['-FILE LIST-']
        path = values['-FOLDER-'] + '/' + str(img[0])
        roi = createROI(path)

    if event == '-VIDEO FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-VIDEO FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".avi", ".mp4", ".mkv"))]
        window['-FILE VIDEO LIST-'].update(fnames)
    elif event == '-FILE VIDEO LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-VIDEO FOLDER-'], values['-FILE VIDEO LIST-'][0])
            window['-VIDEO TOUT-'].update(filename)
            window['-VIDEO-'].update(data=convert_to_bytes(filename, resize=new_size))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename

    if event == 'Run Video':
        print("Button clicked")
        img = values['-FILE VIDEO LIST-']
        path = values['-VIDEO FOLDER-'] + '/' + str(img[0])
        print(path)
        videoPlay(path)

    if event == 'Check overlap':
        check_overlap(roi)

    if event.startswith('-TOGGLE SEC'):
        toggle_section = not toggle_section

        window['-TOGGLE SEC1-RADIO'].update(toggle_section)
        window['-TOGGLE SEC2-RADIO'].update(not toggle_section)

        window['-SEC1-'].update(visible=toggle_section)
        window['-SEC2-'].update(visible=(not toggle_section))

window.close()
