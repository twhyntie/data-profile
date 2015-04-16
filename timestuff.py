#!/usr/bin/env python
# -*- coding: utf-8 -*-

#...for the logging.
import logging as lg

#...for the time (being).
import time

#...for even more MATH.
import numpy as np

# Import the plotting libraries.
import pylab as plt

#...for the colours. Oh, the colours!
from matplotlib.colors import LogNorm

# Load the LaTeX text plot libraries.
from matplotlib import rc

# Uncomment to use LaTeX for the plot text.
rc('font',**{'family':'serif','serif':['Computer Modern']})
rc('text', usetex=True)

#...for plotting arbitrary rectangles on the plots.
from matplotlib.patches import Rectangle

#...for the custom Pixelman time string.
from handlers import getPixelmanTimeString

## Dictionary for the month start times in seconds since epoch.
month_start_times = {}

month_start_times["2012-01-01-000000"] = 1325376000
month_start_times["2012-02-01-000000"] = 1328054400
month_start_times["2012-03-01-000000"] = 1330560000
month_start_times["2012-04-01-000000"] = 1333238400
month_start_times["2012-05-01-000000"] = 1335830400
month_start_times["2012-06-01-000000"] = 1338508800
month_start_times["2012-07-01-000000"] = 1341100800
month_start_times["2012-08-01-000000"] = 1343779200
month_start_times["2012-09-01-000000"] = 1346457600
month_start_times["2012-10-01-000000"] = 1349049600
month_start_times["2012-11-01-000000"] = 1351728000
month_start_times["2012-12-01-000000"] = 1354320000
month_start_times["2013-01-01-000000"] = 1356998400
month_start_times["2013-02-01-000000"] = 1359676800
month_start_times["2013-03-01-000000"] = 1362096000

class DataMonth:
    """ Wrapper class for each month. """

    def __init__(self, start_time_s, end_time_s):
        """ Constructor. """

        lg.info(" * Initialising DataMonth object...")

        ## The start time of the month [s].
        self.__st_s = start_time_s

        ## The Python time object representing the month start time.
        self.__st = time.gmtime(self.__st_s)

        ## The Pixelman time string of the start time.
        self.__st_str = getPixelmanTimeString(self.__st_s)[2]

        ## The end time of the month [s].
        self.__et_s = end_time_s

        ## The Python time object representing the month end time.
        self.__et = time.gmtime(self.__et_s)

        ## The Pixelman time string of the end time.
        self.__et_str = getPixelmanTimeString(self.__et_s)[2]

        ## The duration of the month [s].
        self.__Delta_s = self.__et_s - self.__st_s + 1

        ## The number of non-full day seconds in the month (error checking).
        self.__remainder_seconds = self.__Delta_s % (60 * 60 * 24)

        ## The number of days in the month [days].
        self.__n_days = (self.__Delta_s - self.__remainder_seconds) / (60 * 60 * 24)
        #
        if self.__remainder_seconds != 0:
            raise IOError("* Error! Month has %d remainder seconds." % (self.__remainder_seconds))

        ## Dictionary of the number of frames recorded in each day.
        self.__frames_in_a_day = {}
        #
        #
        for day in range(1, self.__n_days + 1):
            self.__frames_in_a_day[day] = 0

        ## The number of frames found in that month.
        self.__num_frames = 0

        # Update the user.
        lg.info(" * Start time is %s (%d)" % (self.__st_str, self.__st_s))
        lg.info(" * End   time is %s (%d)" % (self.__et_str, self.__et_s))
        lg.info(" * Number of days in the month = %d" % (self.__n_days))
        lg.info(" *")

    def __lt__(self, other):
        return self.getStartTime() < other.getStartTime()

    def getStartTime(self):
        return self.__st_s

    def getNumberOfDays(self):
        return self.__n_days

    def getName(self):
        return time.strftime("%Y-%m", self.__st)

    def addFrame(self, st):
        """
        Add a frame to the month.

        @param [in] st The frame start time [s].
        """
        self.__num_frames += 1

        ## The day of the month (%02d) associated with the start time.
        day = int(time.strftime("%d", time.gmtime(st)))

        #lg.info(" * Found new frame: %s -> day = %d" % (time.asctime(time.gmtime(st)), day))

        self.__frames_in_a_day[day] += 1

    def getNumberOfFrames(self):
        return self.__num_frames

    def getFramesInEachDay(self):
        return self.__frames_in_a_day


class MonthPlot:
    """ Wrapper class for the monthly plots. """

    def __init__(self, data_month, **kwargs):
        """
        Constructor.

        @param [in] data_month DataMonth object for the month to plot.
        """

        lg.info(" * Initialising MonthPlot object...")

        # Reset the matplot lib plotting stuff.
        plt.close()

        # Here we create the figure on which we'll be plotting our results.
        # We assign the figure a number, a size (5" x 3"), set the resolution
        # of the image (150 DPI), and set the background and outline to white.

        ## The figure width [inches].
        self.__fig_w = 5.0
        #
        if "fig_width" in kwargs.keys():
            self.__fig_width = kwargs["fig_width"]

        ## The figure height [inches].
        self.__fig_h = 5.0
        #
        if "fig_height" in kwargs.keys():
            self.__fig_h = kwargs["fig_height"]

        ## The histogram.
        self.__plot = plt.figure(101, figsize=(self.__fig_w, self.__fig_h), dpi=150, facecolor='w', edgecolor='w')

        # Then we give a bit of clearance for the axes.
        self.__plot.subplots_adjust(bottom=0.17, left=0.15)

        # This is the subplot on which we'll actually be plotting.
        self.__plot_ax = self.__plot.add_subplot(111)

        # Label your axes:

        ## The x axis label.
        self.__x_label = "Day"
        #
        if "x_label" in kwargs.keys():
            self.__x_label = kwargs["x_label"]
        #
        plt.xlabel(self.__x_label)

        ## The y axis label.
        self.__y_label = "$y$"
        #
        if "y_label" in kwargs.keys():
            self.__y_label = kwargs["y_label"]
        #
        plt.ylabel(self.__y_label)

        # Plot the number of frames.

        # Should be we use a logarithmic scale for the y axis?
        # Not yet, but we might do later.
        uselogy = False

        # Firstly, we'll choose our plot bin values. We will use bin
        # widths of 1.

        ## The maximum x (day) value.
        max_x = data_month.getNumberOfDays()
        #lg.info(" * x max                           : %4d" % (sim_max_x))

        ## The bin width - we'll stick with one for the moment.
        bin_width = 1

        # Create the bin edges array for the frames data:
        bins = np.arange(1, max_x+bin_width, bin_width)
        #lg.info("* Bins")
        #lg.info bins # uncomment this if you want to see the actual bin edges.
        lg.info(" *")

        #lg.info(" * Bins:")
        #lg.info(bins)
        #lg.info(" * Frames from each day:")
        #lg.info(data_month.getFramesInEachDay().values())
        #lg.info(" *")

        # Create a histogram for the frames data
        # using the bin edges defined above.
        #
        ## The bar chart patches.
        patches_f = plt.bar(bins, data_month.getFramesInEachDay().values())

        # Set the display propertied of the "patches" (bars).
        # We're using translucent green bars with no outline.
        plt.setp(patches_f, 'facecolor', '#AADDAA', 'alpha', 1.0, 'linewidth', 0.0)

        ## The maximum y value.
        y_max = max(data_month.getFramesInEachDay().values())
        #
        # Round up to the nearest 1000.
        y_max = 1000 * (np.floor(y_max/1000.) + 1)
        #
        if y_max > 0:
            plt.ylim([0.0, y_max])

        # If supplied by the user, set the y axis limits.
        if "y_max" in kwargs.keys():
            y_max = kwargs["y_max"]
            plt.ylim([0.0, y_max])


        # Shade out the unused days.
        self.__plot_ax.add_patch(Rectangle((data_month.getNumberOfDays() + 1, 0), 31 - data_month.getNumberOfDays(), y_max, facecolor="#dddddd", edgecolor="#dddddd"))

        # Add gridlines.
        plt.grid(1)

        ## The x axis maximum.
        self.__x_max = 32.0
        #
        if "x_max" in kwargs.keys():
            self.__x_max = kwargs["x_max"]

        # Set the x axis limits.
        plt.xlim([1, self.__x_max])

        lg.info(" *")

    def save_plot(self, outputpath, name):
        """ Saves the figure. """

        # PNG (for HTML pages).
        self.__plot.savefig(outputpath + "/%s.png" % (name))

        # PostScript (for publications).
        self.__plot.savefig(outputpath + "/%s.ps"  % (name))
