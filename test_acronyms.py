import csv
import tkinter as tk
import random
import sys
import webbrowser


class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        self.all_items = []
        self.items = []
        self.current_item_index = -1
        # {'itemkey': '', 'itemvalue': '', 'itemlink': ''}
        self.current_item = None
        self.manual_entry_mode_enabled = False

        # Keep a list of None/0/1 to note untried/incorrect/correct for each item.
        # The results list is the same length as the items list.
        self.results = []

        self.CORRECT = True
        self.INCORRECT = False
        self.UNTESTED = None

        # set window size and center window on screen
        window_width = 500
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_ul_x = int(screen_width/2 - window_width/2)
        window_ul_y = int(screen_height/2 - window_height/2)
        self.geometry(f"{window_width}x{
                      window_height}+{window_ul_x}+{window_ul_y}")

        # Do this before creating any menus
        self.option_add('*tearOff', False)

        # Row 0
        self.acronym_length_var = tk.IntVar()
        self.length_menu = self.create_length_menu()
        self.length_menu.grid(row=0, column=1)

        self.key_entry_var = tk.StringVar()
        self.key_entry = tk.Entry(textvariable=self.key_entry_var, font=(
            'Courier', '18'), justify=tk.CENTER, validatecommand=(self.register(self.manual_entry), '%P'), validate='key')
        self.key_entry.grid(row=0, column=2)
        self.cur_which_var = tk.StringVar()
        tk.Label(textvariable=self.cur_which_var).grid(
            row=0, column=3, sticky='w')

        # Row 1
        self.itemvalue_var = tk.StringVar()
        tk.Label(textvariable=self.itemvalue_var, justify=tk.CENTER,
                 width=55).grid(row=1, column=1, columnspan=4)

        # Row 2
        previous_btn = tk.Button(text='Previous', command=self.prev_item)
        previous_btn.grid(row=2, column=1, sticky='e')
        tk.Button(text='Toggle', command=self.toggle_itemvalue).grid(
            row=2, column=2)
        tk.Button(text='Next', command=self.next_item).grid(
            row=2, column=3, sticky='w')

        # Row 3
        self.score_var = tk.StringVar()
        tk.Label(textvariable=self.score_var).grid(row=3, column=2)
        self.score_var.set('Score: ')
        self.correct_answer_var = tk.BooleanVar(value=self.CORRECT)
        self.correct_answer_btn = tk.Checkbutton(
            text='Correct', variable=self.correct_answer_var, command=self.toggle_correct_answer)
        self.correct_answer_btn.grid(
            row=3, column=3, sticky='w')

        # Row 4
        tk.Button(text='Reload', command=self.restart_test).grid(
            row=4, column=1, sticky='e')
        self.review_mode_var = tk.BooleanVar(value=False)
        self.review_mode_btn = tk.Checkbutton(
            text='Review Mode', variable=self.review_mode_var, command=self.toggle_review_mode)
        self.review_mode_btn.grid(row=4, column=2)
        tk.Button(text='Browse', command=self.open_description_in_browser).grid(
            row=4, column=3, sticky='w')

        self.restart_test()

        # test the longest string
        # self.itemvalue_var.set(
        #     'Completely Automated Turing Test To Tell Computers and Humans Apart')

        self.bind('<Key>', self.win_evt)

    def load_items_from_csv(self):
        with open('A+ acronyms.csv') as acs:
            # acronyms: [{
            #   'itemkey':'TACACS',
            #   'itemvalue': 'Terminal Access Controller Access-Control System',
            #   'itemlink': '' | 'https://en.wikipedia.org/wiki/TACACS
            # }, ...]
            self.all_items = [item for item in csv.DictReader(acs)]
        random.shuffle(self.all_items)

    def scan_items_for_acronym_lengths(self):
        # Scan all_items and make a list of acronym lengths
        length_options = [0]
        for item in self.all_items:
            length = len(item['itemkey'])
            if length not in length_options:
                length_options.append(length)
        return sorted(length_options)

    def create_length_menu(self):
        length_options = self.scan_items_for_acronym_lengths()
        menu = tk.OptionMenu(self, self.acronym_length_var, *length_options,
                             command=self.acronym_length_changed)
        return menu

    def update_length_menu(self):
        length_options = self.scan_items_for_acronym_lengths()
        menu = self.length_menu['menu']
        menu.delete(0, 'end')

        def notify_change(value):
            self.acronym_length_var.set(value)
            self.acronym_length_changed(value)

        for option in length_options:
            menu.add_command(label=option,
                             command=lambda value=option: notify_change(value))

        # Try to keep the same choice
        if self.acronym_length_var.get() not in length_options:
            self.acronym_length_var.set(0)

    def toggle_itemvalue(self):
        if len(self.items) > 0 and not self.itemvalue_var.get():
            self.itemvalue_var.set(self.current_item['itemvalue'])
        else:
            self.itemvalue_var.set('')
        self.focus_set()

    def manual_entry(self, key):
        # A hacky way to try out a specific key. It does not affect the current
        # index. Prev/Next will continue as if the manual entry did not occur.
        # Press esc to exit manual entry mode.
        if self.focus_get() == self.key_entry:
            self.set_manual_entry_mode(True)
            acs = list(
                filter(lambda item: item['itemkey'].upper() == key.upper(), self.items))
            if len(acs) > 0:
                item = acs[0]
                self.itemvalue_var.set(item['itemvalue'])
                self.current_item = item
            else:
                self.itemvalue_var.set(' ')
        return True

    def set_manual_entry_mode(self, enabled):
        self.manual_entry_mode_enabled = enabled
        if enabled:
            self.correct_answer_btn.config(state=tk.DISABLED)
        else:
            self.correct_answer_btn.config(state=tk.ACTIVE)
            self.set_current_item(self.items[self.current_item_index])

    def acronym_length_changed(self, _new_length):
        self.filter_items_and_show_first()

    def filter_items_and_show_first(self):
        # build the filtered list of items and display the first one
        length = self.acronym_length_var.get()
        if length == 0:
            self.items = list(self.all_items)
        else:
            self.items = list(filter(lambda item: len(
                item['itemkey']) == length, self.all_items))
        self.set_current_item_index(0)
        self.reset_score()
        self.show_itemkey()

    def show_itemkey(self):
        self.focus_set()
        self.key_entry_var.set('')
        if self.current_item:
            self.key_entry_var.set(self.current_item['itemkey'])
        self.itemvalue_var.set('')
        self.cur_which_var.set(
            f"{self.current_item_index + 1} / {len(self.items)}")
        self.show_score()

    def next_item(self):
        self.set_manual_entry_mode(False)
        self.update_current_item_result()

        if self.review_mode_var.get():
            index = self.get_next_incorrect_index(self.current_item_index)
            if index is not None:
                self.set_current_item_index(index)
        else:
            self.set_current_item_index(self.current_item_index + 1)\

        self.update_correct_answer_checkbox()
        self.show_itemkey()

    def prev_item(self):
        self.set_manual_entry_mode(False)
        if self.review_mode_var.get():
            index = self.get_prev_incorrect_index(self.current_item_index)
            if index is not None:
                self.set_current_item_index(index)
        else:
            self.set_current_item_index(self.current_item_index - 1)
            self.update_correct_answer_checkbox()

        self.show_itemkey()

    def get_next_incorrect_index(self, cur_index):
        try:
            found_index = self.results.index(self.INCORRECT, cur_index + 1)
        except (ValueError, IndexError):
            try:
                found_index = self.results.index(self.INCORRECT, 0)
            except ValueError:
                found_index = None
        return found_index

    def get_prev_incorrect_index(self, cur_index):
        try:
            results_rev = self.results[-1::-1]
            starting_index = len(results_rev) - cur_index
            found_index = results_rev.index(self.INCORRECT,  starting_index)
        except (ValueError, IndexError) as e:
            try:
                found_index = results_rev.index(self.INCORRECT, 0)
            except ValueError:
                found_index = None
        if found_index is not None:
            found_index = len(results_rev) - found_index - 1
        return found_index

    def restart_test(self):
        self.load_items_from_csv()
        self.update_length_menu()
        self.filter_items_and_show_first()
        self.update_correct_answer_checkbox()

    def open_description_in_browser(self):
        link = self.current_item['itemlink']
        if link:
            for alink in link.split("\n"):
                webbrowser.open(alink)

    def show_score(self):
        correct_count = self.results.count(self.CORRECT)
        incorrect_count = self.results.count(self.INCORRECT)
        self.score_var.set(
            f"Correct: {correct_count}   Incorrect: {incorrect_count}")

    def set_current_item_index(self, value):
        self.current_item_index = value
        if self.current_item_index >= len(self.items):
            self.current_item_index = 0
        elif self.current_item_index < 0:
            self.current_item_index = len(self.items) - 1

        try:
            self.set_current_item(self.items[self.current_item_index])
        except:
            self.set_current_item(None)

    def set_current_item(self, item):
        self.current_item = item
        self.show_itemkey()

    def update_current_item_result(self):
        self.results[self.current_item_index] = self.CORRECT if self.correct_answer_var.get(
        ) else self.INCORRECT
        if self.INCORRECT in self.results:
            self.review_mode_btn.config(state=tk.ACTIVE)
        else:
            self.reset_review_mode()
        self.show_score()

    def update_correct_answer_checkbox(self):
        # Item result defaults to CORRECT unless it is already INCORRECT
        current_result = self.results[self.current_item_index] if len(
            self.results) > 0 else self.UNTESTED
        self.correct_answer_var.set(self.INCORRECT if current_result ==
                                    self.INCORRECT else self.CORRECT)

    def toggle_review_mode(self):
        is_review_mode = self.review_mode_var.get()
        first_incorrect_index = self.get_next_incorrect_index(-1)
        if first_incorrect_index is not None:
            self.set_current_item_index(first_incorrect_index)
            self.correct_answer_var.set(self.INCORRECT)

    def reset_review_mode(self):
        self.review_mode_var.set(False)
        self.review_mode_btn.config(state=tk.DISABLED)

    def reset_score(self):
        self.results = [self.UNTESTED] * len(self.items)
        self.reset_review_mode()
        self.update_correct_answer_checkbox()
        self.show_score()

    def toggle_correct_answer(self, update_var=False):
        if update_var:
            # Only do this if the command is NOT called from the checkbutton.
            # The checkbutton already sets the var.
            self.correct_answer_var.set(self.INCORRECT if self.correct_answer_var.get()
                                        == self.CORRECT else self.CORRECT)
        self.update_current_item_result()

    def win_evt(self, event):
        match event.keysym:
            case 'Right' | 'Down':
                self.next_item()
            case 'Left' | 'Up':
                self.prev_item()
            case 'space':
                self.toggle_itemvalue()
            case 'Escape':
                if self.manual_entry_mode_enabled:
                    self.set_manual_entry_mode(False)
                else:
                    self.toggle_correct_answer(update_var=True)


if __name__ == "__main__":
    root = Root()
    root.mainloop()
