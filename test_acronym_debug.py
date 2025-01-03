import tkinter as tk


class DebugWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__()

        self.master = master
        self.title('acronym tester debugger')

        # set window size and near to master window
        window_width = 500
        window_height = 200
        window_ul_x = master.winfo_rootx()
        window_ul_y = master.winfo_rooty() - 300
        self.geometry(f"{window_width}x{
                      window_height}+{window_ul_x}+{window_ul_y}")

        # Row 0
        tk.Button(self, text='Print Duplicate Acronyms',
                  command=self.print_duplicate_acronyms).grid()

        tk.Button(self, text='Print Trailing Spaces',
                  command=self.print_trailing_spaces).grid()

        self.protocol('WM_DELETE_WINDOW', master.toggle_debug_mode)

        # Capture all unfocused keystrokes.
        self.bind('<Key>', self.win_evt)

    def print_duplicate_acronyms(self):
        print('print_duplicate_acronyms')
        all_sorted = sorted(self.master.all_items,
                            key=lambda item: item['itemkey'])
        for item in all_sorted:
            if len(item['itemvalues']) > 1:
                print(item)

    def print_trailing_spaces(self):
        print('print_trailing_spaces')
        all_sorted = sorted(self.master.all_items,
                            key=lambda item: item['itemkey'])
        for item in all_sorted:
            if item['itemkey'][-1] == ' ':
                print(item)
            for value in item['itemvalues']:
                if value[-1] == ' ':
                    print(item)
            for link in item['itemlinks']:
                if link[-1] == ' ':
                    print(item)

    def win_evt(self, event):
        match event.keysym:
            case 'question':
                self.master.toggle_debug_mode()
