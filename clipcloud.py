#!/usr/bin/env python
#
# (c) 2011-2013 Giles Lavelle GPLv3

import os
from argparse import ArgumentParser

from main import *
from settings import *


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
    # Create the master argument parser instance
    parser = ArgumentParser(description=HELP_MESSAGE)

    # Add any global options - ones that apply to all tools
    parser.add_argument('-s', '--share', dest='share',
        help="share a link to the file to a social media site",
        default='clipboard', choices=SHARING_SERVICES)

    # Create the subparsers for each of the program's separate tools
    subparsers = parser.add_subparsers()

    # Create the parser for options that only apply to uploading files and folders
    upload_parser = subparsers.add_parser('up')
    upload_parser.add_argument('filepaths', nargs='+')
    upload_parser.set_defaults(func=upload)

    # Create the parser for options that only apply to revisiting old uploads
    revisit_parser = subparsers.add_parser('revisit')
    revisit_parser.add_argument('operation',
        choices=['local', 'remote', 'upload'])
    revisit_parser.add_argument('id', type=int)
    revisit_parser.set_defaults(func=revisit)

    # Create the parser for options that only apply to sharing text snippets
    text_parser = subparsers.add_parser('text')
    text_parser.add_argument('-v', '--text-service', dest='text',
        help="The hosting service to upload text snippets to",
        default='dropbox', choices=['dropbox'])
    # The Dropbox file viewer has inbuilt syntax highlighting so the file extension is relevant
    text_parser.add_argument('-e', '--extension', dest='extension',
        help="The extension of the file to save the snippet of text to",
        default='txt')
    text_parser.set_defaults(func=snippet)

    # Create the parser for options that only apply to taking screenshots
    screenshot_parser = subparsers.add_parser('snap')
    screenshot_parser.add_argument('-m', '--mode', dest='mode',
        help="The way the area of the screen to be captured is defined",
        default='screen', choices=['screen', 'draw'])
    screenshot_parser.set_defaults(func=screenshot)

    # Create the parser for options that only apply to viewing the history
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('-l', '--limit', dest='limit', type=int,
        help="The number of records in the history database to show",
        default=10)
    history_parser.add_argument('-d', '--direction', dest='direction',
        help="The direction to sort the results by - ascending or descending",
        default='a', choices=['a', 'd'])
    history_parser.add_argument('-t', '--sort-by', dest='sort_by',
        help="The field to sort the history results by",
        default='id', choices=['id', 'url', 'path', 'timestamp'])
    history_parser.add_argument('-b', '--start', dest='start', type=int,
        help="The ID of the record to start the history table at",
        default=1)
    history_parser.set_defaults(func=history)

    # finally parse all arguments run the relevant function
    args = parser.parse_args()
    args.func(args)


def main():
        # If program execution time is being measured, call the main function from a timer
        # if TIMER_ACTIVATED:
        #     from timeit import Timer
        #     t = Timer('clipcloud.clipcloud()', 'import clipcloud')
        #     print t.timeit(number=1)
        # Otherwise just call it
        # else:
    clipcloud()
if __name__ == '__main__':
    main()
