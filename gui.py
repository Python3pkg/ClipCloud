from tray import SysTrayIcon
from lib.history import History

hover_text = "ClipCloud"
icon_filename = 'favicon.ico'

def show_history(sysTrayIcon):
    History().display(10, 'd')

menu_options = (
    ('Show history', None, show_history),
    ('A sub-menu', None, (
        ('Hello', None, show_history),
    ))
)

SysTrayIcon(icon_filename, hover_text, menu_options, default_menu_index=1)