import tkinter as tk
from tkinter import ttk
import pyvisa
from pipython import GCSDevice, pitools
import time
import numpy as np
from pipython import GCSDevice, pitools
import math
import logging
import pandas as pd

from threading import Thread

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']

class MeasurementController(tk.Toplevel):


    def __init__(self, parent, **measurement_configuration):

        super().__init__(parent)

        self.title("Messcontroller")

        self.geometry('300x120')

        # add icon
        photo = tk.PhotoImage(file = 'icon.png')
        self.wm_iconphoto(False, photo)

        self.grid()

        # progressbar
        self.pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280
        )
        
        # place the progressbar
        self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        # label
        self.value_label = ttk.Label(self, text=self.update_progress_label())
        self.value_label.grid(column=0, row=1, columnspan=2)

        # stop button
        stop_button = ttk.Button(
            self,
            text='Stop',
            command=self.pb.stop
        )
        stop_button.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)

        # prevent window to be resizable
        self.resizable(False, False)

        # create and start measure thread
        #self.main_thread = Thread(target=self.measurement_controller, daemon=True, args=[measurement_configuration])
        self.main_thread = Thread(target=lambda: self.measurement_controller(**measurement_configuration))
        self.main_thread.start()

        self.mainloop()

    def update_progress_label(self):
        return f"Current Progress: {self.pb['value']}%"

    def test_progress_bar(self, measurement_configuration):
        logging.info("in_test_progress_bar")

        for i in range(0,100):
            time.sleep(1)
            self.pb['value'] = i
            self.value_label['text'] = self.update_progress_label()

    def measurement_controller(self, **measurement_configuration):
    
        Anzahl_Y = int((measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"])
        Anzahl_X = int((measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"])

        # Allocate memory space for arrays -> perfomannncceeeeeee
        xpositionvalues = np.zeros(Anzahl_X, dtype=float)
        ypositionvalues = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)
        measurements = np.zeros(Anzahl_Y, dtype=float)

        stepsize = 100/(Anzahl_X*Anzahl_Y*measurement_configuration["number_of_measurement_runs"])
        progress = 0

        ## Verbinden der Controller über DaisyChain
        with GCSDevice() as Device1:

            ## Set up serial connection 
            # maybe this works as well
            # https://stackoverflow.com/questions/4617034/how-can-i-open-multiple-files-using-with-open-in-python
            
            # Fist setup of the master device which is connected via pc
            Device1.OpenUSBDaisyChain(description='0017550026')
            daisychainid = Device1.dcid
            Device1.ConnectDaisyChainDevice(1, daisychainid)
            logging.info('Master DaisyChain-Verbindung ist aufgebaut')
            
            # Secondly enable connection to the next device in daisy chain
            with GCSDevice() as Device2:
                Device2.ConnectDaisyChainDevice(2, daisychainid)
                
                # A lot of initializing information
                logging.info("Gefundene Devices mit IDs")
                logging.info('\n{}:\n{}'.format(Device1.GetInterfaceDescription(), Device1.qIDN()))
                logging.info('\n{}:\n{}'.format(Device2.GetInterfaceDescription(), Device2.qIDN()))

                logging.info('DaisyChain-Verbindung ist aufgebaut')

                logging.info('Inialisierung Achsen...')
                pitools.startup(Device1, stages=STAGES, refmodes=REFMODES)
                pitools.startup(Device2, stages=STAGES, refmodes=REFMODES)

                logging.info('Min Achse 1:', Device1.qTMN())
                logging.info('Max Achse 1:', Device1.qTMX())
                logging.info('Aktuelle Position Achse 2:', Device1.qPOS())

                logging.info('Min Achse 2:', Device2.qTMN())
                logging.info('Max Achse 2:', Device2.qTMX())
                logging.info('Aktuelle Position Achse 2:', Device2.qPOS())

                # todo solve below
                for axis in Device2.axes:
                    axis2 = axis
                    break

                for axis in Device1.axes:
                    axis1 = axis
                    break

                # run the ammount of configured measuremnts
                for i in range(measurement_configuration["number_of_measurement_runs"]): 
                    
                    # reset of the y and x axis to start point

                    # todo its possible to move both axis at the same time?
                    Device1.MOV(axis1, measurement_configuration["y_start_value"])
                    Device2.MOV(axis2, measurement_configuration["x_start_value"])
                    pitools.waitontarget(Device1, axes=axis1)
                    pitools.waitontarget(Device2, axes=axis2)
                    time.sleep(5)       # timer to wait so the table doesnt shake anymore

                    currentyposition = Device1.qPOS(axis1)[axis1]
                    logging.info('Current position of y axis is {:.2f}'.format(currentyposition))
                    currentxposition = Device2.qPOS(axis2)[axis2]
                    logging.info('Aktuelle Position der Achse 2 ist {:.2f}'.format(currentxposition))

                    # cycle through the amount of meassurement points on the y axis
                    meassurementcounter = 0
                    for currentystep in range(0, Anzahl_Y):

                        # cycle through the amount of meassurement points on the x axis
                        for currentxstep in range(0, Anzahl_X):
                            
                            currentyposition = Device1.qPOS(axis1)[axis1]
                            currentxposition = Device2.qPOS(axis2)[axis2]
                            
                            # Measurement save to array
                            measurements[meassurementcounter] = self.make_measurement(measurement_configuration)
                            xpositionvalues[meassurementcounter] = currentxposition 
                            ypositionvalues[meassurementcounter] = currentyposition

                            meassurementcounter = meassurementcounter + 1

                            # as long as not last measurement
                            if currentxstep < (Anzahl_X - 1 ):
                                
                                # this instead of using currentposition avoids error propagation
                                theoreticalposition = (currentxstep + 1) * measurement_configuration["delta_x_value"] 
                                nextxposition = theoreticalposition + measurement_configuration["delta_x_value"]

                                # Move to next X Meassurepoint
                                Device2.MOV(axis2, nextxposition)
                                pitools.waitontarget(Device2, axes=axis2)
                                time.sleep(5)       # timer to wait so the table doesnt shake anymore

                            # update progress bar in gui
                            progress = progress + stepsize
                            self.pb['value'] = math.ceil(progress)
                            self.value_label['text'] = self.update_progress_label()

                        # as long as not last measurement
                        if currentystep < (Anzahl_Y - 1 ):
                            
                            # this instead of using currentposition avoids error propagation
                            theoreticalposition = (currentystep + 1) * measurement_configuration["delta_y_value"] 
                            nextyposition = theoreticalposition + measurement_configuration["delta_y_value"]

                            # Move to next Y Meassurepoint
                            Device1.MOV(axis1, nextyposition)
                            pitools.waitontarget(Device1, axes=axis1)

                        # Reset to "beginning of line" for next measurement
                        Device2.MOV(axis2, measurement_configuration["x_start_value"])
                        pitools.waitontarget(Device2, axes=axis2)

                    # Werte abspeichern
                    df = pd.DataFrame({"xpos" : xpositionvalues, "ypos" : ypositionvalues, "measure" : measurements})
                    df.to_csv(f"Measuremntrun {i}.csv", index=False)

                logging.info("Return to start position")
                Device1.MOV(axis1, measurement_configuration["y_start_value"])
                Device2.MOV(axis2, measurement_configuration["x_start_value"])
                pitools.waitontarget(Device1, axes=axis1)
                pitools.waitontarget(Device2, axes=axis2)
            
            logging.info("Verbindung schließen")
            Device2.CloseDaisyChain()
            Device1.CloseDaisyChain()

    def make_measurement(**measurement_configuration):
        """This function performs the local measurement. If more then one measurement is taken the mean of all saved values is returned.

        Args: 
            measurement_configuration (dict): Dictonary with measurment configuration

        Returns:
            float: power value of performed measurement
        """
        rm = pyvisa.ResourceManager()
        Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
        Spannungsmeasurements = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)
    
        for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
            Spannungsmeasurements[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )
    
        Leistungsmesswert = np.mean(measurement_configuration["conversion_factor"] * Spannungsmeasurements)
        return Leistungsmesswert