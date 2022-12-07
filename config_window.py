import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('450x350')
        self.title('Konfigurations Menü')

        self.configloadbutton = tk.Button(
            self,
            text="Konfiguration Laden",
            font=("Arial", 10),
            command=lambda: self.openfile(parent),
        ).pack()

        self.entryfield = tk.Entry(
            self,
        )


    def openfile(self,parent):
        filepath = filedialog.askopenfilename(
            title='Datei öffnen',
            initialdir='C:/Users/Lukas/Documents/Git/X-Y-MeasurementController',
            filetypes=(('Konfigurations Datei','*.csv'),('Alle Formate','*.*'))
        )

        df = pandas.read_csv(filepath, header=None, index_col=0).squeeze("columns")
        config = df.to_dict()
        configkeys = config.keys()
       
        for key in configkeys:
            # Load the config into input fields
            parent.input_fields[key].delete(0,tk.END)
            parent.input_fields[key].insert(0, config[key])

            


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
