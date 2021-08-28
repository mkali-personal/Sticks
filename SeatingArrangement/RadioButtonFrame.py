import tkinter as tk


class RadioButtonFrame(tk.Frame):
    def __init__(self, parent, values_list, label):
        tk.Frame.__init__(self, parent)
        row_label = tk.Label(self, text=label)
        row_label.grid(row=0, column=0)

        self.result = tk.IntVar()
        self.result.set(values_list[0])

        for i, value in enumerate(values_list):
            tk.Radiobutton(self, text=str(value), variable=self.result, value=value).grid(row=i+1, column=0)
