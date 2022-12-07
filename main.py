import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

import config_window
import measurement_controller

class StartWindow(tk.Tk):
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

        measure_controller = measurement_controller.MeasurementController(self)

        measure_controller.measurement_controller()

        #self.MeasurementController(measurement_configuration)


    def ReadConfiguration(self):
        """This function reads in the entered configuration for the measurement
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
    start_window = StartWindow()
    start_window.mainloop()