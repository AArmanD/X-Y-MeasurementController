"""Module for managing the start window

Contains class StartWindow for that purpose

    Usage:
        start_window = StartWindow -> starts the start window
        start_window.mainloop() -> start main loop of the start window
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import matplotlib.pyplot as plt
import json
import pandas as pd
import os

import src.progress_window as progress_window

class StartWindow(tk.Tk):
    """Class which controls the start window in which measurement configuration can be inputted/exported and
    a measurement can be started
    """

    def __init__(self):
        """This function initializes the configuration window for the measurement
        """

        super().__init__()

        # set title
        self.title("X-Y Measuring progam")
        
        # create menu bar
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        options_menu = tk.Menu(menu_bar, tearoff=False)
        options_menu.add_command(label="Import measuement configuration", underline=0, command=self._read_configuration_from_json)
        options_menu.add_command(label="Export measurement configuration", underline=0, command=self._write_configuration_to_json)
        options_menu.add_command(label="Show measurement graph", underline=0, command=self._print_data_graph)
        options_menu.add_command(label="Exit", underline=0, command=self.destroy)

        menu_bar.add_cascade(label="Options", underline=0, menu=options_menu)
        
        # add icon
        self.iconbitmap('res/icon.ico')
    
        # create field for storing input variables
        self.input_fields = dict()

        # configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
    
        # initialize Labels and input fields
        output_label_1 = tk.Label(
            self,
            text="Conversion factor of voltage to power",
            font=("Arial", 10),
        )
        output_label_1.grid(column=0, row=0, sticky="w")
        

        self.input_fields["conversion_factor"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["conversion_factor"].grid(column=1, row=0, sticky="e")
    
        output_label_2 = tk.Label(
            self,
            text="Number of measurement runs:",
            font=("Arial", 10),
        )
        output_label_2.grid(column=0, row=1, sticky="w")

        self.input_fields["number_of_measurement_runs"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["number_of_measurement_runs"].grid(column=1, row=1, sticky="e")
    
        output_label_3 = tk.Label(
            self,
            text="Number of measurements at one position:",
            font=("Arial", 10),
        )
        output_label_3.grid(column=0, row=2, sticky="w")

        self.input_fields["number_of_measurements_in_one_position"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["number_of_measurements_in_one_position"].grid(column=1, row=2, sticky="e")
    
        output_label_4 = tk.Label(
            self,
            text="X-start-value in mm:",
            font=("Arial", 10),
        )
        output_label_4.grid(column=0, row=3, sticky="w")

        self.input_fields["x_start_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["x_start_value"].grid(column=1, row=3, sticky="e")

        output_label_5 = tk.Label(
            self,
            text="X-end-value in mm:",
            font=("Arial", 10),
        )
        output_label_5.grid(column=0, row=4, sticky="w")

        self.input_fields["x_end_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["x_end_value"].grid(column=1, row=4, sticky="e")
    
        output_label_6 = tk.Label(
            self,
            text="Y-start-value in mm:",
            font=("Arial", 10),
        )
        output_label_6.grid(column=0, row=5, sticky="w")

        self.input_fields["y_start_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["y_start_value"].grid(column=1, row=5, sticky="e")
    
    
        output_label_7 = tk.Label(
            self,
            text="Y-end-value in mm:",
            font=("Arial", 10),
        )
        output_label_7.grid(column=0, row=6, sticky="w")

        self.input_fields["y_end_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["y_end_value"].grid(column=1, row=6, sticky="e")
    
        output_label_8 = tk.Label(
            self,
            text="Delta X-value in mm:",
            font=("Arial", 10),
        )
        output_label_8.grid(column=0, row=7, sticky="w")

        self.input_fields["delta_x_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["delta_x_value"].grid(column=1, row=7, sticky="e")
    
        output_label_9 = tk.Label(
            self,
            text="Delta Y-value in mm:",
            font=("Arial", 10),
        )
        output_label_9.grid(column=0, row=8, sticky="w")

        self.input_fields["delta_y_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["delta_y_value"].grid(column=1, row=8, sticky="e")


        output_label_9 = tk.Label(
            self,
            text="Wait time before each measurement in s:",
            font=("Arial", 10),
        )
        output_label_9.grid(column=0, row=9, sticky="w")

        self.input_fields["wait_time"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["wait_time"].grid(column=1, row=9, sticky="e")

    
        self.start_btn = tk.Button(
            self,
            text="Start measurement",
            font=("Arial", 10),
            command=self._start_measurement,
        )

        self.start_btn.grid(column=0, row=11, columnspan=2, pady=15)

        # prevent gui resize
        self.resizable(False, False)

    def _start_measurement(self):
        """This function creates a progress bar window which starts the measurement process
        """

        # read in the measurement configuration
        measurement_configuration = self._read_configuration()

        # if measurement configuration not valid, return
        if(not measurement_configuration):
            return

        # disable start measurement button
        self.start_btn['state'] = tk.DISABLED

        # start progress window
        progress_window.ProgressWindow(self, **measurement_configuration)

        # enable start measurement button after measurement again
        self.start_btn['state'] = tk.NORMAL


    def _read_configuration(self):
        """This function reads in the entered configuration from the input fields into a dictionary which then is returned

        Returns:
            Dict: Dictionary with read in measurement configuration data
        """

        measurement_configuration = dict()

        try:
            measurement_configuration["conversion_factor"] = int(self.input_fields["conversion_factor"].get())
            measurement_configuration["number_of_measurement_runs"] = int(self.input_fields["number_of_measurement_runs"].get())
            measurement_configuration["number_of_measurements_in_one_position"] = int(self.input_fields["number_of_measurements_in_one_position"].get())
            measurement_configuration["x_start_value"] = int(self.input_fields["x_start_value"].get())
            measurement_configuration["x_end_value"] = int(self.input_fields["x_end_value"].get())
            measurement_configuration["y_start_value"] = int(self.input_fields["y_start_value"].get())
            measurement_configuration["y_end_value"] = int(self.input_fields["y_end_value"].get())
            measurement_configuration["delta_x_value"] = float(self.input_fields["delta_x_value"].get())
            measurement_configuration["delta_y_value"] = float(self.input_fields["delta_y_value"].get())
            measurement_configuration["wait_time"] = float(self.input_fields["wait_time"].get())

        except ValueError:
            messagebox.showerror("Error", "Error in reading in configuration")
            return None
        
        # check whether values are in correct range
        if(not(measurement_configuration["x_start_value"] >= 0) or not(measurement_configuration["x_start_value"] <= 52)):
            messagebox.showerror("Error", "Error: x start value " + str(measurement_configuration["x_start_value"]) + " not in a valid range")
            return None
        
        if(not(measurement_configuration["x_end_value"] >= 0) or not(measurement_configuration["x_end_value"] <= 52)):
            messagebox.showerror("Error", "Error: x end value " + str(measurement_configuration["x_end_value"]) + " not in a valid range")
            return None

        if(not(measurement_configuration["y_start_value"] >= 0) or not(measurement_configuration["y_start_value"] <= 52)):
            messagebox.showerror("Error", "Error: y start value " + str(measurement_configuration["y_start_value"]) + " not in a valid range")
            return None

        if(not(measurement_configuration["y_end_value"] >= 0) or not(measurement_configuration["y_end_value"] <= 52)):
            messagebox.showerror("Error", "Error: y end value " + str(measurement_configuration["y_end_value"]) + " not in a valid range")
            return None

        if((measurement_configuration["delta_x_value"] <= 0.005) or ((measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) < measurement_configuration["delta_x_value"])):
            messagebox.showerror("Error", "Error: delta x value " + str(measurement_configuration["delta_x_value"]) + " not in a valid range")
            return None
        
        if((measurement_configuration["delta_y_value"] <= 0.005) or ((measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) < measurement_configuration["delta_y_value"])):
            messagebox.showerror("Error", "Error: delta y value " + str(measurement_configuration["delta_y_value"]) + " not in a valid range")
            return None

        # check whether start value is greater than end value
        if(not(measurement_configuration["x_end_value"] > measurement_configuration["x_start_value"])):
            messagebox.showerror("Error", "Error: x start value " + str(measurement_configuration["x_start_value"]) + " is greater than or equal to x end value")
            return None

        if(not(measurement_configuration["y_end_value"] > measurement_configuration["y_start_value"])):
            messagebox.showerror("Error", "Error: y start value " + str(measurement_configuration["y_start_value"]) + " is greater than or equal to y end value")
            return None

        return measurement_configuration

    def _read_configuration_from_json(self):
        """This function reads in a measurement configuration file and writes the values into the input fields
        """

        # get path to file
        filepath = filedialog.askopenfilename(
            title='Open file',
            filetypes=(('Configuration files','*.json'),('All formats','*.*')),
            initialdir=os.getcwd() + os.sep + "measurement_configurations"
        )

        # if cancel is pressed, exit the process
        if not filepath:
            return

        config = dict()

        # open json file
        with open(filepath, mode='r') as json_file:
            config = json.load(json_file)

        for key in config:

            # clear input field
            self.input_fields[key].delete(0,tk.END)

            # write appropriate value into input field
            self.input_fields[key].insert(0, config[key])
        
    def _write_configuration_to_json(self):
        """This function writes measurement configuration from the input fields into a json file
        """

        # check whether the values in the inputs are valid by reading them in
        measurement_configuration = self._read_configuration()

        # if the measurement configuration values are not valid, return without saving
        if(not measurement_configuration):
            return

        # open file dialog for choosing the save path, file object is returned
        file = filedialog.asksaveasfile(
            mode='w', 
            defaultextension=".json", 
            filetypes=(('Configuration files','*.json'),('All formats','*.*')),
            initialdir=os.getcwd() + os.sep + "measurement_configurations"
            )
        
        # return if file dialog was closed with "cancel"
        if file is None:
            return

        # write the measurement configuration into the file object
        json.dump(measurement_configuration, file)

        # close the json file
        file.close()

    def _print_data_graph(self):
        """This function prints out a graph of the measured data
        """

        # get path to file
        filepath = filedialog.askopenfilename(
            title='Open file',
            filetypes=(('Measurement data','*.csv'),('All formats','*.*')),
            initialdir=os.getcwd() + os.sep + "measurement_data"
        )

        # if cancel is pressed, exit the process
        if not filepath:
            return

        # read data out of the csv file into a pandas dataframe
        df = pd.read_csv(filepath)

        # set the data for plotting
        axes = plt.axes(projection="3d")
        axes.scatter3D(df['ypos'].to_numpy(), df['xpos'].to_numpy(), df['measure'].to_numpy(), color="blue")

        # set the labels in the plot window
        axes.set_title("3D-Diagram of the measured values")
        axes.set_xlabel("X-Coordinates in mm", fontsize=6)
        axes.set_ylabel("Y-Coordinates in mm", fontsize=6)
        axes.set_zlabel("Average of measured Power per Position in W", fontsize=6)

        # set the icon of the plot
        current_fig_manager = plt.get_current_fig_manager()
        current_fig_manager.window.wm_iconbitmap('res/icon.ico')

        # set size of tick parameters to be smaller, so nothing overlaps
        plt.tick_params(axis='x', which='major', labelsize=6)
        plt.tick_params(axis='y', which='major', labelsize=6)
        plt.tick_params(axis='z', which='major', labelsize=6)

        # plt.rcParams.update({'font.size': 12})
        plt.tight_layout()
        plt.show()
