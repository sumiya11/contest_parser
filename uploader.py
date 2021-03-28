# !/usr/bin/python

import gspread
import sys
import json
import argparse

from datetime import datetime
from itertools import takewhile

# -----------------------------------------------------------------------------

"""
    Output positions are sorted by group. Within the group the order is
    least lexicographical on students names

    The number of Students is not constant, so, we must look up
    the table with each update to determine the order
"""


sheet_url   = "https://docs.google.com/spreadsheets/d/1ONirZzjx7I0OBfYtKVowg7xQMoRhieTRrIhY6a6nJgs/edit#gid=0"

# -----------------------------------------------------------------------------

def initialize_headers(sh):
    headers = [[
        "Фамилия, Имя, Отчество", "Группа",
        "ДЗ 1", "ДЗ 2", "ДЗ 3", "ДЗ 4", "ДЗ 5", "ДЗ 6", "ДЗ 7", "ДЗ 8", "Одз",
        "КР 1", "КР 2", "КР 3", "КР 4", "Окр",
        "", "Онакоп"
        ]
    ]
    formats = {
        "horizontalAlignment": "CENTER",
        "textFormat": {
            "fontSize": 10,
            "bold": True
        }
    }
    sh.clear()
    sh.update(f"A1:{chr(ord('A')+len(headers[0]))}1", headers)
    sh.format(f"A1:{chr(ord('A')+len(headers[0]))}1", formats)
    sh.freeze(1, 2)


def initialize_names(sh, data):
    names = [[student["name"], student["group"]] for student in data]
    sh.update(f"A2:B{len(names)+1}", names)


def add_points(sh, data, number, append=False):
    """
    params:
        number -- the number of contest to be updated
            where `1` stands for the first HW
            and   `10` for the first KR   
        append -- set if students present in data
            are being updated only
    """

    # column index to be updated
    shift = 1
    col = chr(ord('A') + number + shift)

    # take name ordering from the table
    names  = list(takewhile(bool, sh.col_values(1)[1:]))
    if append:
        totals = [
            [_] 
            for _ in takewhile(bool, sh.col_values(number + shift+1)[1:])
        ]
    else:
        totals = [[0] for _ in range(len(names))]
    
    for student in data:
        # set the student' score
        idx = names.index(student["name"])
        # we take the maximum of all student' results for the test
        totals[idx][0] = max(
            student["total"],
            float(totals[idx][0])
        )

    sh.update(f"{col}{2}:{col}{len(totals) + 1}", totals)

def timestamp(sh):
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    stamp += " MSK"
    sh.update("W3:W3", [[stamp]])

# -----------------------------------------------------------------------------

def parse(filename):
    with open(filename) as inputs:
        data = json.load(fp=inputs, encoding="utf-8")

    data = list(data.values())
    data.sort(
            key=lambda user: 
            (len(user["group"]), user["group"], user["name"])
    )

    return data


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Path to parsed data file', required=True)
    parser.add_argument('-n','--number', help='The number to be updated', required=True)
    parser.add_argument('-c','--create', help='Create table from scratch', default=False, action="store_true")
    parser.add_argument('-a','--append', help='Only present students to be rewritten', default=False, action="store_true")

    return vars(parser.parse_args())

# -----------------------------------------------------------------------------

def main():
    args = parseargs() 
    filename = args["input"]
    number   = int(args["number"])
    create   = args["create"]
    append   = args["append"]

    # -------

    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_url(sheet_url)
    sh = sh.sheet1
    
    # -------

    data = parse(filename)

    # -------

    if create:
        if False:
            initialize_headers(sh)
        initialize_names(sh, data)
    
    # ------

    if True:
        add_points(sh, data, number, append=append)
    
    # ------
    if True:
        timestamp(sh)

    return 0


if __name__ == "__main__":
    main()


