import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import matplotlib.pyplot as plt
import json

import progress_window

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
        options_menu.add_command(label="Show measurement graph", underline=0, command=self.destroy)
        options_menu.add_command(label="Exit", underline=0, command=self.destroy)

        menu_bar.add_cascade(label="Options", underline=0, menu=options_menu)
        
        # add icon
        photo = tk.PhotoImage(file = 'icon.png')
        self.wm_iconphoto(False, photo)
    
        # create field for storing input variables
        self.input_fields = dict()

        # configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
    
        # initialize Labels and input fields
        self.ausgabe_label1 = tk.Label(
            self,
            text="Conversion of voltage to power",
            font=("Arial", 10),
        )
        self.ausgabe_label1.grid(column=0, row=0, sticky="w")
        

        self.input_fields["conversion_factor"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["conversion_factor"].grid(column=1, row=0, sticky="e")
    
        ausgabe_label2 = tk.Label(
            self,
            text="Number of measurement runs:",
            font=("Arial", 10),
        )
        ausgabe_label2.grid(column=0, row=1, sticky="w")

        self.input_fields["number_of_measurement_runs"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["number_of_measurement_runs"].grid(column=1, row=1, sticky="e")
    
        ausgabe_label3 = tk.Label(
            self,
            text="Number of measurements at one position:",
            font=("Arial", 10),
        )
        ausgabe_label3.grid(column=0, row=2, sticky="w")

        self.input_fields["number_of_measurements_in_one_position"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["number_of_measurements_in_one_position"].grid(column=1, row=2, sticky="e")
    
        ausgabe_label4 = tk.Label(
            self,
            text="X-start-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label4.grid(column=0, row=3, sticky="w")

        self.input_fields["x_start_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["x_start_value"].grid(column=1, row=3, sticky="e")
    
        ausgabe_label5 = tk.Label(
            self,
            text="Y-start-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label5.grid(column=0, row=4, sticky="w")

        self.input_fields["y_start_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["y_start_value"].grid(column=1, row=4, sticky="e")
    
        ausgabe_label6 = tk.Label(
            self,
            text="X-end-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label6.grid(column=0, row=5, sticky="w")

        self.input_fields["x_end_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["x_end_value"].grid(column=1, row=5, sticky="e")
    
        ausgabe_label7 = tk.Label(
            self,
            text="Y-end-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label7.grid(column=0, row=6, sticky="w")

        self.input_fields["y_end_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["y_end_value"].grid(column=1, row=6, sticky="e")
    
        ausgabe_label8 = tk.Label(
            self,
            text="Delta X-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label8.grid(column=0, row=7, sticky="w")

        self.input_fields["delta_x_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["delta_x_value"].grid(column=1, row=7, sticky="e")
    
        ausgabe_label9 = tk.Label(
            self,
            text="Delta Y-value in mm:",
            font=("Arial", 10),
        )
        ausgabe_label9.grid(column=0, row=8, sticky="w")

        self.input_fields["delta_y_value"] = tk.Entry(self, font=("Arial", 10), width=10, justify="right")
        self.input_fields["delta_y_value"].grid(column=1, row=8, sticky="e")

    
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
            measurement_configuration["y_start_value"] = int(self.input_fields["y_start_value"].get())
            measurement_configuration["x_end_value"] = int(self.input_fields["x_end_value"].get())
            measurement_configuration["y_end_value"] = int(self.input_fields["y_end_value"].get())
            measurement_configuration["delta_x_value"] = float(self.input_fields["delta_x_value"].get())
            measurement_configuration["delta_y_value"] = float(self.input_fields["delta_y_value"].get())

        except ValueError:
            messagebox.showerror("Title", "Error in reading in configuration")
        
        # todo auf Wertebereiche prüfen

        return measurement_configuration

    def _read_configuration_from_json(self):
        """This function reads in a measurement configuration file and writes the values into the input fields
        """

        # get path to file
        filepath = filedialog.askopenfilename(
            title='Datei öffnen',
            filetypes=(('Konfigurations Datei','*.json'),('Alle Formate','*.*'))
        )

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
        file = filedialog.asksaveasfile(mode='w', defaultextension=".json", filetypes=(('Konfigurations Datei','*.json'),('Alle Formate','*.*')))
        
        # return if file dialog was closed with "cancel"
        if file is None:
            return

        # write the measurement configuration into the file object
        json.dump(measurement_configuration, file)

        # close the json file
        file.close()
