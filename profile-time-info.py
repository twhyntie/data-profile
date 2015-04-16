#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Profiling Mafalda Time Information.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

#...for the binary handling.
import struct

#...for the MATH.
import math

if __name__ == "__main__":

    print("*")
    print("*==========================================*")
    print("* CERN@school - time information profiling *")
    print("*==========================================*")

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
    lg.basicConfig(filename=os.path.join(outputpath, 'log_profile-time-info.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")

    ## The total number of frames.
    n_frames = os.path.getsize(datapath) / 8

    # Error handling.
    if n_frames_to_process == -1:
        n_frames_to_process = n_frames
    #
    if start_frame_number > n_frames:
        raise IOError("* ERROR! Starting frame number greater than the number of frames.")

    lg.info(" * Profiling: '%s'" % (datapath))
    lg.info(" *")
    lg.info(" * File size                : % 15d [B]" % (os.path.getsize(datapath)))
    lg.info(" * Number of frames         : % 15d"     % (n_frames))
    lg.info(" *")

    # Read the information from the binary profile file.
    with open(datapath, "rb") as bf:

        ## Frame counter.
        frame_count = 0

        while True:

            ## The eight bytes representing the next frame.
            bs = bf.read(8)

            # Skip frames before the start frame (FIXME).
            if frame_count < start_frame_number:
                frame_count += 1
                continue

            # Quit if we're at the end of the file or frame count.
            if not bs or frame_count > (n_frames_to_process + start_frame_number - 1): break

            ## The frame's data - 8 bytes, eh? Nice.
            data = struct.unpack("IhH", bs)

            ## The start time (seconds since epoch) - 4 byte unsigned integer.
            start_time_s = data[0]

            ## The acquisition time (decoded 2 byte signed integer).
            acq_time = math.pow(10, int(data[1]))

            ## The number of hit pixels (2 byte unsigned integer).
            n_pixels = int(data[2])

            # DO NOT UNCOMMENT THIS FOR THE WHOLE RUN!
            # You'll end up with a massive log file. No-one likes a massive
            # log.
            #lg.info(" * Frame % 12d: %d % f % 10d" % (frame_count, start_time_s, acq_time, n_pixels))

            frame_count += 1
