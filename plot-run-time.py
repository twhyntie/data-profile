#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 CERN@school - Plotting the MoEDAL LHC Run 1 Timepix data.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

#...for the data unpacking.
import struct

#...for the MATH.
import math

#...for the time (being).
import time

#...for the extra time (stuff).
from timestuff import month_start_times, DataMonth, MonthPlot

if __name__ == "__main__":

    print("*")
    print("*=============================*")
    print("* CERN@school - plot run time *")
    print("*=============================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the binary input data.")
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
    lg.basicConfig(filename=os.path.join(outputpath, 'log_plot-run-time.log'), filemode='w', level=level)

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

    lg.info(" * Plotting information about: '%s'" % (datapath))
    lg.info(" *")
    lg.info(" * File size                : % 15d [B]" % (os.path.getsize(datapath)))
    lg.info(" * Number of frames         : % 15d"     % (n_frames))

    ## The month start times.
    start_times = sorted(month_start_times.values())

    ## Dictionary of the month wrapper objects.
    months = {}
    #
    # Populate it.
    for i, st_s in enumerate(start_times):
        try:
            end_time_s = start_times[i+1] - 1
        except:
            break

        ## The month ID (for the dictionary key).
        month_id = time.strftime("%Y-%m", time.gmtime(st_s))

        # Add the month.
        months[month_id] = DataMonth(st_s, end_time_s)


    # Read the information from the binary dataset profile.
    with open(datapath, "rb") as bf:

        ## The frame count.
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

            ## The month ID.
            month_id = time.strftime("%Y-%m", time.gmtime(start_time_s))

            # Add the frame to the month.
            months[month_id].addFrame(start_time_s)

            frame_count += 1

    ## The number of frames processed - check.
    n_frames_check = 0
    #
    for month_id in sorted(months.keys()):
        #
        n_frames_check += months[month_id].getNumberOfFrames()
        #
        lg.info(" * Frames in %s: % 10d" % (months[month_id].getName(), months[month_id].getNumberOfFrames()))

    lg.info(" *")
    lg.info(" * Total number of frames : %d" % (n_frames))
    lg.info(" *                  Check : %d" % (n_frames_check))

    # Create the plots for each month.
    for month_id in sorted(months.keys()):

        ## The plot for the current month.
        m_plot = MonthPlot(months[month_id], y_max=16000, y_label="Frames")

        # Save the plot.
        m_plot.save_plot(outputpath, "%s" % (months[month_id].getName()))

        #break
