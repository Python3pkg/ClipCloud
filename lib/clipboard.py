from Tkinter import Tk


class Clipboard:
    def get(self):
        """Return the contents of the user's clipboard if it is plain text"""
        try:
            return Tk().clipboard_get()
        except:
            print 'Could not get the contents of the clipboard.\n' + \
                'Are you sure that you currently have only plain text copied?'
            return None

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
