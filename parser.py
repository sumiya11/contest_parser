#!/usr/bin/python

import sys
import os
import json
import argparse
import re

from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup


output_folder = "standings"
output_ext    = ".json"


"""
    UTC+3:00
"""


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Path to contest dump file', required=True)
    parser.add_argument('-d','--deadlines', help='Path to deadlines file', required=True)
    parser.add_argument('-o','--output', help='Output filename', required=True)
    parser.add_argument('-f','--filter', help='Take participants from the filename', default=None)
    parser.add_argument('-k','--KR', help='Kontrolnaya rabota rules', default=False, action="store_true")
    return vars(parser.parse_args())


def main():
    args = parseargs()
    input_file     = args["input"]
    deadlines_file = args["deadlines"]
    output_file    = args["output"]
    filter_file    = args["filter"]
    KR             = args["KR"]

    # parse deadlines
    with open(deadlines_file) as inputs:
        deadlines = [
            [ 1000 * int(parser.parse(timepoint).timestamp()), float(scaling) ]
            for timepoint, scaling in 
            [ line.split("=") for line in inputs.readlines() ]    
        ]
    
    # parse the dump
    with open(input_file, 'r') as inputs:
        soup = BeautifulSoup(inputs, 'xml')


    # parse the file with logins
    if filter_file:
        with open(filter_file, 'r') as inputs:
            # valid login --> user group
            sep = re.compile("[\t ]+")
            valid_logins = {} 
            for line in inputs.readlines():
                line = re.split(sep, line)
                login, group = line[0].strip(), line[-1].strip()
                valid_logins[login] = group

    # problem titles
    problems = [
        problem["title"]
        for problem in soup.find_all("problem")
    ]
    
    # additional 
    # userid --> userlogin
    id_to_login = {
        user["id"] : user["loginName"]
        for user in soup.find_all("user")
    }

    # userlogin --> (name, problems score, total score)
    login_to_data = {
        user["loginName"] : { 
            "name" : user["displayedName"],
            "problems" : {
                title : 0.
                for title in problems
            },
            "total" : 0.
        }
        for user in soup.find_all("user")
    }

    
    for submit in soup.find_all("submit", verdict="OK"):
        userid = submit["userId"]
        userlogin = id_to_login[userid]
        absolute_time = int(submit["absoluteTime"])
        problem_title = submit["problemTitle"]
        score = float(submit["score"])
        
        max_scale = 0.

        for deadline, scaling in deadlines:
            # time < deadline time
            if absolute_time < deadline:
                max_scale = max(max_scale, scaling)
        # we want the best result so far
        login_to_data[userlogin]["problems"][problem_title] = max(
                # and give 0.5 for non-positive OKs
                max_scale * score if score > 0 else (0.5 if not KR else 0),
                login_to_data[userlogin]["problems"][problem_title],
        )

    # to sum it up
    for user in login_to_data.values():
        user["total"] = sum(user["problems"].values())

    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    
    # we ignore users who are not from the given list
    if filter_file:
        for login in list(login_to_data.keys()):
            if login not in valid_logins:
                login_to_data.pop(login)
            else:
                login_to_data[login]["group"] = valid_logins[login]


    with open(output_folder + "/" + output_file + output_ext, 'w') as outputs:
        json.dump(login_to_data, outputs, ensure_ascii=False, indent="\t")        

    return 0


if __name__ == "__main__":
    main()





