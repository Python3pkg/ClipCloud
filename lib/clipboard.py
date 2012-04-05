from Tkinter import Tk


class Clipboard:
    def get(self):
        return Tk().clipboard_get()

    def set(self, link):
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
