import os
import sys

from nicegui import native, ui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generic_file_cleaner.gui.gui import GenericFileFilter

GenericFileFilter()()
ui.run(reload=True, port=native.find_open_port())
