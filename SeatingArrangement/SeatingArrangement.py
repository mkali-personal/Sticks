import numpy as np
from pandas import DataFrame
from subprocess import Popen
from tkinter import filedialog


class SeatingArrangement:
    def __init__(self, students, rows, columns):
        self.students = students
        self.classroom = np.zeros((rows, columns * 2))
        self.columns = columns
        self.rows = rows
        self.current_seat_choice = None

    @staticmethod
    def table_cols2seat_cols(table_cols):
        seat_cols = []
        for c in table_cols:
            seat_cols.extend([c * 2, (c * 2) + 1])
        return seat_cols

    @staticmethod
    def seat_col2double_seat_cols(seat_col):
        if seat_col % 2 == 0:
            double_seat_cols = [seat_col, seat_col + 1]
        else:
            double_seat_cols = [seat_col - 1, seat_col]
        return double_seat_cols

    def prioritize_students(self):
        for s in self.students:
            s.rank_self()
        self.students.sort(key=lambda x: x.num_of_constraints, reverse=True)
        for i, student in enumerate(self.students):
            student.id = i + 1
            student.preferred_columns = self.table_cols2seat_cols(student.preferred_columns)

    @staticmethod
    def remove_surrounding_seats(available_seats, center_seat):
        forbidden_rows = np.logical_and(available_seats[0] >= center_seat[0] - 1,
                                        available_seats[0] <= center_seat[0] + 1)

        forbidden_columns = np.logical_and(available_seats[1] >= center_seat[1] - 1,
                                           available_seats[1] <= center_seat[1] + 1)

        return available_seats[:, ~np.logical_and(forbidden_rows, forbidden_columns)]

    def remove_surrounding_table_columns(self, available_seats, center_seat):
        table_col = self.seat_col2double_seat_cols(center_seat[1])

        return available_seats[:, np.isin(available_seats[1], table_col)]

    @staticmethod
    def choose_random_seat(available_seats):
        return available_seats[:, np.random.randint(available_seats.shape[1])]

    @staticmethod
    def filter_forbidden_lines(available_seats, forbidden_lines, axis):
        return available_seats[:, np.isin(available_seats[axis], forbidden_lines)]

    # Ask Asaf about static methods issue
    def try_to_proceed(self, available_seats, available_seats_temp):
        if available_seats_temp.shape[1] == 0:
            self.current_seat_choice = self.choose_random_seat(available_seats)
        return available_seats_temp

    def place_student(self):
        for student in self.students:
            self.current_seat_choice = None
            available_seats = np.array(np.where(self.classroom == 0))
            # If the students has no constraints just put it in the first seat available:
            if student.num_of_constraints == (self.columns + self.rows) * (-8):
                self.current_seat_choice = available_seats[:, 0]
            else:
                available_seats_temp = self.filter_forbidden_lines(available_seats, student.preferred_columns, 1)
                available_seats = self.try_to_proceed(available_seats, available_seats_temp)
                if self.current_seat_choice is None:
                    available_seats_temp = self.filter_forbidden_lines(available_seats, student.preferred_rows, 0)
                    available_seats = self.try_to_proceed(available_seats, available_seats_temp)
                for s in student.near_by_students:
                    if s.seat is not None and self.current_seat_choice is not None:
                        available_seats_temp = self.remove_surrounding_seats(available_seats, s.seat)
                        available_seats = self.try_to_proceed(available_seats, available_seats_temp)
                for s in student.eye_contact_students:
                    if s.seat is not None and self.current_seat_choice is not None:
                        available_seats_temp = self.remove_surrounding_seats(available_seats, s.seat)
                        available_seats_temp = self.remove_surrounding_table_columns(available_seats_temp, s.seat)
                        available_seats = self.try_to_proceed(available_seats, available_seats_temp)
                if self.current_seat_choice is None:
                    self.current_seat_choice = available_seats[:, np.random.randint(available_seats.shape[1])]
            self.classroom[self.current_seat_choice[0], self.current_seat_choice[1]] = student.id
        print('all set')

    def insert_dummy_col_rows(self):
        a = np.insert(self.classroom, range(2, self.classroom.shape[1], 2), -1, axis=1)
        a = np.insert(a, range(1, a.shape[0], 1), -1, axis=0)
        return a

    def convert_ids_to_names(self, export_classroom):
        ids_to_names = {}
        ids_to_names[0] = 'כיסא ריק'
        ids_to_names[-1] = ''
        for s in self.students:
            ids_to_names[s.id] = s.name
        names_classroom = np.vectorize(ids_to_names.get)(export_classroom)

        return names_classroom

    def generate_export_classroom(self):
        export_classroom = self.insert_dummy_col_rows()
        export_classroom = self.convert_ids_to_names(export_classroom)
        export_classroom = np.insert(export_classroom, 0, 'לוח', axis=0)

        return export_classroom

    def generate_csv(self):
        export_classroom = self.generate_export_classroom()
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if path is None:
            return
        df = DataFrame(export_classroom)
        df.to_excel(path)  # , encoding='utf-8'
        # np.savetxt(path, export_classroom, encoding='iso8859_8') # , fmt='%s'
        Popen(path, shell=True)

    def all_procedures_at_once(self):
        self.prioritize_students()
        self.place_student()
        self.generate_csv()
