import os
import subprocess
from settings import *
try:
    import wx
except ImportError as e:
    if DEBUG:
        print 'Wxpython is not available, custom screenshot dimensions not available'


class ScreenshotArea(wx.Frame):
    def __init__(self):
        style = (wx.STAY_ON_TOP | wx.RESIZE_BORDER)
        wx.Frame.__init__(self, None, style=style)
        #self.SetClientSize(frame.size)
        self.Move(wx.Point(200, 200))
        self.SetTransparent(128)
        #self.Bind(wx.EVT_MOTION, self.OnMouse)
        self.Bind(wx.EVT_KEY_UP, self.keypress)
        self.Show(True)

    def keypress(self, event):
        global size
        global pos
        if event.GetKeyCode() == wx.WXK_RETURN:
            size = self.GetClientRect()
            pos = self.GetPosition()
            self.Close(force=True)
        else:
            event.Skip()

    # def OnMouse(self, event):
    #     """implement dragging"""
    #     if not event.Dragging():
    #         self._dragPos = None
    #         return
    #     self.CaptureMouse()
    #     if not self._dragPos:
    #         self._dragPos = event.GetPosition()
    #     else:
    #         pos = event.GetPosition()
    #         displacement = self._dragPos - pos
    #         self.SetPosition(self.GetPosition() - displacement)


def draw_rect():
    app = wx.App(False)
    print 'Please resize the rectangle to cover the area you wish to capture in your screenshot, then press enter'
    ScreenshotArea()
    app.MainLoop()


def capture(mode):
    """
    Invoke the C# app that takes the screenshot
    Returns: the path to the image file that the screenshot was saved to
    """

    if mode == 'screen':
        filename = subprocess.check_output([UTILS_SCRIPT, 'screenshot'], shell=True)
        filename = filename[:-2]  # trim line breaks
        path = os.path.join(SCREENSHOT_PATH, filename)
    elif mode == 'draw':
        draw_rect()
        filename = subprocess.check_output([UTILS_SCRIPT, 'screenshot', pos.x, pos.y, size.width, size.height])
        print filename

    return path, filename
