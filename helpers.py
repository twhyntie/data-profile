#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

CERN@school: helper functions.

See http://cernatschool.web.cern.ch for more information.

"""

#...for the time (being).
import time

#...for handling the time strings.
from handlers import getPixelmanTimeString

def make_profile_page(jds):

    """
    Make a dataset profile page.

    @param [in] jds Dictionary of JSON data for the datasets.
    """

    ## The string to return for the page.
    s = '''<!DOCTYPE html>
<html>
<head>
  <!-- <link rel="stylesheet" type="text/css" href="main.css"> -->
  <style>
{{CSS}}
  </style>
</head>
<div id="container">

  <!-- Main Content -->
  <div id="main">
    <table>
      <tr>
        <th>Run ID</th>
        <!-- <th>Chip ID</th> -->
        <th>Frames</th>
        <th>Size [B]</th>
        <th>Start time</th>
        <th>&Delta; <em>T</em> [s]</th>
        <th>&Delta; <em>t</em> [s]</th>
        <th>&delta; <em>t</em> [s]</th>
        <th>File name</th>
      </tr>
      {{TABLE_ROWS}}
    </table>
  </div>

  <!-- Footer -->
  <div id="footer">&copy; CERN@school 2015</div>

</div>
</html>
'''

    ## The table contents (generated from the JSON information).
    t = ""

    # Loop over the datasets.
    for run_id in sorted(jds.keys()):

        ## The dataset JSON information.
        jd = jds[run_id]

        # The start time second, sub-second, and Pixelman timestamp.
        st_s, st_sub, st_str = getPixelmanTimeString(jd["start_time_s"])

        ## The total length of the run.
        Delta_T = jd["Delta_T"]

        ## The number of days in the run.
        days = int(Delta_T/(24*60*60))

        ## The (remainder) hours in the run.
        hours = int((Delta_T%(24*60*60))/(60*60))

        ## The (remainder) minutes in the run.
        mins = int((Delta_T%(60*60))/60)

        #check_s = days*(24*60*60) + hours*(60*60) + mins*(60)
        #print check_s, Delta_T

        ## String representing the run length.
        Delta_T_str = "%3d days, %3d hours, %2d mins." % (days, hours, mins)

        # Add the dataset information to the table.
        t += '''
      <tr>
        <td>%s</td>
        <!-- <td>%s</td> -->
        <td class="number">%d</td>
        <td class="number">%d</td>
        <td>%s</td>
        <td>%s</td>
        <td class="number">%.2f</td>
        <td class="number">%.4f</td>
        <td>%s</td>
      </tr>
''' % \
            (run_id, jd["chip_id"], jd["n_frames"], jd["file_size"], st_str, Delta_T_str, jd["Delta_t"], jd["delta_t"], jd["file_name"])

    # Add the table contents.
    s = s.replace('{{TABLE_ROWS}}', t)

    # Add the CSS inline to the web page.
    s = s.replace('{{CSS}}', make_css())

    return s


def make_css():
    """ Add the web page CSS - see The Woork Handbook (A. Lupetti). """

    ## The CSS string to return.
    s = '''
/* ----------------------- */
/* STANDARD HTML TAG RESET */
/* ----------------------- */
  body,
  h1, h2, h3,
  p, ul, li,
  form {
    border:0;
    margin:0px;
    padding:0px;
  }

/* ---------------------------- */
/* STANDARD HTML TAG DEFINITION */

  body, form, input {
    color:#000000;
    font-family:Arial, Helvetica, sans-serif;
    font-size:12px;
    color:#000000;
  }

  h1{font-size:24px;}

  h2{font-size:18px;}

  h3{font-size:13px;}

  a:link, a:visited{
    color:#0033CC;
  }

  table{
    color: #222222;
    border-collapse: collapse;
    border-spacing: 0;
    margin: 20px;
    width: 90%;
  }

  td, th {
    border: 1px solid #cccccc;
    /* height: 30px; */
    transition: all 0.3s;
    padding: 5px;
  }

  th {
    background: #e2e2e2;
    font-weight: bold;
  }

  td{
    background: #f5f5f5;
    font-family: Monospace;
  }

  td.number {
    text-align:right;
  }

  tr:nth-child(even) td {
    background: #f5f5f5;
  }

  tr:nth-child(odd) td {
    background: #fcfcfc;
  }

  tr td:hover {
    background: #778877;
    color: #ffffff;
  }

/* ----------------------------*/
/* PAGE ELEMENTS               */
/* ----------------------------*/
  #container{
    margin: 30px auto;
    width:100%;
  }

/* ---------------------------*/
/* FOOTER                     */
  #footer{
    clear:both;
    color:#666666;
    font-size:11px;
    text-align:center;
  }

/* ---------------------------*/
/* CUSTOM                     */
  .caption {
    font-family:Arial, Helvetica, sans-serif;
    text-align:center;
  }
'''

    return s


def make_plot_page(plot_names):

    """
    Make a plot profile page.

    @param [in] plot_names Dictionary of plot names { month_id:path }.
    """

    ## The string to return for the page.
    s = '''<!DOCTYPE html>
<html>
<head>
  <!-- <link rel="stylesheet" type="text/css" href="main.css"> -->
  <style>
{{CSS}}
  </style>
</head>
<div id="container">

  <!-- Main Content -->
  <div id="main">
    <table>

{{TABLE_ROWS}}
    </table>
  </div>

  <!-- Footer -->
  <div id="footer">&copy; CERN@school 2015</div>

</div>
</html>
'''

    ## The table contents (generated from the supplied dictionary).
    t = "      <tr>"

    # Loop over the plots.
    for i, month_id in enumerate(sorted(plot_names.keys())):

        # Add the image tag to the table.
        t += "<td><img src=\"%s\" /></td>" % (plot_names[month_id])

    t += "</tr>"

    # Add the month and year captions.
    t += "      <tr>"

    # Loop over the plots.
    for i, month_id in enumerate(sorted(plot_names.keys())):

        ## The time of the month.
        month_time = time.strptime(month_id, "%Y-%m")

        t += "<td class=\"caption\">%s</td>" % (time.strftime("%B %Y", month_time))

    t += "</tr>"

    # Add the table contents.
    s = s.replace('{{TABLE_ROWS}}', t)

    # Add the CSS inline to the web page.
    s = s.replace('{{CSS}}', make_css())

    return s
