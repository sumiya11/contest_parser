#!/usr/bin/python

import sys
import os
import json
import argparse
import re

from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup
from collections import namedtuple

output_folder = "standings"
output_ext    = ".json"


"""
    UTC+3:00
"""


def parse_deadlines(dls):
    """
        transforms a given vector of lines `dls` to a vector of pairs:
            (until time, grade scale)
        where time format is ms and scale format lies in [0, 1]
    """
    dl = namedtuple("deadline", ["until", "scale"])
    return [
        dl(
            1000*int(parser.parse(timepoint).timestamp()),
            float(scaling)
        )
        for timepoint, scaling in [ 
            line.split("=") for line in dls
            if line
        ]
    ]


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Path to contest dump file', required=True)
    parser.add_argument('-d','--deadlines', help='Path to deadlines file', required=True)
    # whatever it means
    parser.add_argument('-e','--extension', help='Path to optionally extended deadlines', default=None)
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
    extension      = args["extension"]

    
    # parse deadlines
    with open(deadlines_file) as inputs:
        common_dls = parse_deadlines(inputs.readlines())
    
    # parse dump
    with open(input_file, 'r') as inputs:
        soup = BeautifulSoup(inputs, 'xml')

    # parse the file with logins
    if filter_file:
        with open(filter_file, 'r') as inputs:
            # valid login --> user group
            sep = re.compile("[\t ]+")
            valid_logins = {} 
            for line in filter(bool, inputs.readlines()):
                line = re.split(sep, line)
                login, group = line[0].strip(), line[-1].strip()
                name = " ".join(map(lambda x : x.strip(), line[1:-1]))
                meta = namedtuple("meta", ["group", "name"])
                valid_logins[login] = meta(group, name)
    
    # user login -> vector of his deadlines
    # (in case of any custom deadline provided in extension)
    custom_dls = {}

    # parse optional deadlines extension
    if extension:
        with open(extension, 'r') as inputs:
            inputs = map(lambda x: x.strip(), inputs.read().split("=="))
            for login, *dls in map(lambda x: x.split('\n'), inputs):
                custom_dls[login] = parse_deadlines(dls)

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
        deadlines = custom_dls[userlogin] \
                    if userlogin in custom_dls \
                    else common_dls 

        for dl in deadlines:
            # time < deadline time
            if absolute_time < dl.until:
                max_scale = max(max_scale, dl.scale)
        # we want the best result so far
        login_to_data[userlogin]["problems"][problem_title] = max(
                # and give 0.5 for non-positive OKs
                # (only if it is not kontrolnaya rabota)
                max_scale * (score if score > 0 else (0.5 if not KR else 0)),
                login_to_data[userlogin]["problems"][problem_title],
        )

    # to sum it up
    for user in login_to_data.values():
        user["total"] = sum(user["problems"].values())
    
    # we [1] ignore users who are not from the given list
    # and [2] fill missing ones with zeros
    if filter_file:
        # [1]
        for login in list(login_to_data.keys()):
            if login not in valid_logins:
                login_to_data.pop(login)
            else:
                login_to_data[login]["group"] = valid_logins[login].group
                login_to_data[login]["name"]  = valid_logins[login].name
        # [2]
        for valid_login in list(valid_logins.keys()):
            if valid_login not in login_to_data:
                login_to_data[valid_login] = {
                    "name"  : valid_logins[valid_login].name,
                    "group" : valid_logins[valid_login].group,
                    "total" : 0.0
                }

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    with open(output_folder + "/" + output_file + output_ext, 'w') as outputs:
        json.dump(login_to_data, outputs, ensure_ascii=False, indent="\t")        

    return 0


if __name__ == "__main__":
    main()


