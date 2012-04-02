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

    (options, args) = parser.parse_args()

    # finally send the command line arguments off to be processed
    main(argv, options.share)

clipcloud()
