import os
from settings import *
from time import time
import subprocess


class Screenshot:
    def __init__(self, mode):
        if PLATFORM != 'Darwin':
            print 'Screenshot tool only works on OS X'
            exit(1)

        self.flags = self.build_flags(mode)
        self.filename = self.build_filename()
        self.path = os.path.join(SCREENSHOT_PATH, self.filename)

    def build_flags(self, mode):
        flags = '-'

        # Don't play camera shutter sound effect
        flags += 'x'

        flags += 'm' if mode == 'screen' else 'i'

        return flags

    def build_filename(self):
        return 'screenshot_%s.png' % str(int(time()))

    def capture(self):
        """
        Take a screenshot

        Arguments:
        - mode: The type of screenshot to capture, either the entire screen or a custom rectangle

        Returns the path to the image file that the screenshot was saved to
        and the name of the file without the full path
        """

        subprocess.call(['screencapture', self.flags, self.path])
