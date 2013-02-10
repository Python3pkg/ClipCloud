import sys


class Message:
    def __init__(self, in_user_mode=True):
        self.in_user_mode = in_user_mode

    def message(self, text, type=1):
        """
        Display some text intended for a human to read

        Arguments:
        - text: the test to display
        - in_user_mode: a boolean defining whether the program is being run by a human
        If it is then information about the program should be shown.
        If not, then the program is being used as part of a script or the output is being piped
        to another program, so user messages should not be shown.
        """

        if self.in_user_mode:
            if type == 1:
                print text
            elif type == 2:
                sys.stderr.write(text + '\n')
