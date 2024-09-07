import csv
import tkinter as tk
import random

with open('A+ 1101 acronyms.csv') as acs:
    ad = csv.DictReader(acs)
    # acronyms: [{'initials':'AC', 'meaning': 'Alternating Current}]
    acronyms = [item for item in ad]

random.shuffle(acronyms)


for acr in acronyms:
    acs = list(
        filter(lambda item: item['initials'] == acr['initials'], acronyms))
    if len(acs) != 1:
        for acr in acs:
            print(acr)
