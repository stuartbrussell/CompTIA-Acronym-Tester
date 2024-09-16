import csv
import tkinter as tk
import random
import sys
import webbrowser

items = []
which_item = -1
current_item = None  # {'itemkey': '', 'itemvalue': '', 'itemlink': ''}

# Keep a list of None/0/1 to note untried/incorrect/correct for each item.
# The results list is the same length as the items list.
results = []

CORRECT = True
INCORRECT = False
UNTESTED = None


def load_items_from_csv():
    global all_items, results
    with open('A+ acronyms.csv') as acs:
        # acronyms: [{
        #   'itemkey':'TACACS',
        #   'itemvalue': 'Terminal Access Controller Access-Control System',
        #   'itemlink': '' | 'https://en.wikipedia.org/wiki/TACACS
        # }, ...]
        all_items = [item for item in csv.DictReader(acs)]
    random.shuffle(all_items)


def scan_items_for_acronym_lengths():
    # Scan all_items and make a list of acronym lengths
    length_options = [0]
    for item in all_items:
        length = len(item['itemkey'])
        if length not in length_options:
            length_options.append(length)
    return sorted(length_options)


def create_length_menu():
    length_options = scan_items_for_acronym_lengths()
    menu = tk.OptionMenu(root, acronym_length_var, *length_options,
                         command=acronym_length_changed)
    return menu


def update_length_menu():
    length_options = scan_items_for_acronym_lengths()
    menu = length_menu['menu']
    menu.delete(0, 'end')

    def notify_change(value):
        acronym_length_var.set(value)
        acronym_length_changed(value)

    for option in length_options:
        menu.add_command(label=option,
                         command=lambda value=option: notify_change(value))

    # Try to keep the same choice
    if acronym_length_var.get() not in length_options:
        acronym_length_var.set(0)


def toggle_itemvalue():
    global current_item
    if len(items) > 0 and not itemvalue_var.get():
        itemvalue_var.set(current_item['itemvalue'])
    else:
        itemvalue_var.set('')


def manual_entry(key):
    global current_item
    if root.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            current_item = acs[0]
            itemvalue_var.set(current_item['itemvalue'])
        else:
            itemvalue_var.set('')
    return True


def acronym_length_changed(_new_length):
    filter_items_and_show_first()


def filter_items_and_show_first():
    # build the filtered list of items and display the first one
    global items, which_item, current_item
    length = acronym_length_var.get()
    if length == 0:
        items = list(all_items)
    else:
        items = list(filter(lambda item: len(
            item['itemkey']) == length, all_items))
    which_item = 0
    reset_score()
    current_item = items[which_item] if len(items) > 0 else None
    show_itemkey()


def show_itemkey():
    root.focus_set()
    key_entry_var.set('')
    if current_item:
        key_entry_var.set(current_item['itemkey'])
    itemvalue_var.set('')
    cur_which_var.set(f"{which_item + 1} / {len(items)}")
    show_score()


def next_item():
    global which_item, current_item

    '''
    user clicks Next
    Set result for the current item (before moving to the next)
    Are we in review mode?
        No (the normal case)
            increment which_item
            deal with increment wrap
        Yes
            get index of the next incorrect result starting from current
                index == None?
    '''
    set_current_item_result()

    if review_mode_var.get():
        index = get_next_incorrect_index()
        if index is not None:
            which_item = index
    else:
        which_item += 1
        if which_item >= len(items):
            which_item = 0

    current_item = items[which_item]

    # Item result defaults to CORRECT unless it is already INCORRECT
    current_result = results[which_item]
    correct_answer_var.set(INCORRECT if current_result ==
                           INCORRECT else CORRECT)

    show_itemkey()


def prev_item():
    global which_item, current_item

    if review_mode_var.get():
        # Previous isn't available in review mode
        return

    if which_item <= 0:
        which_item = len(items) - 1
    else:
        which_item -= 1
    current_item = items[which_item]

    reset_current_item_result()

    show_itemkey()


def get_next_incorrect_index():
    try:
        found_index = results.index(INCORRECT, which_item + 1)
    except (ValueError, IndexError):
        try:
            found_index = results.index(INCORRECT, 0)
        except ValueError:
            found_index = None
    return found_index


def restart_test():
    load_items_from_csv()
    update_length_menu()
    filter_items_and_show_first()


def open_description_in_browser():
    link = current_item['itemlink']
    if link:
        for alink in link.split("\n"):
            webbrowser.open(alink)


def show_score():
    correct_count = results.count(CORRECT)
    incorrect_count = results.count(INCORRECT)
    score_var.set(
        f"Correct: {correct_count}   Incorrect: {incorrect_count}")


def set_current_item_result():
    results[which_item] = CORRECT if correct_answer_var.get() else INCORRECT
    show_score()


def reset_current_item_result():
    results[which_item] = UNTESTED
    show_score()


def reset_score():
    global results
    results = [UNTESTED] * len(items)
    show_score()


def toggle_correct_answer():
    correct_answer_var.set(
        INCORRECT if correct_answer_var.get() == CORRECT else CORRECT)


def win_evt(event):
    match event.keysym:
        case 'Right':
            next_item()
        case 'Left':
            prev_item()
        case 'space':
            toggle_itemvalue()
        case 'Escape':
            toggle_correct_answer()


load_items_from_csv()
root = tk.Tk()
# root.geometry('500x200+2500+1100')  # external monitor
root.geometry('500x200+800+500')  # laptop

# Do this before creating any menus
root.option_add('*tearOff', False)

# Row 0
acronym_length_var = tk.IntVar()
length_menu = create_length_menu()
length_menu.grid(row=0, column=1)

key_entry_var = tk.StringVar()
key_entry = tk.Entry(textvariable=key_entry_var, font=(
    'Courier', '18'), justify=tk.CENTER, validatecommand=(root.register(manual_entry), '%P'), validate='key')
key_entry.grid(row=0, column=2)
cur_which_var = tk.StringVar()
tk.Label(textvariable=cur_which_var).grid(row=0, column=3, sticky='w')

# Row 1
itemvalue_var = tk.StringVar()
tk.Label(textvariable=itemvalue_var, justify=tk.CENTER,
         width=55).grid(row=1, column=1, columnspan=4)

# Row 2
tk.Button(text='Previous', command=prev_item).grid(row=2, column=1, sticky='e')
tk.Button(text='Toggle', command=toggle_itemvalue).grid(row=2, column=2)
tk.Button(text='Next', command=next_item).grid(row=2, column=3, sticky='w')

# Row 3
score_var = tk.StringVar()
tk.Label(textvariable=score_var).grid(row=3, column=2)
score_var.set('Score: ')
correct_answer_var = tk.BooleanVar(value=CORRECT)
tk.Checkbutton(text='Correct', variable=correct_answer_var).grid(
    row=3, column=3, sticky='w')

# Row 4
tk.Button(text='Reload', command=restart_test).grid(
    row=4, column=1, sticky='e')
review_mode_var = tk.BooleanVar(value=False)
tk.Checkbutton(text='Review Mode', variable=review_mode_var).grid(
    row=4, column=2)
tk.Button(text='Browse', command=open_description_in_browser).grid(
    row=4, column=3, sticky='w')

filter_items_and_show_first()

# test the longest string
# itemvalue_var.set(
#     'Completely Automated Turing Test To Tell Computers and Humans Apart')

root.bind('<Key>', win_evt)
root.mainloop()
