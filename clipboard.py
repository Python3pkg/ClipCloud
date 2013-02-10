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

    def set(self, text):
        """
        Set the contents of the user's clipboard to a string

        text - The text to be copied to the clipboard
        """

        t = Tk()
        t.withdraw()
        t.clipboard_clear()
        t.clipboard_append(text)
        t.destroy()
