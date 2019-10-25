from time import localtime
from time import strftime
from tkinter import *

from app.src import SheetReader
from app.src.Student import Student



GET_INDEX_REGEX = '\((\d+)\).+'

LOAD_MENU_OPT = "Provide Assistance"
REMOVE_MENU_OPT = "Remove"
RESET_MENU_OPT = "Reset"
CALL_MENU_OPT = "Call Student"

DATETIME_FORMAT = '%H:%M'

ARRIVED_BTN_TEXT = "Student Arrived"
NO_SHOW_BTN_TEXT = "No Show"
FINISHED_BTN_TEXT = "Next Request"

WINDOW_TITLE = "Lab Support"
HELPING_STU_PRFX = "Receiving Assistance: "
WAITING_STU_PRFX = "Waiting for: "

TOPIC = 'Issue: '
NAME = 'Name: '
NO_SHOW_LIST_TITLE = "Missed Appointments"
STUDENT_LIST_TITLE = "Waiting List"

INDEX = '({}) '

WINDOW_SIZE = '1200x330'
HEADER2_FONT = ("Courier New", 16)
HEADER1_FONT = ("Courier New", 18, 'bold')
BODY_FONT = ("Courier New", 12)
BG = 'white'
LIST_TOPFRM_PADX = 10
FRAME_TITLE_PADX = 5
NO_SHOW_FRM_PADX = 10
INFO_TXT_PADX = 10
INFO_WRAPLENGTH = 300
BTN_FRM_WIDTH = 400
ACTION_BTN_PADX = 20
INFO_FRAME_LENGTH = 350

COLOR_FROM_STATUS = {'1': "yellow",
                     '2': "orange",
                     '3': "green"}

WAITING = 1
HELPING = 2


class Gui:

    def __init__(self):

        # Create the sheet reader.
        self.reader = SheetReader.SheetReader()

        # Create the window:
        self.root = Tk()
        self.root.geometry(WINDOW_SIZE)
        self.root.title(WINDOW_TITLE)
        # self.root.wm_attributes("-topmost", 1)

        # Set status to waiting for student:
        self.current_status = WAITING

        # Create some data holders:
        self.current_student = None
        self.current_list = []
        self.no_shows_list = []

        # --- Build interface: ---

        # Student List:

        student_list_frame = Frame(self.root, relief=SUNKEN, borderwidth=2)

        names_label = Label(self.root, text=STUDENT_LIST_TITLE, font=HEADER1_FONT, justify=LEFT)
        names_label.grid(row=0, column=1, sticky=W, padx=FRAME_TITLE_PADX)

        names_canvas = Canvas(student_list_frame, bg=BG)

        self.names_frame = Frame(names_canvas, bg=BG)

        names_scrollbar = Scrollbar(student_list_frame, command=names_canvas.yview, orient=VERTICAL)
        names_canvas.configure(yscrollcommand=names_scrollbar.set)
        names_canvas.create_window((0, 0), window=self.names_frame, anchor=NW)
        student_list_frame.bind("<Configure>",
                                lambda x: names_canvas.configure(scrollregion=names_canvas.bbox(ALL)))
        student_list_frame.grid(row=1, column=1, padx=LIST_TOPFRM_PADX, rowspan=2)

        # added by Yitzchak:
        names_scrollbar2 = Scrollbar(student_list_frame, command=names_canvas.xview, orient=HORIZONTAL)
        names_scrollbar.pack(side=RIGHT, fill=Y, expand=True)
        names_scrollbar2.pack(side=BOTTOM, fill=X, expand=False)
        names_canvas.pack(side=LEFT, expand=True, fill=BOTH)
        names_canvas.configure(xscrollcommand=names_scrollbar2.set)
        # (now packed in the correct order so the scrollbars appear in their correct locations.


        # No-Shows list:
        no_shows_title = Label(self.root, text=NO_SHOW_LIST_TITLE,
                               font=HEADER1_FONT, justify=LEFT, padx=FRAME_TITLE_PADX)
        no_shows_title.grid(row=0, column=3, sticky=W)

        no_show_frame = Frame(self.root, relief=SUNKEN, borderwidth=2)

        no_shows_canvas = Canvas(no_show_frame, bg=BG)

        self.no_shows_frame = Frame(no_shows_canvas, bg=BG)
        no_shows_scrollbar = Scrollbar(no_show_frame, command=no_shows_canvas.yview, orient=VERTICAL)
        no_shows_canvas.configure(yscrollcommand=no_shows_scrollbar.set)

        no_shows_canvas.create_window((0, 0), window=self.no_shows_frame, anchor=NW)

        # added by Yitzchak:
        no_shows_scrollbar2 = Scrollbar(no_show_frame, command=no_shows_canvas.xview, orient=HORIZONTAL)
        no_shows_scrollbar2.pack(side=BOTTOM, fill=X, expand=True)
        no_shows_scrollbar.pack(side=RIGHT, fill=Y, expand=True)
        no_shows_canvas.pack(side=LEFT, expand=True, fill=BOTH)

        no_shows_canvas.configure(xscrollcommand=no_shows_scrollbar2.set)
        #

        no_show_frame.bind("<Configure>",
                           lambda x: no_shows_canvas.configure(scrollregion=no_shows_canvas.bbox(ALL)))
        no_show_frame.grid(row=1, column=3, padx=NO_SHOW_FRM_PADX, rowspan=2)

        # Current state frame:

        # self.current_stats_frame = Frame(self.root)
        # self.current_stats_frame.grid(row=0, column=3)

        self.current_student_label = Label(self.root, font=HEADER2_FONT, anchor=W, justify=LEFT,
                                           wraplength=INFO_WRAPLENGTH)
        self.current_student_label.grid(row=1, column=0, sticky=NW, padx=INFO_TXT_PADX)

        button_frame = Frame(self.root, width=BTN_FRM_WIDTH)

        self.action_button = Button(button_frame, text=ARRIVED_BTN_TEXT,
                                    command=self.student_arrived, font=BODY_FONT, default=ACTIVE)
        self.action_button.pack(side=LEFT, padx=ACTION_BTN_PADX)
        self.no_show_button = Button(button_frame, text=NO_SHOW_BTN_TEXT,
                                     command=self.student_no_show, font=BODY_FONT)
        self.no_show_button.pack()
        button_frame.grid(row=2, column=0, sticky=S)
        self.root.grid_columnconfigure(index=0, minsize=INFO_FRAME_LENGTH)

        # --- Initialize ---

        self.get_info()  # Get current data from spreadsheet
        self.next_student(False)  # Get the next student

        def draw_loop():
            self.root.after(5000, draw_loop)
            self.draw()

        self.root.after(1000, draw_loop)  # Draw the current data in a loop
        self.root.mainloop()  # Start the mainloop

    def get_info(self):
        rows = self.reader.get_current_rows()
        new_list = []
        no_show_list = []
        for index, row in enumerate(rows):
            stu = Student(row, index)
            if stu.status == SheetReader.SheetReader.NO_SHOW:
                no_show_list.append(stu)
            # elif stu.status == SheetReader.SheetReader.FINISHED:  # Automatically delete greens? reds?
            #     self.reader.remove_stu(stu.index)
            else:
                new_list.append(stu)
        self.current_list = new_list
        self.no_shows_list = no_show_list

    def draw(self):
        self.get_info()
        for slave in self.names_frame.pack_slaves():
            slave.pack_forget()
        for stu in self.current_list:
            color = BG
            if stu.status and stu.status in COLOR_FROM_STATUS:
                color = COLOR_FROM_STATUS[stu.status]
            name = Label(self.names_frame,
                         text=INDEX.format(
                             stu.index + 1) + NAME + stu.name + ', ' + TOPIC + stu.topic, bg=color, anchor=W,
                         font=BODY_FONT,
                         justify=LEFT, width=500)
            name.bind("<Button-3>", lambda event: self.right_click_menu(event))
            name.pack(anchor=W, fill=X, expand=True)

        for slave in self.no_shows_frame.pack_slaves():
            slave.pack_forget()
        for stu in self.no_shows_list:
            if stu.should_be_red():
                color = 'red'
            else:
                color = 'orange'
            name = Label(self.no_shows_frame,
                         text=INDEX.format(
                             stu.index + 1) + NAME + stu.name + ', ' + TOPIC + stu.topic, bg=color, anchor=W,
                         font=BODY_FONT,
                         justify=LEFT, width=500)
            name.bind("<Double-Button-1>",
                      lambda event: self.load_no_show(event))
            name.bind("<Button-3>", lambda event: self.right_click_menu(event))
            name.pack(anchor=W, fill=X, expand=True)

        name = ""
        topic = ""

        if self.current_student:
            topic = self.current_student.topic
            name = self.current_student.name

        if self.current_status == HELPING:
            self.current_student_label.configure(
                text=HELPING_STU_PRFX + '\n' + name + '\n\n' + TOPIC + '\n' + topic)
            self.action_button.configure(text=FINISHED_BTN_TEXT,
                                         command=self.next_student)
            self.no_show_button.configure(state=DISABLED)

        elif self.current_status == WAITING:
            self.current_student_label.configure(
                text=WAITING_STU_PRFX + '\n' + name + '\n\n' + TOPIC + '\n' + topic)
            self.no_show_button.configure(state=NORMAL)

            self.action_button.configure(text=ARRIVED_BTN_TEXT,
                                         command=self.student_arrived)

    def student_arrived(self):
        self.current_status = HELPING
        self.draw()

    def next_student(self, finished=True):
        if self.current_student and finished:
            self.reader.stu_finished(self.current_student.index)
            self.get_info()
        if len(self.current_list) == 0:
            self.current_student = None
            self.draw()
            return
        for stu in self.current_list:

            if (
                    not self.current_student or stu.timestamp != self.current_student.timestamp) and (
                    not stu.status):
                self.current_student = stu
                break
        else:
            self.current_student = None
            self.draw()
            return

        self.reader.stu_arrived(self.current_student.index)

        self.current_status = WAITING
        self.draw()

    def student_no_show(self):
        if not self.current_student:
            return
        hour = strftime(DATETIME_FORMAT, localtime())
        self.reader.stu_no_showed(self.current_student.index, hour)

        self.no_show_button.configure(state=DISABLED)
        self.next_student(False)

    def load_student(self, index):
        if self.current_student:
            if self.current_status == HELPING:
                self.reader.stu_finished(self.current_student.index)
            elif self.current_status == WAITING:
                self.reader.reset_stu(self.current_student.index)

        self.get_info()
        stu = self.stu_from_index(index)
        self.current_student = stu
        self.reader.stu_arrived(stu.index)
        self.current_status = HELPING
        self.draw()

    def call_stu(self, index):
        if self.current_student:
            if self.current_status == HELPING:
                self.reader.stu_finished(self.current_student.index)
            elif self.current_status == WAITING:
                self.reader.reset_stu(self.current_student.index)

        self.get_info()
        stu = self.stu_from_index(index)
        self.current_student = stu
        self.reader.stu_arrived(stu.index)
        self.current_status = WAITING
        self.draw()

    def stu_from_index(self, index):
        for stu in self.current_list:
            if stu.index == index:
                return stu
        for stu in self.no_shows_list:
            if stu.index == index:
                return stu

    def load_no_show(self, event):
        name = event.widget.cget('text')
        index = self.get_index_from_name(name)
        self.load_student(index)
        # self.reader.reset_stu(index)
        # if self.current_status == HELPING:
        #     self.next_student()
        # elif self.current_status == WAITING:
        #     self.reader.reset_stu(self.current_student.index)
        #     self.get_info()
        #     self.next_student(False)
        #
        # # self.reader.stu_arrived(index)
        # self.current_status = HELPING
        # self.action_button.configure(text=FINISHED_BTN_TEXT,
        #                              command=self.next_student)

    def right_click_menu(self, event):
        name = event.widget.cget('text')
        index = self.get_index_from_name(name)
        menu = Menu(event.widget, tearoff=0)
        menu.add_command(label=RESET_MENU_OPT,
                         command=lambda: self.reset_stu(index))
        menu.add_command(label=REMOVE_MENU_OPT,
                         command=lambda: self.remove_stu(index))
        menu.add_command(label=CALL_MENU_OPT,
                         command=lambda: self.call_stu(index))
        # if event.widget.master is self.no_shows_frame:
        menu.add_command(label=LOAD_MENU_OPT,
                         command=lambda: self.load_no_show(event))
        menu.post(event.x_root, event.y_root)

    def reset_stu(self, index):
        self.reader.reset_stu(index)
        self.get_info()
        if self.current_student and index is self.current_student.index:
            self.next_student(False)
        else:
            self.draw()

    def remove_stu(self, index):
        self.reader.remove_stu(index)
        self.get_info()
        if self.current_student:
            for stu in self.current_list:
                if stu.timestamp == self.current_student.timestamp:
                    self.current_student = stu
        self.draw()

    @staticmethod
    def get_index_from_name(name):
        pattern = GET_INDEX_REGEX
        return int(re.search(pattern, name).group(1)) - 1