import tkinter as tk


class OptionalsChosenLists(tk.Frame):
    def __init__(self, parent, optionals_header, chosen_header, reversed_direction=False, warning_above_one=False):
        tk.Frame.__init__(self, parent)
        if reversed_direction is False:
            chosen_column = 1
            optionals_column = 3
        else:
            chosen_column = 3
            optionals_column = 1
        self.warning_above_one = warning_above_one
        self.above_one_warning_win = None
        self.full_optionals_names = None

        self.optionals_label = tk.Label(self, text=":"+optionals_header)
        self.optionals_label.grid(column=optionals_column, row=0)

        self.optionals_listbox = tk.Listbox(self)
        self.optionals_listbox.bind('<Double-1>', lambda x: self.add_name())
        self.optionals_listbox.bind('<Return>', lambda x: self.add_name())
        self.optionals_listbox.grid(column=optionals_column, row=1, padx=7, pady=7)
        self.optionals_listbox.configure(justify='right')
        self.attach_scrollbar_to_widget(self, self.optionals_listbox)

        self.chosen_label = tk.Label(self, text=":"+chosen_header)
        self.chosen_label.grid(column=chosen_column, row=0, padx=7, pady=7)

        self.chosen_listbox = tk.Listbox(self)
        self.chosen_listbox.bind('<Double-1>', lambda x: self.remove_name())
        self.chosen_listbox.bind('<Delete>', lambda x: self.remove_name())
        self.chosen_listbox.grid(column=chosen_column, row=1, padx=7, pady=7)
        self.chosen_listbox.configure(justify='right')
        self.attach_scrollbar_to_widget(self, self.optionals_listbox)

    @staticmethod
    def attach_scrollbar_to_widget(parent, widget):
        widget_row = widget.grid_info()['row']
        widget_column = widget.grid_info()['column']
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.config(command=widget.yview)
        scrollbar.grid(column=widget_column-1, row=widget_row, sticky=tk.N + tk.S)
        widget.config(yscrollcommand=scrollbar.set)

    def load_info(self, optionals, chosen=[], current=None):
        self.full_optionals_names = optionals

        remove_from_optionals = chosen.copy()
        if current is not None:
            remove_from_optionals.append(current)
        optionals_filtered = [s for s in self.full_optionals_names if s not in remove_from_optionals]

        self.optionals_listbox.delete(0, 'end')
        self.optionals_listbox.insert(tk.END, *optionals_filtered)

        self.chosen_listbox.delete(0, 'end')
        self.chosen_listbox.insert(tk.END, *chosen)

    @staticmethod
    def add_item_to_list(originals_list, current_list, item):
        current_list.append(item)
        return [x for x in originals_list if x in current_list]

    def above_one_warning(self):
        self.above_one_warning_win = tk.Toplevel()
        self.above_one_warning_win.wm_title("!שים לב")
        warning = tk.Label(self.above_one_warning_win, text='מומלץ שלא להכניס יותר מתלמיד אחד\nאיתו אסור ליצור קשר עין')
        warning.grid(column=0, row=0, padx=10, pady=10)
        button = tk.Button(self.above_one_warning_win, text='הבנתי', command=self.above_one_warning_win.destroy)
        button.grid(column=0, row=1, padx=10, pady=10)
        self.above_one_warning_win.lift()

    def add_name(self):
        current_name_idx = self.optionals_listbox.curselection()[0]
        name_to_add = self.optionals_listbox.get(current_name_idx)
        updated_list = self.add_item_to_list(self.full_optionals_names,
                                             list(self.chosen_listbox.get(0, tk.END)),
                                             name_to_add)
        if self.warning_above_one:
            if len(self.chosen_listbox.get(0, tk.END)) > 0:
                self.above_one_warning()
        self.chosen_listbox.delete(0, 'end')
        self.chosen_listbox.insert(tk.END, *updated_list)

        self.optionals_listbox.delete(current_name_idx)

    def remove_name(self):
        index = self.chosen_listbox.curselection()[0]
        self.chosen_listbox.delete(index)
        new_optionals_values = [s for s in self.full_optionals_names if s not in self.chosen_listbox.get(0, 'end')]
        self.optionals_listbox.delete(0, 'end')
        self.optionals_listbox.insert('end', *new_optionals_values)
