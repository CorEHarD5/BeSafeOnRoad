import PySimpleGUI as sg

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


SYMBOL_UP = '▲'
SYMBOL_DOWN = '▼'


def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))


section1 = [[sg.Text('Image', text_color='yellow', size=(8, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Button('Run')]]


# Coger el image name {values[0]}
# [sg.Input('Input sec 1', key='-IN1-')],
# [sg.Input(key='-IN11-')],
# [sg.Button('Button section 1',  button_color='yellow on green'),
#  sg.Button('Button2 section 1', button_color='yellow on green'),
#  sg.Button('Button3 section 1', button_color='yellow on green')]]

section2 = [[sg.Text('Video', text_color='purple', size=(8, 1)), sg.Input(), sg.FileBrowse()],
            [sg.Button('Run')]]
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

    if event.startswith('-TOGGLE SEC'):
        toggle_section = not toggle_section

        window['-TOGGLE SEC1-RADIO'].update(toggle_section)
        window['-TOGGLE SEC2-RADIO'].update(not toggle_section)

        window['-SEC1-'].update(visible=toggle_section)
        window['-SEC2-'].update(visible=(not toggle_section))

window.close()
