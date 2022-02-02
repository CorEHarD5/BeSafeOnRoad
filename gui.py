import PySimpleGUI as sg
# import PySimpleGUIQt as sg
import os.path
import PIL.Image
import io
import base64
from roi import *

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

file_list_column = [[sg.Text('Folder'), sg.In(size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))]]

section1 = [[sg.Text('Image', text_color='yellow', size=(8, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Button('Run')]]



section2 = [[sg.Text('Video', text_color='purple', size=(8, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Button('Run')]]


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

    if event.startswith('-TOGGLE SEC'):
        toggle_section = not toggle_section

        window['-TOGGLE SEC1-RADIO'].update(toggle_section)
        window['-TOGGLE SEC2-RADIO'].update(not toggle_section)

        window['-SEC1-'].update(visible=toggle_section)
        window['-SEC2-'].update(visible=(not toggle_section))

window.close()
