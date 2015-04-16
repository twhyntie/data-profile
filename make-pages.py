#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Making the MoEDAL LHC Run 1 Timepix data pages.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

#...for the file writing.
import codecs

#...for making the plot HTML.
from helpers import make_plot_page

if __name__ == "__main__":

    print("*")
    print("*===================================*")
    print("* CERN@school - make the HTML pages *")
    print("*===================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the plot image files.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data file.
    datapath = args.inputPath

    ## The output path.
    outputpath = args.outputPath
    #
    # Check if the output directory exists. If it doesn't, quit.
    if not os.path.isdir(outputpath):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (outputpath))

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_make-pages.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")

    # Make the web pages.

    ## Dictionary for the plot images.
    plot_paths = {}
    #
    for fn in sorted(glob.glob(os.path.join(datapath, "*.png"))):

        ## The month ID ("%Y-%m").
        month_id = os.path.basename(fn).split(".")[0]
        #
        # Add the plot to the dictionary.
        plot_paths[month_id] = os.path.basename(fn)

    ## The path to the HTML page for the dataset profiles.
    html_path = os.path.join(outputpath, "plots.html")
    #
    with codecs.open(html_path, 'w', 'utf-8') as f:
        f.write(make_plot_page(plot_paths))
