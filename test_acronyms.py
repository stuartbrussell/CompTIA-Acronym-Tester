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
    root.focus_set()


def manual_entry(key):
    # A hacky way to try out a specific key. It does not affect the current
    # index. Prev/Next will continue as if the manual entry did not occur.
    if root.focus_get() == key_entry:
        acs = list(
            filter(lambda item: item['itemkey'].upper() == key.upper(), items))
        if len(acs) > 0:
            item = acs[0]
            itemvalue_var.set(item['itemvalue'])
            global current_item
            current_item = item
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
    update_current_item_result()

    if review_mode_var.get():
        index = get_next_incorrect_index(current_item_index)
        if index is not None:
            set_current_item_index(index)
    else:
        set_current_item_index(current_item_index + 1)\

    update_correct_answer_checkbox()
    show_itemkey()


def prev_item():
    if review_mode_var.get():
        index = get_prev_incorrect_index(current_item_index)
        if index is not None:
            set_current_item_index(index)
    else:
        set_current_item_index(current_item_index - 1)
        update_correct_answer_checkbox()

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


def get_prev_incorrect_index(cur_index):
    try:
        results_rev = results[-1::-1]
        starting_index = len(results_rev) - cur_index
        found_index = results_rev.index(INCORRECT,  starting_index)
    except (ValueError, IndexError) as e:
        try:
            found_index = results_rev.index(INCORRECT, 0)
        except ValueError:
            found_index = None
    if found_index is not None:
        found_index = len(results_rev) - found_index - 1
    return found_index


def restart_test():
    load_items_from_csv()
    update_length_menu()
    reset_current_item_result()
    update_correct_answer_checkbox()
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


def update_current_item_result():
    results[current_item_index] = CORRECT if correct_answer_var.get() else INCORRECT
    if INCORRECT in results:
        review_mode_btn.config(state=tk.ACTIVE)
    else:
        reset_review_mode()
    show_score()


def update_correct_answer_checkbox():
    # Item result defaults to CORRECT unless it is already INCORRECT
    current_result = results[current_item_index]
    correct_answer_var.set(INCORRECT if current_result ==
                           INCORRECT else CORRECT)


def reset_current_item_result():
    results[current_item_index] = UNTESTED
    show_score()


def toggle_review_mode():
    is_review_mode = review_mode_var.get()
    first_incorrect_index = get_next_incorrect_index(-1)
    if first_incorrect_index is not None:
        set_current_item_index(first_incorrect_index)
        correct_answer_var.set(INCORRECT)


def reset_review_mode():
    review_mode_var.set(False)
    review_mode_btn.config(state=tk.DISABLED)


def reset_score():
    global results
    results = [UNTESTED] * len(items)
    reset_review_mode()
    update_correct_answer_checkbox()
    show_score()


def toggle_correct_answer(update_var=False):
    if update_var:
        # Only do this if the command is NOT called from the checkbutton.
        # The checkbutton already sets the var.
        correct_answer_var.set(INCORRECT if correct_answer_var.get()
                               == CORRECT else CORRECT)
    update_current_item_result()


def win_evt(event):
    match event.keysym:
        case 'Right' | 'Down':
            next_item()
        case 'Left' | 'Up':
            prev_item()
        case 'space':
            toggle_itemvalue()
        case 'Escape':
            toggle_correct_answer(update_var=True)


load_items_from_csv()
root = tk.Tk()
window_width = 500
window_height = 200
# center window on screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_ul_x = int(screen_width/2 - window_width/2)
window_ul_y = int(screen_height/2 - window_height/2)
root.geometry(f"{window_width}x{window_height}+{window_ul_x}+{window_ul_y}")

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
tk.Checkbutton(text='Correct', variable=correct_answer_var, command=toggle_correct_answer).grid(
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
