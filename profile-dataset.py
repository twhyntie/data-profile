#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Profiling Datasets (MoEDAL).

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

# Import the JSON library.
import json

#...for the ROOT stuff.
from ROOT import TFile, TTree

#... handler functions.
from handlers import getPixelmanTimeString, make_time_dir

if __name__ == "__main__":

    print("*")
    print("*=================================*")
    print("* CERN@school - dataset profiling *")
    print("*=================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the input dataset.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("numFrames",       help="The number of frames to process (-1 for all).")
    parser.add_argument("startFrame",      help="The starting frame.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data file.
    datapath = args.inputPath

    ## The output path.
    outputpath = args.outputPath

    # Check if the output directory exists. If it doesn't, quit.
    if not os.path.isdir(outputpath):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (outputpath))

    ## The number of frames to process.
    n_frames_to_process = int(args.numFrames)

    ## The start frame.
    start_frame_number = int(args.startFrame)

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_profile-dataset.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")

    ## The ROOT file containing the dataset to be profiled.
    f = TFile(datapath, "READ")

    ## The TTree containing the data.
    dataset_chain = f.Get('dscData')

    ## The number of frames in the file.
    n_frames = dataset_chain.GetEntriesFast()


    # Error handling.
    if n_frames_to_process == -1:
        n_frames_to_process = n_frames
    #
    if start_frame_number > n_frames_to_process:
        raise IOError("* ERROR! Starting frame number greater than the number of frames.")

    ## The chip ID, determined from the dataset filename.
    chip_id = None

    ## The dataset filename.
    dataset_file_name = os.path.basename(datapath)

    if   dataset_file_name[0:5] == "tpx01":
        chip_id = "F03-W0098"
    elif dataset_file_name[0:5] == "tpx02":
        chip_id = "F04-W0098"
    else:
        raise IOError("* ERROR! Invalid chip ID!")

    lg.info(" *")
    lg.info(" * Input path          : '%s'" % (datapath))
    lg.info(" * Output path         : '%s'" % (outputpath))
    lg.info(" *")
    lg.info(" * Chip ID             : '%s'" % (chip_id))
    lg.info(" *")
    lg.info(" * Number of frames in the dataset  : % 15d" % (n_frames))
    lg.info(" * Starting frame                   : % 15d" % (start_frame_number))
    lg.info(" * Frames to be processed           : % 15d" % (n_frames_to_process))
    lg.info(" *")

    ## List of the start times.
    st_s = []

    # Loop over the frames.
    for fn in range(start_frame_number, n_frames_to_process):

        # Load the TTree.
        ientry = dataset_chain.LoadTree(fn)

        # Copy the entry into memory.
        nb = dataset_chain.GetEntry(fn)

        ## The start time of the frame.
        st = float(dataset_chain.Start_time)

        # Add the start timt to the list.
        st_s.append(st)

        #start_time_s, start_time_subsec, start_time_str = getPixelmanTimeString(st)

        #acq_time = float(dataset_chain.Acq_time)

        #lg.info(" * Frame % 15d: %s (%f), %f [s]" % (fn, start_time_str, st, acq_time))

    ## The acquisition time for the frame (from the last frame).
    delta_t = dataset_chain.Acq_time

    # Close the ROOT file.
    f.Close()

    # Sort the list of start times.
    st_s = sorted(st_s)

    # Get the first frame's start time information.
    first_start_time_s, first_start_time_subsec, first_start_time_str = getPixelmanTimeString(st_s[0])

    # Get the last frame's start time information.
    last_start_time_s, last_start_time_subsec, last_start_time_str = getPixelmanTimeString(st_s[-1])

    ## The total length of time covered by the dataset [s].
    Delta_T = st_s[-1] - st_s[0]

    ## The average time between frames [s].
    Delta_t = Delta_T / (len(st_s) - 1)

    # Create the dataset information JSON.
    dataset_info_dict = {}
    #
    dataset_info_dict["chip_id"] = chip_id
    #
    dataset_info_dict["start_time_s"] = first_start_time_s
    #
    dataset_info_dict["Delta_T"] = Delta_T
    #
    dataset_info_dict["Delta_t"] = Delta_t
    #
    dataset_info_dict["delta_t"] = delta_t
    #
    dataset_info_dict["file_name"] = dataset_file_name
    #
    dataset_info_dict["n_frames"] = n_frames

    lg.info(" * Chip ID         : '%s'" % (chip_id))
    lg.info(" *")
    lg.info(" * First start time: %s (%f)" % (first_start_time_str, st_s[ 0]))
    lg.info(" * Last  start time: %s (%f)" % (last_start_time_str,  st_s[-1]))
    lg.info(" *")
    lg.info(" * Delta_{T} = %f [s]" % (Delta_T))
    lg.info(" *")
    lg.info(" * Delta_{t} = %f [s]" % (Delta_t))

    json_file_name = "%s_%s.json" % (chip_id, make_time_dir(st_s[0]))
    #
    # Write out the frame information to a JSON file.
    with open(os.path.join(outputpath, json_file_name), "w") as jf:
        json.dump(dataset_info_dict, jf)
