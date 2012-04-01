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

# for setting the clipboard
from Tkinter import Tk

# for opening pages to share the links
import webbrowser

# for uploading to Dropbox
from dropbox.dropbox import Dropbox

# for parsing the arguments passed to the program when invoked from the command line
from lib.parse_args import parse_args
from lib.history import History
from lib.settings import *

SHARING_SERVICES = 'clipboard facebook twitter email'.split(' ')
SHARE_MESSAGE = 'I just uploaded a file to ClipCloud - check it out.'
URLS = {
    'twitter': "https://twitter.com/intent/tweet?text=%s&url=%s",
    'facebook': "http://www.facebook.com/sharer.php?u=%s&t=%s",
    'email': "mailto:%s%s"
}


class ClipCloud:
    """
    Sweet class for miscellaneous methods
    """
    def __init__(self):
        """
        Perform various actions that need to be run every time the program runs
        """

        # Create the folder for storing screenshots if it doesnt exist.
        if not os.path.exists(SCREENSHOT_PATH):
            os.makedirs(SCREENSHOT_PATH)

        # Add command line options
        parser = OptionParser()
        parser.add_option('-s', '--share', dest='share',
            help="share a link to the file to a social media site",
            metavar='SHARE', default='clipboard', choices=SHARING_SERVICES)

        (options, args) = parser.parse_args()

        parse_args(argv, self, options.share)

    def set_clipboard(self, link):
        """
        Set the contents of the user's clipboard to a string
        Arguments:
            link: the url of the uploaded file to set the clipboard to
        """
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(link)
        r.destroy()

    def handle_file(self, path, filename, share_to):
        """
        Respond to the event of the user attempting to upload a file,
        be it a screenshot, text snippet or generic file.
        """
        # upload the file,
        link = Dropbox().upload(path, filename)

        # save a record of it to the history,
        History().add(path, link)

        # and then send the link to its destination, be that clipboard or social network.
        if share_to == 'clipboard':
            self.set_clipboard(link)
            return

        url = URLS[share_to] % (SHARE_MESSAGE, link)

        webbrowser.open(url, new=2)

ClipCloud()
