import csv
import tkinter as tk
import random
import sys
import webbrowser

items = []
current_item_index = -1
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
    if len(items) > 0 and not itemvalue_var.get():
        itemvalue_var.set(current_item['itemvalue'])
    else:
        itemvalue_var.set('')


def manual_entry(key):
    if root.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            itemvalue_var.set(acs[0]['itemvalue'])
        else:
            itemvalue_var.set(' ')
    return True


def acronym_length_changed(_new_length):
    filter_items_and_show_first()


def filter_items_and_show_first():
    # build the filtered list of items and display the first one
    global items
    length = acronym_length_var.get()
    if length == 0:
        items = list(all_items)
    else:
        items = list(filter(lambda item: len(
            item['itemkey']) == length, all_items))
    set_current_item_index(0)
    reset_score()
    show_itemkey()


def show_itemkey():
    root.focus_set()
    key_entry_var.set('')
    if current_item:
        key_entry_var.set(current_item['itemkey'])
    itemvalue_var.set('')
    cur_which_var.set(f"{current_item_index + 1} / {len(items)}")
    show_score()


def next_item():
    set_current_item_result()

    if review_mode_var.get():
        index = get_next_incorrect_index(current_item_index)
        if index is not None:
            set_current_item_index(index)
    else:
        set_current_item_index(current_item_index + 1)

    # Item result defaults to CORRECT unless it is already INCORRECT
    current_result = results[current_item_index]
    correct_answer_var.set(INCORRECT if current_result ==
                           INCORRECT else CORRECT)

    show_itemkey()


def prev_item():
    set_current_item_index(current_item_index - 1)

    reset_current_item_result()

    show_itemkey()


def get_next_incorrect_index(cur_index):
    try:
        found_index = results.index(INCORRECT, cur_index + 1)
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


def set_current_item_index(value):
    global current_item_index
    current_item_index = value
    if current_item_index >= len(items):
        current_item_index = 0
    elif current_item_index < 0:
        current_item_index = len(items) - 1

    try:
        set_current_item(items[current_item_index])
    except:
        set_current_item(None)


def set_current_item(item):
    global current_item
    current_item = item
    show_itemkey()


def set_current_item_result():
    results[current_item_index] = CORRECT if correct_answer_var.get() else INCORRECT
    if INCORRECT in results:
        review_mode_btn.config(state=tk.ACTIVE)
    else:
        reset_review_mode()
    show_score()


def reset_current_item_result():
    results[current_item_index] = UNTESTED
    show_score()


def toggle_review_mode():
    is_review_mode = review_mode_var.get()
    if is_review_mode:
        previous_btn.config(state=tk.DISABLED)
        first_incorrect_index = get_next_incorrect_index(-1)
        if first_incorrect_index is not None:
            set_current_item_index(first_incorrect_index)
            correct_answer_var.set(INCORRECT)
    else:
        previous_btn.config(state=tk.ACTIVE)


def reset_review_mode():
    review_mode_var.set(False)
    review_mode_btn.config(state=tk.DISABLED)
    previous_btn.config(state=tk.ACTIVE)


def reset_score():
    global results
    results = [UNTESTED] * len(items)
    reset_review_mode()
    show_score()


def toggle_correct_answer():
    correct_answer_var.set(INCORRECT if correct_answer_var.get()
                           == CORRECT else CORRECT)


# def set_correct_answer(is_correct):
#     correct_answer_var.set(is_correct)


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
root.geometry('500x200+100+500')  # laptop

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
previous_btn = tk.Button(text='Previous', command=prev_item)
previous_btn.grid(row=2, column=1, sticky='e')
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
review_mode_btn = tk.Checkbutton(
    text='Review Mode', variable=review_mode_var, command=toggle_review_mode)
review_mode_btn.grid(row=4, column=2)
tk.Button(text='Browse', command=open_description_in_browser).grid(
    row=4, column=3, sticky='w')

filter_items_and_show_first()

# test the longest string
# itemvalue_var.set(
#     'Completely Automated Turing Test To Tell Computers and Humans Apart')

root.bind('<Key>', win_evt)
root.mainloop()
