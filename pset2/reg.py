"""Code for reg"""

import argparse
import socket
from sys import exit, argv
from pickle import load, dump

from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QListWidget
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QErrorMessage

from dialog import FixedWidthMessageDialog, FW_FONT


def get_filter_terms():
    """User interface. Gets host and port from user and returns them"""
    parser = argparse.ArgumentParser(description='Client for the registrar application',
                                    prog='reg.py', allow_abbrev=False, usage='%(prog)s ' +
                                    '[-h] host port')

    parser.add_argument('host', help='the host on ' +
                            'which the server is running')
    parser.add_argument('port', help='the port at which ' +
                            'the server is listening')

    return parser.parse_args()

def output_courses(test_table, listbox):
    """"Puts table contents in list box"""
    listbox.clear()
    for row in test_table:
        string = ''.join(row)
        listbox.addItem(string)

def button_called(line_edits, cmd_line_args, listbox, window):
    """Button called"""
    args = {}
    if line_edits["department"].text() == '':
        args['d'] = None
    else:
        args['d'] = line_edits["department"].text()
    if line_edits["title"].text() == '':
        args['t'] = None
    else:
        args['t'] = line_edits["title"].text()
    if line_edits["subject"].text() == '':
        args['s'] = None
    else:
        args['s'] = line_edits["subject"].text()
    if line_edits["course_num"].text() == '':
        args['n'] = None
    else:
        args['n'] = line_edits["course_num"].text()

    if not (line_edits["department"].text() == '' and line_edits["title"].text() == '' and
                line_edits["subject"].text() == '' and line_edits["course_num"].text() ==  ''):
        try:
            host = cmd_line_args.host
            port = int(cmd_line_args.port)

            with socket.socket() as sock:
                sock.connect((host, port))
                out_flo = sock.makefile(mode='wb')
                dump(args, out_flo)

                screen_size = QApplication.primaryScreen().availableGeometry()
                dump(screen_size.width()//2, out_flo)

                dump("courses", out_flo)
                out_flo.flush()

                in_flo = sock.makefile(mode='rb')
                courses = load(in_flo)
                output_courses(courses, listbox)

        except socket.error as ex:
            QErrorMessage(window).showMessage(str(ex))

    if (line_edits["department"].text() == '' and line_edits["title"].text() == '' and
        line_edits["subject"].text() == '' and line_edits["course_num"].text() ==  ''):
        listbox.clear()


def reg_details(cmd_line_args, crn, window):
    """Reg details"""
    try:
        host = cmd_line_args.host
        port = int(cmd_line_args.port)

        with socket.socket() as sock:
            sock.connect((host, port))
            out_flo = sock.makefile(mode='wb')
            dump(crn, out_flo)
            dump('dummy', out_flo)
            dump("details", out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode='rb')
            courses = load(in_flo)
            output_details(courses, crn, window)

    except socket.error as ex:
        QErrorMessage(window).showMessage(ex)

def output_details(courses, crn, window):
    """Outputting reg details"""
    count = 0
    course_details = ""
    for table in courses:
        if count != 0:
            course_details += "\n"
        course_details += str(table) + '\n'
        count += 1
    FixedWidthMessageDialog(f"Details for class {crn}", course_details, window).show()

def create_window(central_frame):
    """Creating window"""
    window = QMainWindow()
    window.setWindowTitle('Registrar Application')
    window.setCentralWidget(central_frame)
    screen_size = QApplication.primaryScreen().availableGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    return window

def create_lineedits():
    """Creating line edits"""
    department = QLineEdit()
    subject = QLineEdit()
    course_num = QLineEdit()
    title = QLineEdit()
    line_edits = {
        "department": department,
        "title": title,
        "subject": subject,
        "course_num": course_num
        }
    return line_edits

def create_labels():
    """Creating labels"""
    dep_label = QLabel('Department')
    subject_label = QLabel('Subject')
    course_num_label = QLabel('Course Number')
    title_label = QLabel('Title')

    labels = {
        "department": dep_label,
        "subject": subject_label,
        "course_num": course_num_label,
        "title": title_label
    }

    return labels

def create_central_frame(line_edits, labels, button, listbox):
    """Putting labels and line edits into one frame"""
    layout1 = QGridLayout()
    layout1.addWidget(labels["department"], 0, 0)
    layout1.addWidget(line_edits["department"], 0, 1)
    layout1.setContentsMargins(0, 0, 0, 0)
    frame1 = QFrame()
    frame1.setLayout(layout1)

    layout2 = QGridLayout()
    layout2.addWidget(labels["subject"], 0, 0)
    layout2.addWidget(line_edits["subject"], 0, 1)
    layout2.setContentsMargins(0, 0, 0, 0)
    frame2 = QFrame()
    frame2.setLayout(layout2)

    layout3 = QGridLayout()
    layout3.addWidget(labels["course_num"], 0, 0)
    layout3.addWidget(line_edits["course_num"], 0, 1)
    layout3.setContentsMargins(0, 0, 0, 0)
    frame3 = QFrame()
    frame3.setLayout(layout3)

    layout4 = QGridLayout()
    layout4.addWidget(labels["title"], 0, 0)
    layout4.addWidget(line_edits["title"], 0, 1)
    layout4.setContentsMargins(0, 0, 0, 0)
    frame4 = QFrame()
    frame4.setLayout(layout4)

    combined_frame = QFrame()
    combined_layout = QGridLayout()
    combined_layout.addWidget(frame1, 0, 0)
    combined_layout.addWidget(frame2, 1, 0)
    combined_layout.addWidget(frame3, 0, 1)
    combined_layout.addWidget(frame4, 1, 1)
    combined_layout.addWidget(button, 2, 0, 1, 2)
    combined_layout.addWidget(listbox, 3, 0, 1, 2)

    combined_frame.setLayout(combined_layout)

    return combined_frame

def main():
    """Main"""
    cmd_line_args = get_filter_terms()

    app = QApplication(argv)

    def button_slot():
        button_called(line_edits, cmd_line_args, listbox, window)

    def details_slot():
        selected_item = listbox.selectedItems()[0].text()
        crn = selected_item[:5]
        reg_details(cmd_line_args, crn, window)

    line_edits = create_lineedits()
    labels = create_labels()

    line_edits["department"].returnPressed.connect(button_slot)
    line_edits["subject"].returnPressed.connect(button_slot)
    line_edits["course_num"].returnPressed.connect(button_slot)
    line_edits["title"].returnPressed.connect(button_slot)

    listbox = QListWidget()
    listbox.setFont(FW_FONT)
    listbox.itemActivated.connect(details_slot)

    button = QPushButton('Submit Query')
    button.clicked.connect(button_slot)

    central_frame = create_central_frame(line_edits, labels, button, listbox)

    window = create_window(central_frame)

    window.show()
    exit(app.exec())

if __name__ == '__main__':
    main()
