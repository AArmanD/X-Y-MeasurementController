import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('450x350')
        self.title('Konfigurations Menü')

        self.configloadbutton = tk.Button(
            self,
            text="Konfiguration Laden",
            font=("Arial", 10),
            command=self.openfile,
        ).pack()

        self.entryfield = tk.Entry(
            self,
        )

        # insert some sample content for testing purposes
        parent.input_fields[0].delete(0,tk.END)
        parent.input_fields[0].insert(0, "125")

    def openfile(self):
        filepath = filedialog.askopenfilename(
            title='Datei öffnen',
            initialdir='C:/Users/Lukas/Documents/Git/X-Y-MeasurementController',
            filetypes=(('Konfigurations Datei','*.csv'),('Alle Formate','*.*'))

        )

        with open(filepath) as csv_file:
            csvFile = csv.DictReader(csv_file)
    
            for row in csvFile:
                print(row)


if __name__ == "__main__":

    class App(tk.Tk):
        def __init__(self):
            super().__init__()

            self.geometry('300x200')
            self.title('Debug Window')

            # place a button on the root window
            ttk.Button(self,
                    text='Öffne Config Window',
                    command=self.open_window).pack(expand=True)


        def open_window(self):
            window = ConfigWindow(self)
            window.grab_set()
                    
    app = App()
    app.mainloop()
