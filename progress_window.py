import tkinter as tk
from tkinter import ttk
import pyvisa
from pipython import GCSDevice, pitools
import numpy as np
import math
import logging
import threading
import pandas as pd
import time


_logger = logging.getLogger(__name__)

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']

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
        self.main_thread = threading.Thread(target=self._test_progress_bar, daemon=True)

        # create and start measure thread
        #self.main_thread = Thread(target=lambda: self._control_xy_table(**measurement_configuration))

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

    def _control_xy_table(self, **measurement_configuration):
        """This method controls the movement of the xy-table, starts mesurements and saves the results of
        measurement runs

        Args:
            measurement_configuration (dict): Dictonary with measurment configuration
        """
    
        # Calculate number of x and y values
        Anzahl_Y = int((measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"])
        Anzahl_X = int((measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"])

        # Allocate memory space for arrays
        xpositionvalues = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)
        ypositionvalues = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)
        measurements = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)

        # make calculations for progress bar step size
        stepsize = 100/(Anzahl_X*Anzahl_Y*measurement_configuration["number_of_measurement_runs"])
        progress = 0

        # create two gsc device instances for being able to control the two step motors
        with GCSDevice() as Device1, GCSDevice() as Device2:
            
            # Fist setup of the master device which is connected via pc
            Device1.OpenUSBDaisyChain(description='0017550026')
            daisychainid = Device1.dcid
            Device1.ConnectDaisyChainDevice(1, daisychainid)
            _logger.info('Connection to DaisyChain-Master established')
            
            # Secondly enable connection to the next device in daisy chain
            Device2.ConnectDaisyChainDevice(2, daisychainid)
            _logger.info('Connection to DaisyChain-Slave established')
            
            # A lot of initializing information
            _logger.info('Connected to devices with IDs')
            _logger.info('\n{}:\n{}'.format(Device1.GetInterfaceDescription(), Device1.qIDN()))
            _logger.info('\n{}:\n{}'.format(Device2.GetInterfaceDescription(), Device2.qIDN()))


            _logger.info('Initialization of axes...')

            # initialize axes
            pitools.startup(Device1, stages=STAGES, refmodes=REFMODES)
            pitools.startup(Device2, stages=STAGES, refmodes=REFMODES)

            _logger.info('Min y-axis:', Device1.qTMN())
            _logger.info('Max y-axis:', Device1.qTMX())

            _logger.info('Min x-axis 2:', Device2.qTMN())
            _logger.info('Max x-axis 2:', Device2.qTMX())


            # run the ammount of configured measuremnts
            for i in range(measurement_configuration["number_of_measurement_runs"]): 
                
                _logger.info('In {}. measurement run'.format(i))

                # reset of the y and x axis to start point
                Device1.MOV(1, measurement_configuration["y_start_value"])
                pitools.waitontarget(Device1, axes=1)

                Device2.MOV(1, measurement_configuration["x_start_value"])
                pitools.waitontarget(Device2, axes=1)

                # wait so the table doesnt shake anymore
                self.stopped.wait(timeout=5)

                # cycle through the amount of measurement points with measurementcounter
                measurementcounter = 0

                for currentystep in range(0, Anzahl_Y):

                    # cycle through the amount of meassurement points on the x axis
                    for currentxstep in range(0, Anzahl_X):
                        
                        currentyposition = Device1.qPOS(1)[1]
                        currentxposition = Device2.qPOS(1)[1]
                        
                        # Measurement save to array
                        measurements[measurementcounter] = self._make_measurement(**measurement_configuration)
                        xpositionvalues[measurementcounter] = currentxposition 
                        ypositionvalues[measurementcounter] = currentyposition
                        
                        _logger.debug('Actual Data: x-pos: {:.2f} y-pos: {:.2f} reading: {:.2f}'.format(currentyposition, currentxposition, measurements[measurementcounter]))

                        measurementcounter = measurementcounter + 1

                        if(self.stopped.is_set()):

                            # todo check whether that works
                            _logger.info('Close daisy chain connection')
                            Device2.CloseDaisyChain()
                            Device1.CloseDaisyChain()
                            return

                        # as long as not last measurement
                        if currentxstep < (Anzahl_X - 1 ):
                            
                            # this instead of using currentposition avoids error propagation
                            theoreticalposition = (currentxstep + 1) * measurement_configuration["delta_x_value"] 
                            nextxposition = theoreticalposition + measurement_configuration["delta_x_value"]

                            # Move to next X Meassurepoint
                            Device2.MOV(1, nextxposition)
                            pitools.waitontarget(Device2, axes=1)

                            # timer to wait so the table doesnt shake anymore
                            self.stopped.wait(timeout=5)       

                        # update progress bar in gui
                        progress = progress + stepsize
                        self.progress_bar['value'] = math.ceil(progress)
                        self.value_label['text'] = self._update_progress_label()

                    # as long as not last measurement
                    if currentystep < (Anzahl_Y - 1 ):
                        
                        # this instead of using currentposition avoids error propagation
                        theoreticalposition = (currentystep + 1) * measurement_configuration["delta_y_value"] 
                        nextyposition = theoreticalposition + measurement_configuration["delta_y_value"]

                        # Move to next Y Meassurepoint
                        Device1.MOV(1, nextyposition)
                        pitools.waitontarget(Device1, axes=1)

                    # Reset to "beginning of line" for next measurement
                    Device2.MOV(1, measurement_configuration["x_start_value"])
                    pitools.waitontarget(Device2, axes=1)

                
                _logger.info('Saving measurement run results...')

                # Save measurement results
                df = pd.DataFrame({"xpos" : xpositionvalues, "ypos" : ypositionvalues, "measure" : measurements})
                df.to_csv(f"Measurementrun {i}.csv", index=False)
            
            _logger.info("Close daisy chain connection")

            # close the daisy chain connection
            Device2.CloseDaisyChain()
            Device1.CloseDaisyChain()

    def _make_measurement(self, **measurement_configuration):
        """This function performs the local measurement. If more then one measurement is taken the mean of all saved values is returned.

        Args: 
            measurement_configuration (dict): Dictonary with measurment configuration

        Returns:
            float: power value of performed measurement
        """

        # connect to measurement device
        rm = pyvisa.ResourceManager()
        Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
        Spannungsmeasurements = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)
    
        # make specified number of measurements
        for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
            Spannungsmeasurements[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )
    
        # calculate mean value from measurements
        Leistungsmesswert = np.mean(measurement_configuration["conversion_factor"] * Spannungsmeasurements)

        return Leistungsmesswert