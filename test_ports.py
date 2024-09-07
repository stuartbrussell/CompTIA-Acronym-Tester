import csv
import tkinter as tk
import random

with open('flashcards/A+ ports.csv') as acs:
    ad = csv.DictReader(acs)
    # acronyms: [{'itemkey':'AC', 'itemvalue': 'Alternating Current'}, ...]
    all_items = [item for item in ad]
random.shuffle(all_items)

items = []
which_item = -1


def toggle_value():
    if len(items) > 0 and not value_var.get():
        value_var.set(items[which_item]['itemvalue'])
    else:
        value_var.set('')


def manual_entry(key):
    if win.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            value_var.set(acs[0]['itemvalue'])
        else:
            value_var.set('')
    return True


def set_ac_size(new_size):
    global items
    global which_item
    if new_size.isdigit():
        size = int(new_size)
        items = list(filter(lambda item: len(
            item['itemkey']) == size, all_items))
    else:
        items = list(all_items)
    which_item = 0
    show_key()
    return True


def show_key():
    win.focus_set()
    key_entry_var.set('')
    if len(items):
        key_entry_var.set(items[which_item]['itemkey'])
    value_var.set('')
    cur_which_var.set(f"{which_item} / {len(items)}")


def next_item():
    global which_item
    which_item += 1
    if which_item >= len(items):
        which_item = 0
    show_key()


def prev_item():
    global which_item
    if which_item <= 0:
        which_item = len(items) - 1
    else:
        which_item -= 1
    show_key()


def win_evt(event):
    match event.keysym:
        case 'Right':
            next_item()
        case 'Left':
            prev_item()
        case 'space':
            toggle_value()


win = tk.Tk()
# middle of large monitor: 1500+700
win.geometry('460x200+1500+700')
key_entry_var = tk.StringVar()
key_entry = tk.Entry(textvariable=key_entry_var, font=(
    'Courier', '18'), justify=tk.CENTER, validatecommand=(win.register(manual_entry), '%P'), validate='key')
key_entry.grid(column=2)
value_var = tk.StringVar()
tk.Label(textvariable=value_var, justify=tk.CENTER,
         width=50).grid(column=1, columnspan=4, row=1)
tk.Button(text='Previous', command=prev_item).grid(column=1, row=2, sticky='e')
tk.Button(text='Toggle', command=toggle_value).grid(column=2, row=2)
tk.Button(text='Next', command=next_item).grid(column=3, row=2, sticky='w')
cur_which_var = tk.StringVar()
tk.Label(textvariable=cur_which_var).grid(column=2)
ac_size_var = tk.StringVar()
ac_size_var.set('')
tk.Entry(textvariable=ac_size_var, justify=tk.CENTER,
         validatecommand=(win.register(set_ac_size), '%P'), validate='key').grid(column=2)
set_ac_size('')

win.bind('<Key>', win_evt)
win.mainloop()

# win = tk.Tk()
# win.geometry('800x200+1000+500')
# win.columnconfigure(0, minsize=800)
# key_entry_var = tk.StringVar()
# key_entry = tk.Entry(textvariable=key_entry_var, font=(
#     'Courier', '18'), justify=tk.CENTER, validatecommand=(win.register(manual_entry), '%P'), validate='key')
# key_entry.grid()
# value_var = tk.StringVar()
# value = tk.Label(textvariable=value_var)
# value.grid()
# next = tk.Button(text='Next', command=next_item, padx=100)
# next.grid()
# next = tk.Button(text='Previous', command=prev_item, padx=100)
# next.grid()
# toggle = tk.Button(text='Toggle', command=toggle_value, padx=100)
# toggle.grid()
# cur_which_var = tk.StringVar()
# cur_which = tk.Label(textvariable=cur_which_var)
# cur_which.grid()
# ac_size_var = tk.StringVar()
# ac_size_var.set('')
# ac_size = tk.Entry(textvariable=ac_size_var, justify=tk.CENTER,
#                    validatecommand=(win.register(set_ac_size), '%P'), validate='key')
# ac_size.grid()
# set_ac_size('')

# win.mainloop()
