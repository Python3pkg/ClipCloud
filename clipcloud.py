#!/usr/bin/env python
#
# ######################################################################
#
#  CCC  L     III  PPP    CCC  L      OO   U  U  DDD            #       
# C     L      I   P  P  C     L     O  O  U  U  D  D     ##   ###  #   
# C     L      I   PPP   C     L     O  O  U  U  D  D    #### #######   
#  CCC  LLLL  III  P      CCC  LLLL   OO    UU   DDD    ############### 
#
# ######################################################################
# (c) 2011-2012 Giles Lavelle GPLv3
#

# for interacting with the file system
import os

# for parsing command-line arguments and options
from sys import argv
from optparse import OptionParser

from lib.main import main
from lib.settings import *


def clipcloud():
    """
    Wrapper around the rest of the program's functionality.
    Receives the command line parameters and passes them on to be processed.
    Also does some other stuff that needs to be done every time the program runs.
    """

    # Create the folder for storing screenshots if it doesnt exist.
    if not os.path.exists(SCREENSHOT_PATH):
        os.makedirs(SCREENSHOT_PATH)

    # Create the folder for storing temporary files if it doesnt exist.
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    # Add command line options
    parser = OptionParser()

    parser.add_option('-s', '--share', dest='share',
        help="share a link to the file to a social media site",
        metavar='SHARE', default='clipboard', choices=SHARING_SERVICES)

    parser.add_option('-l', '--limit', dest='limit', type='int',
        help="The number of records in the history database to show",
        metavar='LIMIT', default=10)

    parser.add_option('-d', '--direction', dest='direction',
        help="The direction to sort the results by - ascending or descending",
        metavar='DIR', default='a', choices=['a', 'd'])

    parser.add_option('-t', '--sort-by', dest='sort_by',
        help="The field to sort the history results by",
        metavar='SORT', default='id', choices=['id', 'url', 'path', 'timestamp'])

    parser.add_option('-b', '--start', dest='start', type='int',
        help="The ID of the record to start the history table at",
        metavar='START', default=1)

    # The Dropbox file viewer has inbuilt syntax highlighting so the file extension is relevant
    parser.add_option('-e', '--extension', dest='extension',
        help="The extension of the file to save the snippet of text to",
        metavar='EXT', default='txt')

    parser.add_option('-m', '--mode', dest='mode',
        help="The way the area of the screen to be captured is defined",
        metavar='MODE', default='screen', choices=['screen', 'draw'])

    options, args = parser.parse_args()

    # finally send the command line arguments off to be processed
    main(argv, options)

clipcloud()
