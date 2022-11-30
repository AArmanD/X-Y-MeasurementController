import numpy as np
from pipython import GCSDevice, pitools
import tkinter as tk
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
import pyvisa
import config_window

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']

class MeasureController(tk.Tk):
    def __init__(self):
        """This class initializes the configuration window for the measurement
        """

        super().__init__()

        self.title("X-Y Messprogramm")

        
        # create menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        

        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label="Import measuement configuration", underline=0, command=self.OpenConfigWindow)
        fileMenu.add_command(label="Show measurement graph", underline=0, command=self.destroy)
        fileMenu.add_command(label="Exit", underline=0, command=self.destroy)

        menubar.add_cascade(label="Options", underline=0, menu=fileMenu)
        

        # add icon
        photo = tk.PhotoImage(file = 'icon.png')
        self.wm_iconphoto(False, photo)
    
        # create field for storing input variables
        self.input_fields = []

        # configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
    
        self.ausgabe_label1 = tk.Label(
            self,
            text="Umrechnungsfaktor von Spannung in Leistung:",
            font=("Arial", 10),
        )
        self.ausgabe_label1.grid(column=0, row=0, sticky="w")
        

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[0].grid(column=1, row=0, sticky="e")
    
        ausgabe_label2 = tk.Label(
            self,
            text="Anzahl der Messdurchläufe:",
            font=("Arial", 10),
        )
        ausgabe_label2.grid(column=0, row=1, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[1].grid(column=1, row=1, sticky="e")
    
        ausgabe_label3 = tk.Label(
            self,
            text="Anzahl der Messungen an einer Position:",
            font=("Arial", 10),
        )
        ausgabe_label3.grid(column=0, row=2, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[2].grid(column=1, row=2, sticky="e")
    
        ausgabe_label4 = tk.Label(
            self,
            text="X-Startwert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label4.grid(column=0, row=3, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[3].grid(column=1, row=3, sticky="e")
    
        ausgabe_label5 = tk.Label(
            self,
            text="Y-Startwert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label5.grid(column=0, row=4, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[4].grid(column=1, row=4, sticky="e")
    
        ausgabe_label6 = tk.Label(
            self,
            text="X-Endwert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label6.grid(column=0, row=5, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[5].grid(column=1, row=5, sticky="e")
    
        ausgabe_label7 = tk.Label(
            self,
            text="Y-Endwert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label7.grid(column=0, row=6, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[6].grid(column=1, row=6, sticky="e")
    
        ausgabe_label8 = tk.Label(
            self,
            text="Delta X-Wert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label8.grid(column=0, row=7, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[7].grid(column=1, row=7, sticky="e")
    
        ausgabe_label9 = tk.Label(
            self,
            text="Delta Y-Wert in mm:",
            font=("Arial", 10),
        )
        ausgabe_label9.grid(column=0, row=8, sticky="w")

        self.input_fields.append(tk.Entry(self, font=("Arial", 10), width=10, justify="right"))
        self.input_fields[8].grid(column=1, row=8, sticky="e")

    
        tk.Button(
            self,
            text="Messung starten",
            font=("Arial", 10),
            command=self.StartMeasurement,
        ).grid(column=0, row=11, columnspan=2, pady=15)
    
        # tk.Button(
        #     self,
        #     text="Messung stoppen",
        #     font=("Arial", 10),
        #     bg="red",
        #     command=self.destroy
        # ).grid(column=1, row=9)

        # prevent gui resize
        self.resizable(False, False)

    def OpenConfigWindow(self):
        configwindow = config_window.ConfigWindow(self)
        configwindow.grab_set()

    def StartMeasurement(self):
        measurement_configuration = self.ReadConfiguration()
        self.MeasurementController(measurement_configuration)


    def ReadConfiguration(self):
        """This function reads in the entered configuration for the measurement
        """

        measurement_configuration = dict()

        try:
            measurement_configuration["conversion_factor"] = int(self.input_fields[0].get())
            measurement_configuration["number_of_measurement_runs"] = int(self.input_fields[1].get())
            measurement_configuration["number_of_measurements_in_one_position"] = int(self.input_fields[2].get())
            measurement_configuration["x_start_value"] = int(self.input_fields[3].get())
            measurement_configuration["y_start_value"] = int(self.input_fields[4].get())
            measurement_configuration["x_end_value"] = int(self.input_fields[5].get())
            measurement_configuration["y_end_value"] = int(self.input_fields[6].get())
            measurement_configuration["delta_x_value"] = float(self.input_fields[7].get())
            measurement_configuration["delta_y_value"] = float(self.input_fields[8].get())

        except ValueError:
            messagebox.showerror("Title", "Error in reading in configuration")
        
        # todo auf Wertebereiche prüfen

    def MeasurementController(self, **measurement_configuration):
    

        Anzahl_Y = (measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"]
        Anzahl_X = (measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"]

        X_Werte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)
        Y_Werte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)
        Messwerte = np.zeros((int(Anzahl_Y), int(Anzahl_X)), dtype=float)

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

                                    Messwerte[target1, target2] = Messgeraet(measurement_configuration)
                                    X_Werte[target1, target2] = position2
                                    Y_Werte[target1, target2] = position1
                                    Device2.MOV(axis, (position2 + measurement_configuration["delta_x_value"]))

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

                    print("Diagramm öffnen")
                    Diagramm(Y_Werte, X_Werte, Messwerte)

def Messgeraet(**measurement_configuration):
    rm = pyvisa.ResourceManager()
    Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
    Spannungsmesswerte = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)


    for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
        Spannungsmesswerte[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )

    Leistungsmesswert = np.mean(measurement_configuration["conversion_factor"] * Spannungsmesswerte)
    return Leistungsmesswert
        

def Diagramm(Y_Werte, X_Werte, Messwerte):
    #fig = plt.figure()
    axes = plt.axes(projection="3d")
    axes.scatter3D(Y_Werte, X_Werte, Messwerte, color="blue")
    axes.set_title("3D -Diagramm der Leistungsmesswerte")
    axes.set_xlabel("X-Korrdinaten des Verschiebetischs in mm")
    axes.set_ylabel("Y-Korrdinaten des Verschiebetischs in mm")
    axes.set_zlabel("Mittelwerte pro Position in P")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    measure_controller = MeasureController()
    measure_controller.mainloop()