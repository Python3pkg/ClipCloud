from subprocess import check_output
from settings import UTILS_SCRIPT

def capture(self, dimensions=None):
    """
    Invoke the C# app that takes the screenshot
    Returns: the path to the image file that the screenshot was saved to
    """
    path = check_output([UTILS_SCRIPT, 'screenshot'], shell=True)
    return path[:-2]  # trim line breaks