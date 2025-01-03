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

        self.protocol('WM_DELETE_WINDOW', master.toggle_debug_mode)

        # Capture all unfocused keystrokes.
        self.bind('<Key>', self.win_evt)

    def print_duplicate_acronyms(self):
        print('debug_print_duplicate_acronyms')
        for item in self.master.all_items:
            if len(item['itemvalues']) > 1:
                print(item)

    def win_evt(self, event):
        print(event)
        match event.keysym:
            case 'question':
                self.master.toggle_debug_mode()
