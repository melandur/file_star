import os
import sys

from nicegui import native, ui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_star.gui.gui import FileStar

FileStar()()
ui.run(reload=True, port=native.find_open_port())
