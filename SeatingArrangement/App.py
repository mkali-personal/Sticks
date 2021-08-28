from OptionalsChosenLists import OptionalsChosenLists
from RadioButtonFrame import RadioButtonFrame
from SeatingArrangement import SeatingArrangement
from Student import Student
import tkinter as tk
from tkinter import ttk


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.students = []
        self.current_edited_student = None
        self.parsed_data = None
        self.introduction_window = None
        self.names_to_be_inserted_win = None
        self.seating_arrangement = None
        self.choose_row_col_win = None
        self.row_radio = None
        self.col_radio = None
        self.optional_rows = None
        self.optional_columns = None
        self.geometry('900x720')

        self.bind('<<Paste>>', lambda x: self.accept_clipboard_data())

        self.names_management_frame = tk.Frame(self)
        self.names_management_frame.grid(column=0, row=0, padx=7, pady=7)

        self.ctrl_v_tip = tk.Label(self.names_management_frame,
                                   text='או\n תוכלו גם פה להעתיק שמות מרשימה\nאחרת ולהדביק אותם פה')
        self.ctrl_v_tip.grid(column=6, row=3, padx=7)

        self.add_student_label = tk.Label(self.names_management_frame,
                                          text="!שכחתם תלמיד? אל דאגה\n:תוכלו להוסיף עוד תלמידים ידנית")
        self.add_student_label.grid(column=6, row=1, padx=7)

        self.add_student_entry = tk.Entry(self.names_management_frame)
        self.placeholder_foc_out()
        self.add_student_entry.grid(column=6, row=2, padx=7, pady=7)
        self.add_student_entry.bind('<Return>', lambda x: self.manual_student_addition())
        self.add_student_entry.bind('<FocusIn>', lambda x: self.placeholder_foc_in())
        self.add_student_entry.bind('<FocusOut>', lambda x: self.placeholder_foc_out())
        self.add_student_entry.configure(justify='right')
        self.placeholder_foc_out()

        self.names_listbox_frame = tk.Frame(self.names_management_frame)
        self.names_listbox_frame.grid(column=2, row=1, rowspan=3, padx=7, pady=7)
        self.names_listbox = tk.Listbox(self.names_listbox_frame)
        self.names_listbox.grid(column=2, row=0, padx=7, pady=7)
        self.names_listbox.bind('<ButtonRelease-1>', lambda x: self.load_chosen_names())
        self.names_listbox.bind('<KeyRelease-Up>', lambda x: self.load_chosen_names())
        self.names_listbox.bind('<KeyRelease-Down>', lambda x: self.load_chosen_names())
        self.names_listbox.bind('<Button-1>', lambda x: self.update_current_student())
        self.names_listbox.bind('<Up>', lambda x: self.update_current_student())
        self.names_listbox.bind('<Down>', lambda x: self.update_current_student())
        OptionalsChosenLists.attach_scrollbar_to_widget(self.names_listbox_frame, self.names_listbox)
        self.names_listbox.configure(justify='right')

        self.add_student_button = tk.Button(self.names_management_frame, text="<-- הוסף תלמיד <--",
                                            command=self.manual_student_addition)
        self.add_student_button.grid(column=5, row=2, padx=7, pady=7)
        self.remove_student_button = tk.Button(self.names_management_frame, text="מחק את התלמיד המסומן",
                                               command=self.remove_student)
        self.remove_student_button.grid(column=1, row=2, padx=7, pady=7)
        self.remove_all_students_button = tk.Button(self.names_management_frame, text="מחק את כל התלמידים",
                                                    command=self.remove_all_students)
        self.remove_all_students_button.grid(column=1, row=3, padx=7, pady=7)

        self.separator_line = ttk.Separator(self.names_management_frame, orient="horizontal")
        self.separator_line.grid(column=0, row=4, columnspan=7, sticky='we')

        self.current_editing_label = tk.Label(self.names_management_frame, text="כרגע אתם עורכים את ההעדפות של ")
        self.current_editing_label.grid(column=2, row=4, padx=7)

        self.student_info_frame = tk.Frame(self, borderwidth=2, relief="groove")
        self.student_info_frame.grid(column=0, row=2)

        self.near_by_list = OptionalsChosenLists(self.student_info_frame,
                                                 u'תלמידים לידם מותר לו לשבת',
                                                 u'תלמידים לידם אסור לו לשבת')
        self.near_by_list.grid(column=2, row=2, padx=7, pady=7)
        self.eye_contact_list = OptionalsChosenLists(self.student_info_frame,
                                                     u'תלמידים איתם מותר שיהיה לו קשר עין',
                                                     u'תלמידים איתם אסור שיהיה לו קשר עין',
                                                     warning_above_one=True)
        self.eye_contact_list.grid(column=2, row=3, padx=7, pady=7)
        self.preferred_rows_list = OptionalsChosenLists(self.student_info_frame,
                                                        u'שורות בהן הוא לא יכול לשבת',
                                                        u'שורות בהן הוא יכול לשבת',
                                                        reversed_direction=True)
        self.preferred_rows_list.grid(column=4, row=2, padx=7, pady=7)
        self.preferred_columns_lists = OptionalsChosenLists(self.student_info_frame,
                                                            u'טורים בהם הוא לא יכול לשבת',
                                                            u'טורים בהם הוא יכול לשבת',
                                                            reversed_direction=True)
        self.preferred_columns_lists.grid(column=4, row=3, padx=7, pady=7)

        self.generate_class_button = tk.Button(self.names_management_frame,
                                               text="סדר את התלמידים",
                                               command=self.generate_seating_arrangement)
        self.generate_class_button.config({"bg": '#C6EFCE'})
        self.generate_class_button.grid(column=0, row=2, padx=40)

        self.names_listbox.insert(tk.END, *self.students_names_list())

        self.choose_row_col_num()
        self.wm_state('iconic')

    def students_names_list(self):
        return [s.name for s in self.students]

    def choose_row_col_num(self):
        self.choose_row_col_win = tk.Toplevel()

        self.row_radio = RadioButtonFrame(self.choose_row_col_win, [4, 5], ':בחרו כמה שורות יש בכיתה')
        self.row_radio.grid(row=0, column=0)
        self.col_radio = RadioButtonFrame(self.choose_row_col_win, [4, 5], ':בחרו כמה עמודות יש בכיתה')
        self.col_radio.grid(row=0, column=2)

        self.center_window(self.choose_row_col_win)
        self.choose_row_col_win.lift()

        tk.Button(self.choose_row_col_win, text='אשר', command=self.confirm_row_col_num).grid(row=1, column=1)


    def confirm_row_col_num(self):
        if self.row_radio.result.get() == 4:
            self.optional_rows = {'ראשונה': 0, 'שניה': 1, 'שלישית': 2, 'רביעית': 3}
        else:
            self.optional_rows = {'ראשונה': 0, 'שניה': 1, 'שלישית': 2, 'רביעית': 3, 'חמישית':4}
        if self.col_radio.result.get() == 4:
            self.optional_columns = {'שמאלי': 0, 'שני משמאל': 1, 'שני מימין': 2, 'ימני': 3}
        else:
            self.optional_columns = {'שמאלי': 0, 'שני משמאל': 1, 'אמצעי': 2, 'שני מימין': 3, 'ימני': 4}
        self.choose_row_col_win.destroy()
        self.initialize_introduction_window()

    def initialize_introduction_window(self):
        self.introduction_window = tk.Tk()
        self.introduction_window.wm_title("ברוכים הבאים למסדר התלמידים של קלי!")
        instructions = tk.Label(self.introduction_window,
                                text=":שלום! העתיקו את רשימת התלמידים מקובץ אקסל והדביקו אותם פה")
        instructions.pack()
        text_box = tk.Text(self.introduction_window, height=2, width=60)
        text_box.pack()
        text_box.focus()
        self.introduction_window.bind('<<Paste>>', lambda x: self.accept_clipboard_data())
        self.center_window(self.introduction_window)

    def accept_clipboard_data(self):
        if self.introduction_window is not None:
            self.introduction_window.destroy()
        self.parsed_data = self.clipboard_get().split('\n')
        self.parsed_data = [x.replace("\t", " ") for x in self.parsed_data if x != '']
        self.names_to_be_inserted()

    def names_to_be_inserted(self):
        self.names_to_be_inserted_win = tk.Toplevel()
        self.names_to_be_inserted_win.wm_title("אישור תלמידים")
        list_frame = tk.Frame(self.names_to_be_inserted_win)
        list_frame.grid(row=0, column=0, padx=20, pady=20)
        instructions_label = tk.Label(list_frame, text="?האם אלו הם התלמידים שתרצו לטעון")
        instructions_label.grid(column=0, row=0)
        list_box = tk.Listbox(list_frame, height = len(self.parsed_data))
        list_box.grid(column=2, row=1, rowspan=2)
        list_box.insert('end', *self.parsed_data)
        list_box.configure(justify='right')
        confirm_button = ttk.Button(list_frame, text="כן", command=self.update_confirmed_clipboard_data)
        confirm_button.grid(row=1, column=0)
        cancel_button = ttk.Button(list_frame, text="לא, אדביק מחדש", command=self.repaste_names)
        cancel_button.grid(row=2, column=0)
        self.names_to_be_inserted_win.geometry('400x' + str(len(self.parsed_data) * 18 + 90))
        self.center_window(self.names_to_be_inserted_win)

    def update_confirmed_clipboard_data(self):
        self.names_list_to_students()
        self.update_names_listbox()
        self.add_student_entry.delete(0, tk.END)
        self.names_to_be_inserted_win.destroy()
        self.lift()
        self.placeholder_foc_out()
        self.deiconify()

    def repaste_names(self):
        self.initialize_introduction_window()
        self.names_to_be_inserted_win.destroy()
        self.introduction_window.lift()

    def placeholder_foc_in(self):
        if self.add_student_entry.cget("foreground") == 'grey':
            self.add_student_entry.delete(0, 'end')
            self.add_student_entry.config({"fg": 'black'})

    def placeholder_foc_out(self):
        if self.add_student_entry.get() == '':
            self.add_student_entry.delete(0, 'end')
            self.add_student_entry.insert(0, 'תלמיד להוספה')
            self.add_student_entry.config({"fg": 'grey'})

    def manual_student_addition(self):
        if self.add_student_entry.get() is None:
            return
        else:
            self.students.append(Student(self.add_student_entry.get(),
                                         preferred_columns=list(self.optional_columns.values()),
                                         preferred_rows=list(self.optional_rows.values())))
            self.names_listbox.insert(tk.END, self.add_student_entry.get())
            self.add_student_entry.delete(0, tk.END)
            self.update_student_info_listboxes()

    def remove_student(self):
        if self.get_chosen_student() is None:
            return
        self.students.remove(self.get_chosen_student())
        self.update_names_listbox()
        self.update_student_info_listboxes()

    def remove_all_students(self):
        self.students = []
        self.update_names_listbox()
        self.update_student_info_listboxes()

    def get_chosen_student(self):
        if self.names_listbox.curselection() == ():
            return
        current_name_idx = self.names_listbox.curselection()[0]
        student_name = self.names_listbox.get(current_name_idx)
        for student in self.students:
            if student.name == student_name:
                return student
        raise ValueError(f"No student named {student_name}")

    def update_student_info_listboxes(self):
        if self.current_edited_student is None:
            return
        self.near_by_list.load_info(self.students_names_list(),
                                    self.current_edited_student.extract_near_by_names(),
                                    self.current_edited_student.name)
        self.eye_contact_list.load_info(self.students_names_list(),
                                        self.current_edited_student.extract_eye_contact_names(),
                                        self.current_edited_student.name)
        self.preferred_rows_list.load_info(list(self.optional_rows.keys()),
                                           self.current_edited_student.extract_rows_names(self.optional_rows)),
        self.preferred_columns_lists.load_info(list(self.optional_columns.keys()),
                                               self.current_edited_student.extract_column_names(self.optional_columns)),
        self.current_editing_label['text'] = "כרגע אתם עורכים את ההעדפות של " + self.current_edited_student.name

        if len(self.names_listbox.curselection()) > 0:
            current_name_idx = self.names_listbox.curselection()[0]
            for idx, name in enumerate(self.names_listbox.get(0, tk.END)):
                self.names_listbox.itemconfig(idx, {"bg": "#FFFFFF"})
            self.names_listbox.itemconfig(current_name_idx, {"bg": "grey"})

    def update_names_listbox(self):
        self.names_listbox.delete(0, tk.END)
        self.names_listbox.insert(tk.END, *self.students_names_list())
        self.names_listbox.selection_set(0)
        self.load_chosen_names()

    def names_list_to_students(self):
        if self.parsed_data is None:
            return
        for s in self.parsed_data:
            self.students.append(Student(s,
                                         preferred_columns=list(self.optional_columns.values()),
                                         preferred_rows=list(self.optional_rows.values())))
        self.parsed_data = None

    def load_chosen_names(self):
        self.current_edited_student = self.get_chosen_student()
        self.update_student_info_listboxes()

    @staticmethod
    def convert_row_names_to_numbers(l, d):
        return list(map(lambda x: d[x], l))

    @staticmethod
    def convert_row_numbers_to_names(l, d):
        return [x for x in list(d.keys()) if d[x] in l]

    def chosen_list_to_pointers(self, optionals_chosen_lists_object):
        chosen_names = optionals_chosen_lists_object.chosen_listbox.get(0, 'end')
        chosen_objects = [s for s in self.students if s.name in chosen_names]
        return chosen_objects

    def add_student_without_repetitions(self, original_list, list_to_merge):
        if isinstance(list_to_merge, Student):
            list_to_merge = [list_to_merge]
        original_names_list = [s.name for s in original_list]
        names_list_to_merge = [s.name for s in list_to_merge]
        final_names_list = list(set(original_names_list) | set(names_list_to_merge))
        students_list = [s for s in self.students if s.name in final_names_list]
        return students_list

    def mutual_relationship_sync(self, student):
        for s in student.near_by_students:
            s.near_by_students = self.add_student_without_repetitions(s.near_by_students, student)
        for s in student.eye_contact_students:
            s.eye_contact_students = self.add_student_without_repetitions(s.eye_contact_students, student)

    def update_current_student(self):
        if self.current_edited_student is None:
            return
        else:
            self.current_edited_student.near_by_students = self.chosen_list_to_pointers(self.near_by_list)
            self.current_edited_student.eye_contact_students = self.chosen_list_to_pointers(self.eye_contact_list)
            self.current_edited_student.preferred_rows = self.convert_row_names_to_numbers(
                self.preferred_rows_list.chosen_listbox.get(0, tk.END),
                self.optional_rows)
            self.current_edited_student.preferred_columns = self.convert_row_names_to_numbers(
                self.preferred_columns_lists.chosen_listbox.get(0, tk.END),
                self.optional_columns)
            self.mutual_relationship_sync(self.current_edited_student)

    @staticmethod
    def center_window(win):

        window_width = win.winfo_reqwidth()
        window_height = win.winfo_reqheight()

        position_right = int(win.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(win.winfo_screenheight() / 2 - window_height / 2)

        win.geometry("+{}+{}".format(position_right, position_down))

    def generate_seating_arrangement(self):
        self.seating_arrangement = SeatingArrangement(self.students, len(self.optional_rows.keys()), len(self.optional_columns.keys()))
        self.seating_arrangement.all_procedures_at_once()
