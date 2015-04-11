#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Displaying dataset profiles.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for writing out files.
import codecs

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

# Import the JSON library.
import json

#...for the handler functions.
from handlers import getPixelmanTimeString, make_time_dir

#...for making the profile page.
from helpers import make_profile_page

if __name__ == "__main__":

    print("*")
    print("*===========================================*")
    print("* CERN@school - displaying dataset profiles *")
    print("*===========================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the input dataset.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data file.
    datapath = args.inputPath

    ## The output path.
    outputpath = args.outputPath

    # Check if the output directory exists. If it doesn't, quit.
    if not os.path.isdir(outputpath):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (outputpath))

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_display-profile.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")

    # List the JSONs in the input directory.

    ## Dictionary of the datasets.
    jds = {}

    # Loop over the dataset JSON files found.
    for jp in sorted(glob.glob(os.path.join(datapath, "*.json"))):

        ## The JSON file name.
        jfn = os.path.basename(jp)

        ## Get the JSON information from the file.
        jf = open(jp, "r")
        jd = json.load(jf)
        jf.close()

        ## The run ID of the dataset (from the file name).
        run_id = jfn.split(".")[0]

        # Add the dataset to the dictionary.
        jds[run_id] = jd

        lg.info(" * Run ID: '%s'" % (run_id))

    ## The path to the HTML page for the dataset profiles.
    html_path = os.path.join(outputpath, "profiles.html")
    #
    with codecs.open(html_path, 'w', 'utf-8') as f:
        f.write(make_profile_page(jds))
