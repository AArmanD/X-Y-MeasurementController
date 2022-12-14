"""Module for starting the X-Y-Measurement controller. Initializes logger, then opens the start window
"""

import logging.handlers
import sys
import os

import start_window

# set whether the logger outputs into the console or in a file
ENABLE_DEBUGGING_CONSOLE = True

# set logging level -> there are DEBUG, INFO, WARNING, ERROR and CRITICAL
LEVEL = logging.INFO

if ENABLE_DEBUGGING_CONSOLE:

    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=LEVEL, stream=sys.stdout)
else:

    # if ENABLE_DEBUGGING_CONSOLE is False, write logger output into file
    handler = logging.handlers.RotatingFileHandler(os.getcwd() + os.sep + "measurementcontroller.log", 'a', 5 * 1024 * 1024, 10)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(LEVEL)
    root.addHandler(handler)

start_win = start_window.StartWindow()
start_win.mainloop()
