#!/usr/bin/python

import sys
import os
import json

from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup


output_folder = "standings"
output_ext    = ".json"


"""
    UTC+3:00
"""

def main(argv):
    input_file, deadlines_file = argv

    # parse the deadlines
    with open(deadlines_file) as inputs:
        deadlines = [
            [ 1000 * int(parser.parse(timepoint).timestamp()),
                float(scaling) ]
            for timepoint, scaling in 
            [ line.split("=") for line in inputs.readlines() ]    
        ]
    
    # parse the dump
    with open(input_file, 'r') as inputs:
        soup = BeautifulSoup(inputs, 'xml')
    
    # problem titles
    problems = [
        problem["title"]
        for problem in soup.find_all("problem")
    ]
    
    # iserid --> (name, problems score, total score)
    userid_to_data = {
        user["id"] : { 
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
        absolute_time = int(submit["absoluteTime"])
        problem_title = submit["problemTitle"]
        score = float(submit["score"])
        
        max_scale = 0.

        for deadline, scaling in deadlines:
            # time < deadline time
            if absolute_time < deadline:
                max_scale = max(max_scale, scaling)
        # we want the best result so far
        userid_to_data[userid]["problems"][problem_title] = max(
                max_scale * score,
                userid_to_data[userid]["problems"][problem_title],
        )

    # to sum it up
    for user in userid_to_data.values():
        user["total"] = sum(user["problems"].values())

    
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    # output file name is derived from the contest name 
    output_file = soup.find("contestLog").settings.contestName.contents[0]

    with open(output_folder + "/" + output_file + output_ext, 'w') as outputs:
        json.dump(userid_to_data, outputs, ensure_ascii=False, indent="\t")        

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])





