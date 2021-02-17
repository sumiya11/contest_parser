# !/usr/bin/python

import gspread
import sys
import json
import argparse


"""
    Output positions are sorted by least lexicographical order 
    on students names
    The number of Students is not constant, so, we must look up
    the table with each update to determine the order
"""


sheet_url   = "https://docs.google.com/spreadsheets/d/1ONirZzjx7I0OBfYtKVowg7xQMoRhieTRrIhY6a6nJgs/edit#gid=0"
ru_alphabet = "\n АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"


def initialize_headers(sh):
    headers = [[
        "Фамилия, Имя, Отчество",
        "ДЗ 1", "ДЗ 2", "ДЗ 3", "ДЗ 4", "ДЗ 5", "ДЗ 6", "ДЗ 7", "ДЗ 8", "Одз", " ",
        "КР 1", "КР 2", "КР 3", "КР 4","Окр"
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
    sh.freeze(1, 1)
    # TODO: init formulas


def initialize_names(sh, data):
    names = [[student["name"]] for student in data]
    sh.update(f"A2:A{len(names)+1}", names)


def update(sh, data, number):
    """
    params:
        number -- the number of assignment to be updated
    """
    names  = sh.col_values(1)[1:]
    totals = [[0] for _ in range(len(names))]
    for student in data:
        idx = names.index(student["name"])
        totals[idx][0] = student["total"]

    col = chr(ord('A') + number)
    sh.update(f"{col}2:{col}{len(totals)+1}", totals)


def parse(filename):
    with open(filename) as inputs:
        data = json.load(fp=inputs, encoding="utf-8")

    data = list(data.values())
    data.sort(key=lambda student: student["name"])

    # ignore non-ru nicknames
    # this is controversial
    # would be better to have some kind of ignore list for logins
    data = list(filter(
        lambda student:
            all(ch in ru_alphabet for ch in student["name"]),
        data
    ))
    return data


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Path to parsed data file', required=True)
    parser.add_argument('-n','--number', help='The number to be updated', required=True)
    parser.add_argument('-c','--create', help='Create table from scratch', default=False, action="store_true")
    return vars(parser.parse_args())

def main():
    args = parseargs() 
    filename = args["input"]
    number   = int(args["number"])
    create   = args["create"]
    
    # -------

    gc = gspread.service_account(filename="credentials.json")
    sh = gc.open_by_url(sheet_url)
    sh = sh.sheet1
    
    # -------

    data = parse(filename)

    # -------

    if create:
        initialize_headers(sh)
        initialize_names(sh, data)
    
    # -------

    if True:
        update(sh, data, number)


    return 0


if __name__ == "__main__":
    main()













