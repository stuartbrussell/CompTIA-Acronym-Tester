import csv
import tkinter as tk
import random
import time
import webbrowser

items = []
which_item = -1
the_item = None  # {'itemkey': '', 'itemvalue': '', 'itemlink': ''}


def load_items_from_csv():
    global all_items
    with open('A+ acronyms.csv') as acs:
        ad = csv.DictReader(acs)
        # acronyms: [{
        #   'itemkey':'TACACS',
        #   'itemvalue': 'Terminal Access Controller Access-Control System',
        #   'itemlink': '' | 'https://en.wikipedia.org/wiki/TACACS
        # }, ...]
        all_items = [item for item in ad]
    random.shuffle(all_items)


def toggle_value():
    global the_item
    if len(items) > 0 and not value_var.get():
        value_var.set(the_item['itemvalue'])
    else:
        value_var.set('')


def manual_entry(key):
    global the_item
    if win.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            the_item = acs[0]
            value_var.set(the_item['itemvalue'])
        else:
            value_var.set('')
    return True


def validate_ac_size(reason, new_size):
    global items, which_item, the_item
    if reason == 'key':
        return new_size.isdigit() or new_size == ''
    elif reason in ['focusout']:
        filter_items_and_show_first()
    return True


# build the filtered list of items and display the first one
def filter_items_and_show_first():
    global items, which_item, the_item
    size = ac_size_var.get()
    if size == '':
        items = list(all_items)
    else:
        items = list(filter(lambda item: len(
            item['itemkey']) == int(size), all_items))
    which_item = 0
    the_item = items[which_item] if len(items) > 0 else None
    show_key()


def show_key():
    win.focus_set()
    key_entry_var.set('')
    if the_item:
        key_entry_var.set(the_item['itemkey'])
    value_var.set('')
    cur_which_var.set(f"{which_item + 1} / {len(items)}")


def next_item(event):
    global which_item, the_item
    which_item += 1
    if which_item >= len(items):
        which_item = 0
    the_item = items[which_item]
    show_key()


def prev_item():
    global which_item, the_item
    if which_item <= 0:
        which_item = len(items) - 1
    else:
        which_item -= 1
    the_item = items[which_item]
    show_key()


def restart_test():
    load_items_from_csv()
    filter_items_and_show_first()


def open_description_in_browser():
    link = the_item['itemlink']
    if link:
        for alink in link.split("\n"):
            webbrowser.open(alink)


def win_evt(event):
    match event.keysym:
        case 'Right':
            next_item()
        case 'Left':
            prev_item()
        case 'space':
            toggle_value()


load_items_from_csv()
win = tk.Tk()
win.geometry('500x200+70+800')
key_entry_var = tk.StringVar()
key_entry = tk.Entry(textvariable=key_entry_var, font=(
    'Courier', '18'), justify=tk.CENTER, validatecommand=(win.register(manual_entry), '%P'), validate='key')
key_entry.grid(column=2)
value_var = tk.StringVar()
tk.Label(textvariable=value_var, justify=tk.CENTER,
         width=55).grid(column=1, columnspan=4, row=1)
tk.Button(text='Previous', command=prev_item).grid(column=1, row=2, sticky='e')
tk.Button(text='Toggle', command=toggle_value).grid(column=2, row=2)
tk.Button(text='Next', command=next_item).grid(column=3, row=2, sticky='w')
cur_which_var = tk.StringVar()
tk.Label(textvariable=cur_which_var).grid(column=2)
ac_size_var = tk.StringVar()
tk.Entry(textvariable=ac_size_var, justify=tk.CENTER,
         validatecommand=(win.register(validate_ac_size), '%V', '%P'), validate='all').grid(column=2)
filter_items_and_show_first()
# value_var.set(
#     'Completely Automated Turing Test To Tell Computers and Humans Apart')
tk.Button(text='Reload', command=restart_test).grid(
    row=6, column=1, sticky='e')
tk.Button(text='Browse', command=open_description_in_browser).grid(
    row=6, column=3, sticky='w')

win.bind('<Key>', win_evt)
win.mainloop()
