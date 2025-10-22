import tkinter as tk


class DebugWindow(tk.Toplevel):
    def __init__(self, master, all_csv_file_names, current_cvs_file_names, enable_csv_file, current_strict_mode, set_strict_mode):
        super().__init__()

        self.master = master
        self.enable_csv_file = enable_csv_file
        self.strict_mode = current_strict_mode
        self.set_strict_mode = set_strict_mode
        self.title('Acronym Tester Debugger')

        # set window size and near to master window
        window_width = 500
        window_height = 200
        window_ul_x = master.winfo_rootx()
        window_ul_y = master.winfo_rooty() - 300
        self.geometry(f"{window_width}x{
                      window_height}+{window_ul_x}+{window_ul_y}")

        # Column 0
        tk.Button(self, text='Print Duplicate Acronyms',
                  command=self.print_duplicate_acronyms).grid(row=0, column=0)

        tk.Button(self, text='Print Trailing Spaces',
                  command=self.print_trailing_spaces).grid(row=1, column=0)

        strict_mode_cb = tk.Checkbutton(self, text='Strict Mode')
        strict_mode_cb.bind('<ButtonRelease>', self.strict_mode_checked)
        strict_mode_cb.grid(row=2, column=0, sticky='w')
        strict_mode_cb.select() if current_strict_mode else strict_mode_cb.deselect()

       # Column 1
        for i in range(len(all_csv_file_names)):
            file_name = all_csv_file_names[i]
            btn = tk.Checkbutton(self, text=file_name)
            btn.bind('<ButtonRelease>', self.csv_file_checked)
            btn.grid(row=i, column=1, sticky='w')

            # When the window opens, pre-set each checkbox to match current.
            is_current = file_name in current_cvs_file_names
            btn.select() if is_current else btn.deselect()

        # When the user closes this window, tell our owner.
        self.protocol('WM_DELETE_WINDOW', master.toggle_debug_mode)

        # Capture all unfocused keystrokes.
        self.bind('<Key>', self.win_evt)

    def csv_file_checked(self, event):
        csv_file_name = event.widget.cget('text')
        # the event contains the state _before_ the widget was clicked
        enabled = '0' == event.widget.getvar(
            event.widget.cget('variable'))
        self.enable_csv_file(csv_file_name, enabled)

    def strict_mode_checked(self, event):
        # the event contains the state _before_ the widget was clicked
        use_strict_mode = '0' == event.widget.getvar(
            event.widget.cget('variable'))
        self.set_strict_mode(use_strict_mode)

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
                if len(link) > 0 and link[-1] == ' ':
                    print(item)

    def win_evt(self, event):
        match event.keysym:
            case 'question':
                self.master.toggle_debug_mode()
