import os
from settings import *
from time import time
import wx


class ScreenshotArea(wx.Frame):
    def __init__(self):
        style = (wx.STAY_ON_TOP | wx.RESIZE_BORDER)
        wx.Frame.__init__(self, None, style=style)

        #self.SetClientSize()
        self.Move(wx.Point(200, 200))
        self.SetTransparent(128)

        #self.Bind(wx.EVT_MOTION, self.OnMouse)  # enabling moving the window breaks resizing.
        self.Bind(wx.EVT_KEY_UP, self.keypress)

        print 'Please resize the rectangle to cover the area you wish to capture in your screenshot, then press enter'

        self.Show(True)

    def keypress(self, event):
        global pos  # find a way not to do this.

        if event.GetKeyCode() == wx.WXK_RETURN:
            a, b, width, height = self.GetClientRect()
            x, y = self.GetPosition()
            pos = (x, y, width, height)

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


class Screenshot:
    def take_screenshot(self, pos=None):
        """
        Capture the pixel data of the screen and save it to a PNG filename
        Arguments
        - pos: A tuple of length 4 defining the top, left, height and width of the rectangle to capture
        If omitted it defaults to the entire screen
        """
        screen = wx.ScreenDC()

        if pos:
            x, y, width, height = pos
        else:
            x, y = 0, 0
            width, height = screen.GetSize()

        bmp = wx.EmptyBitmap(width, height)
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, width, height, screen, x, y)

        del mem  # Release bitmap data from memory

        filename = 'screenshot_' + str(int(time())) + '.png'
        path = os.path.join(SCREENSHOT_PATH, filename)
        bmp.SaveFile(path, wx.BITMAP_TYPE_PNG)

        self.path = path
        self.filename = filename

    def capture(self, mode):
        """
        Take a screenshot
        Arguments:
        - mode: The type of screenshot to capture, either the entire screen or a custom rectangle
        Returns: the path to the image file that the screenshot was saved to
        """

        self.app = wx.App(False)

        if mode == 'screen':
            self.take_screenshot()

        elif mode == 'draw':
            ScreenshotArea()
            self.app.MainLoop()
            self.take_screenshot(pos=pos)

        return self.path, self.filename
