import tkinter as tk
from tkinter import ttk
import pyvisa
from pipython import GCSDevice, pitools
import time
import numpy as np
from pipython import GCSDevice, pitools
import math

from threading import Thread

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']

class MeasurementController(tk.Toplevel):


    def __init__(self, parent, **measurement_configuration):

        super().__init__(parent)

        self.title("Messcontroller")

        self.geometry('300x120')

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

        # create and start measure thread
        #self.main_thread = Thread(target=self.measurement_controller, daemon=True, args=[measurement_configuration])
        self.main_thread = Thread(target=lambda: self.measurement_controller(**measurement_configuration))
        self.main_thread.start()

        self.mainloop()

    def update_progress_label(self):
        return f"Current Progress: {self.pb['value']}%"

    def test_progress_bar(self, measurement_configuration):
        print("in_test_progress_bar")

        for i in range(0,100):
            time.sleep(1)
            self.pb['value'] = i
            self.value_label['text'] = self.update_progress_label()


    def measurement_controller(self, **measurement_configuration):
    
        Anzahl_Y = (measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"]
        Anzahl_X = (measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"]

        X_Werte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)
        Y_Werte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)
        Messwerte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)

        stepsize = 100/(Anzahl_X*Anzahl_Y*measurement_configuration["number_of_measurement_runs"])
        progress = 0

        """Verbinden der Controller über DaisyChain"""
        with GCSDevice() as Device1:
            Device1.OpenUSBDaisyChain(description='0017550026')
            daisychainid = Device1.dcid
            Device1.ConnectDaisyChainDevice(1, daisychainid)
            with GCSDevice() as Device2:
                Device2.ConnectDaisyChainDevice(2, daisychainid)
                print('\n{}:\n{}'.format(Device1.GetInterfaceDescription(), Device1.qIDN()))
                print('\n{}:\n{}'.format(Device2.GetInterfaceDescription(), Device2.qIDN()))

                print('DaisyChain-Verbindung ist aufgebaut')

                print('Inialisierung Achsen...')
                pitools.startup(Device1, stages=STAGES, refmodes=REFMODES)
                pitools.startup(Device2, stages=STAGES, refmodes=REFMODES)

                rangemin_Device1 = Device1.qTMN()
                print('Min Achse 1:', rangemin_Device1)
                rangemax_Device1 = Device1.qTMX()
                print('Max Achse 1:', rangemax_Device1)
                curpos_Device1 = Device1.qPOS()
                print('Aktuelle Position Achse 2:', curpos_Device1)

                rangemin_Device2 = Device2.qTMN()
                print('Min Achse 2:', rangemin_Device2)
                rangemax_Device2 = Device2.qTMX()
                print('Max Achse 2:', rangemax_Device2)
                curpos_Device2 = Device2.qPOS()
                print('Aktuelle Position Achse 2:', curpos_Device2)

                for i in range(measurement_configuration["number_of_measurement_runs"]): 
                    for axis in Device1.axes:
                        Device1.MOV(axis, measurement_configuration["y_start_value"])
                        for target1 in range(0, int(Anzahl_Y)):

                            pitools.waitontarget(Device1, axes=axis)
                            position1 = Device1.qPOS(axis)[axis]
                            print('Aktuelle Position der Achse 1 ist {:.2f}'.format(position1))

                            for axis in Device2.axes:
                                Device2.MOV(axis, measurement_configuration["x_start_value"])
                                for target2 in range(0, int(Anzahl_X)):

                                    time.sleep(5)
                                    pitools.waitontarget(Device2, axes=axis)
                                    position2 = Device2.qPOS(axis)[axis]
                                    print('Aktuelle Position der Achse 2 ist {:.2f}'.format(position2))

                                    Messwerte[target1, target2] = self.make_measurement(measurement_configuration)
                                    X_Werte[target1, target2] = position2
                                    Y_Werte[target1, target2] = position1
                                    Device2.MOV(axis, (position2 + measurement_configuration["delta_x_value"]))

                                    # update progress bar
                                    progress = progress + stepsize
                                    self.pb['value'] = math.ceil(progress)
                                    self.value_label['text'] = self.update_progress_label()


                                time.sleep(2)


                            Device1.MOV(axis, (position1 + measurement_configuration["delta_y_value"]))

                    #Werte abspeichern
                    print('Y-Werte: ', Y_Werte)
                    np.savetxt('Y-Werte_Verschiebetisch.txt', Y_Werte , delimiter=';', fmt='%1.5f')
                    print('X-Werte: ', X_Werte)
                    np.savetxt('X-Werte_Verschiebetisch.txt', X_Werte, delimiter=';', fmt='%1.5f')
                    print('Messwerte:', Messwerte)
                    np.savetxt('Messwerte_Verschiebetisch.txt', Messwerte, delimiter=';', fmt='%1.8f')          

                    print("Verbindung schließen")
                    Device2.CloseDaisyChain()
                    Device1.CloseDaisyChain()
                    #Device1.CloseConnection()
                    #Device2.CloseConnection()

    def make_measurement(**measurement_configuration):
        rm = pyvisa.ResourceManager()
        Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
        Spannungsmesswerte = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)
    
    
        for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
            Spannungsmesswerte[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )
    
        Leistungsmesswert = np.mean(measurement_configuration["conversion_factor"] * Spannungsmesswerte)
        return Leistungsmesswert