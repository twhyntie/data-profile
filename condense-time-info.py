#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Condensing Datasets (Mafalda ROOT files).

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

#...for the byte packing.
import struct

#...for the MATH.
import math

#...for the ROOT stuff.
from ROOT import TFile, TTree, gSystem

# Load in the (skeleton) Frame class - a bare-minimum class that
# provides the ROOT file format interface.
gSystem.Load('Frame_C')

if __name__ == "__main__":

    print("*")
    print("*==================================*")
    print("* CERN@school - dataset condensing *")
    print("*==================================*")

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
    lg.basicConfig(filename=os.path.join(outputpath, 'log_condense-time-info.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")

    ## The ROOT file itself.
    f = TFile(datapath)

    ## The TTree containing the data.
    chain = f.Get('MPXTree')

    ## The number of frames in the file.
    n_frames = chain.GetEntriesFast()
    #
    if n_frames_to_process == -1:
        n_frames_to_process = n_frames
    #
    if start_frame_number > n_frames_to_process:
        raise IOError("* ERROR: start frame is greater than the number of frames present.")

    # Update the user.
    lg.info(" * Input path is                 : '%s'" % (datapath))
    lg.info(" * The output is being written to: '%s'" % (outputpath))
    lg.info(" *")
    lg.info(" * Start frame            = %d" % (start_frame_number))
    lg.info(" * Number of frames       = %d" % (n_frames_to_process))
    lg.info(" *")
    lg.info(" * Number of frames found = %d" % (n_frames))
    lg.info(" *")

    ## The run ID (from the file name).
    #
    # FIXME: regex check the run ID format.
    run_id = os.path.basename(datapath).split(".")[0]

    ## The name of the dataset profile binary file.
    output_file = os.path.join(outputpath, "%s.bin" % (run_id))

    ## The binary file to write to.
    bf = open(output_file, "wb")

    # Loop over the frames in the file.
    for fn in range(start_frame_number, start_frame_number + n_frames_to_process):

        # Load the TTree.
        ientry = chain.LoadTree(fn)

        # Copy the entry into memory.
        nb = chain.GetEntry(fn)

        if nb == 0:
            break

        ## The start time (nearest second) [s].
        start_time_s = int(chain.FramesData.GetStartTime())

        ## The frame acquisition time.
        acq_time = chain.FramesData.GetAcqTime()

        # Encode the acquisition time.
        #
        # FIXME: make more elegant, perform error checking, etc.
        if acq_time < 0.001:
            log_acq_time = -3
        elif acq_time < 0.01:
            log_acq_time = -2
        elif acq_time < 0.1:
            log_acq_time = -1
        elif acq_time < 1.0:
            log_acq_time = 0
        elif acq_time < 10.0:
            log_acq_time = 1

        ## The number of hit pixels in the frame.
        n_pixels = len(chain.FramesData.GetFrameXC())

        # If we do have a fully occupied frame, set it to one below to avoid
        # a 2 byte penalty for the whole dataset(!).
        if n_pixels == 256*256:
            n_pixels = 256*256 - 1

        #lg.info(" * Start time, acq. time, n_pixels: %d [s], %f [s] (%d), % 10d" % (int(start_time_s), acq_time, int(log_acq_time), int(n_pixels)))

        # Write the start time, log(10) of the acq. time, and number of pixels
        # to the binary file.
        bf.write(struct.pack('IhH', int(start_time_s), int(log_acq_time), int(n_pixels)))

    # Tidy up.
    bf.close()
