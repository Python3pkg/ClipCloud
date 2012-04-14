import os
from subprocess import check_output, call, Popen
from settings import UTILS_SCRIPT, SNIPPING_TOOL, SCREENSHOT_PATH


def capture(mode):
    """
    Invoke the C# app that takes the screenshot
    Returns: the path to the image file that the screenshot was saved to
    """

    if mode == 'screen':
        filename = check_output([UTILS_SCRIPT, 'screenshot'], shell=True)
        filename = filename[:-2]  # trim line breaks
        path = os.path.join(SCREENSHOT_PATH, filename)
    elif mode == 'draw':
        call(SNIPPING_TOOL, shell=True)
        path = ''

    return path, filename
