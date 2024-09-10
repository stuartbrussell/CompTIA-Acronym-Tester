import csv
import tkinter as tk
import random
import sys
import webbrowser

items = []
which_item = -1
the_item = None  # {'itemkey': '', 'itemvalue': '', 'itemlink': ''}

# keep a list of 0/1 to note incorrect/correct for each item
scores = []


def load_items_from_csv():
    global all_items
    with open('A+ acronyms.csv') as acs:
        # acronyms: [{
        #   'itemkey':'TACACS',
        #   'itemvalue': 'Terminal Access Controller Access-Control System',
        #   'itemlink': '' | 'https://en.wikipedia.org/wiki/TACACS
        # }, ...]
        all_items = [item for item in csv.DictReader(acs)]
    random.shuffle(all_items)


def create_length_menu(length_choice):
    # Scan all_items and make a list of acronym lengths
    length_options = [0]
    for item in all_items:
        length = len(item['itemkey'])
        if length not in length_options:
            length_options.append(length)
    length_options = sorted(length_options)
    length_menu = tk.OptionMenu(root, length_choice, *length_options,
                                command=acronym_length_changed)
    return length_menu


def toggle_value():
    global the_item
    if len(items) > 0 and not value_var.get():
        value_var.set(the_item['itemvalue'])
    else:
        value_var.set('')


def manual_entry(key):
    global the_item
    if root.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            the_item = acs[0]
            value_var.set(the_item['itemvalue'])
        else:
            value_var.set('')
    return True


def acronym_length_changed(_new_length):
    filter_items_and_show_first()


def filter_items_and_show_first():
    # build the filtered list of items and display the first one
    global items, which_item, the_item
    length = acronym_length_choice.get()
    if length == 0:
        items = list(all_items)
    else:
        items = list(filter(lambda item: len(
            item['itemkey']) == length, all_items))
    which_item = 0
    reset_score()
    the_item = items[which_item] if len(items) > 0 else None
    show_key()


def show_key():
    root.focus_set()
    key_entry_var.set('')
    if the_item:
        key_entry_var.set(the_item['itemkey'])
    value_var.set('')
    cur_which_var.set(f"{which_item + 1} / {len(items)}")
    show_score()


def next_item():
    global which_item, the_item
    which_item += 1
    if which_item >= len(items):
        which_item = 0
    the_item = items[which_item]

    # append a score based on checkbox value
    append_score()

    correct_answer.set(True)  # new items default to correct

    show_key()


def prev_item():
    global which_item, the_item
    if which_item <= 0:
        which_item = len(items) - 1
    else:
        which_item -= 1
    the_item = items[which_item]

    # remove the last score
    pop_score()

    show_key()


def restart_test():
    load_items_from_csv()
    filter_items_and_show_first()


def open_description_in_browser():
    link = the_item['itemlink']
    if link:
        for alink in link.split("\n"):
            webbrowser.open(alink)


def show_score():
    correct_count = sum(scores)
    incorrect_count = which_item - correct_count
    incorrect_count = scores.count(0)
    score_var.set(
        f"Correct: {correct_count}   Incorrect: {incorrect_count}")


def append_score():
    scores.append(correct_answer.get())
    show_score()


def pop_score():
    try:
        scores.pop()
    except:
        pass
    show_score()


def reset_score():
    scores.clear()
    show_score()


def toggle_correct_answer():
    correct_answer.set(not correct_answer.get())


def win_evt(event):
    match event.keysym:
        case 'Right':
            next_item()
        case 'Left':
            prev_item()
        case 'space':
            toggle_value()
        case 'Escape':
            toggle_correct_answer()


load_items_from_csv()
root = tk.Tk()
root.geometry('500x200+2500+1100')

# Do this before creating any menus
root.option_add('*tearOff', False)

# Row 0
acronym_length_choice = tk.IntVar()
length_menu = create_length_menu(acronym_length_choice)
length_menu.grid(row=0, column=1)

key_entry_var = tk.StringVar()
key_entry = tk.Entry(textvariable=key_entry_var, font=(
    'Courier', '18'), justify=tk.CENTER, validatecommand=(root.register(manual_entry), '%P'), validate='key')
key_entry.grid(row=0, column=2)
cur_which_var = tk.StringVar()
tk.Label(textvariable=cur_which_var).grid(row=0, column=3, sticky='w')

# Row 1
value_var = tk.StringVar()
tk.Label(textvariable=value_var, justify=tk.CENTER,
         width=55).grid(row=1, column=1, columnspan=4)

# Row 2
tk.Button(text='Previous', command=prev_item).grid(row=2, column=1, sticky='e')
tk.Button(text='Toggle', command=toggle_value).grid(row=2, column=2)
tk.Button(text='Next', command=next_item).grid(row=2, column=3, sticky='w')

# Row 3
score_var = tk.StringVar()
tk.Label(textvariable=score_var).grid(row=3, column=2)
score_var.set('Score: ')
correct_answer = tk.BooleanVar(value=True)
tk.Checkbutton(text='Correct', variable=correct_answer).grid(
    row=3, column=3, sticky='w')

# Row 4
tk.Button(text='Reload', command=restart_test).grid(
    row=4, column=1, sticky='e')
tk.Button(text='Browse', command=open_description_in_browser).grid(
    row=4, column=3, sticky='w')

filter_items_and_show_first()

# test the longest string
# value_var.set(
#     'Completely Automated Turing Test To Tell Computers and Humans Apart')

root.bind('<Key>', win_evt)
root.mainloop()
