import re

class LyxParser:
    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name, encoding="utf8") as file:
            self.file_text = file.read()
        self.no_extension_pattern = re.compile('(.*)\.lyx')
        self.backup_text = '_backup.lyx'
        self.begin_graphics_pattern = r'\\begin_inset Graphics'
        self.resized_graphics_pattern = r'\\begin_inset Graphics\n	width 65col%'

    def create_parsed_file(self):
        # Create a second file in the same directory with the theorems list at the buttom
        file_name_no_extension = self.no_extension_pattern.match(self.file_name)
        new_file_name = file_name_no_extension.group(1) + self.backup_text
        with open(new_file_name, 'w', encoding="utf8") as new_file:
            new_file.write(self.file_text)
        file_resized = self.resize_images(self.file_text)
        with open(self.file_name, 'w', encoding="utf8") as new_file:
            new_file.write(file_resized)



    def resize_images(self, text: str):
        # Creates a text variable of the edited file:

        replaced_text = re.sub(self.begin_graphics_pattern, self.resized_graphics_pattern, text)
        return replaced_text


try:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
except ModuleNotFoundError:
    file_path = input('Lyx File Path: ')

L = LyxParser(file_path)
L.create_parsed_file()
