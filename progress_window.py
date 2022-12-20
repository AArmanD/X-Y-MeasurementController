"""Module for managing the progress window

Contains class ProgressWindow for that purpose

    Usage:
        progress_window = ProgressWindow() -> starts progress window, which also directly starts the measurements
"""

import tkinter as tk
from tkinter import ttk
import threading

import measurement_functions


class ProgressWindow(tk.Toplevel):
    """Class which controls the measurement and shows it in a progress bar window
    """

    def __init__(self, parent, **measurement_configuration):
        """This is the constructor for the progress bar window, also starts the xy-Table-controller function

        Args:
            parent (StartWindow): Instance of the start window, used for initializing super class
            measurement_configuration (Dict): Dictionary with the configuration for the measurement
        """

        super().__init__(parent)

        # set title
        self.title("Measuring...")

        # set window size
        self.geometry('300x120')

        # add icon
        self.wm_iconphoto(False, tk.PhotoImage(file = 'icon.png'))
        
        # configure window layout to be a grid
        self.grid()

        # define and place the progress bar
        self.progress_bar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280
        )
        self.progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        # define and place label which shows progress
        self.value_label = ttk.Label(self, text=self._update_progress_label())
        self.value_label.grid(column=0, row=1, columnspan=2)

        # define and place label which stops measurement
        stop_button = ttk.Button(
            self,
            text='Stop',
            command=self._stop_program,
        )
        stop_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)

        # prevent window to be resizable
        self.resizable(False, False)

        # set up thread flag
        self.stopped = threading.Event()
        self.stopped.clear()

        # for test purposes (should be removed at final release)
        # self.main_thread = threading.Thread(target=self._test_progress_bar, daemon=True)

        # create and start measure thread
        self.main_thread = threading.Thread(target=lambda: measurement_functions.control_xy_table(self ,**measurement_configuration))

        # start measuring thread
        self.main_thread.start()

        # set x button to call stop_program
        self.protocol('WM_DELETE_WINDOW', self._stop_program)

        # start window main loop
        self.mainloop()

    def _update_progress_label(self):
        """This function generates a string for the progress label

        Returns:
            String: String for the progress label
        """
        return f"Current Progress: {self.progress_bar['value']}%"

    def _stop_program(self):
        """This function stops the measurement and closes the progress bar window
        """
        
        # set stop flag, which also eliminates wait times in the thread and join the measurement thread to the main thread
        self.stopped.set()
        self.main_thread.join(0.1)

        # destroys the window
        self.destroy()

        # quits the mainloop
        self.quit()

    def _test_progress_bar(self):
        """This function is for test purposes to check whether the progress bar window works as wanted 
        (will be removed in final release)
        """
        
        for i in range(0,100):

            self.progress_bar['value'] = i
            self.value_label['text'] = self._update_progress_label()

            self.stopped.wait(timeout=1)

            if self.stopped.is_set():
                return

    def get_thread_flag(self):
        """Getter for the thread flag

        Returns:
            Event: Thread event flag
        """

        return self.stopped

    def update_progress_bar(self, value):
        """This method sets the progress bar to a specific value

        Args:
            value (int): Value to which the progress bar should be set
        """
        self.progress_bar['value'] = value
        self.value_label['text'] = self._update_progress_label()
        
    def close_progress_window_after_finish(self):
        
        # destroys the window
        self.destroy()

        # quits the mainloop
        self.quit()