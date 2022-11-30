import tkinter as tk
from functools import partial
import pyvisa
import matplotlib.pyplot as plt
from pipython import GCSDevice, pitools
import numpy as np
import time

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']


# todo: werte speichern button speichern nichts, eliminieren
# todo: Einheitliche einlesefunktion
# aufgefallen!! auslesen der Textfelder erst bei bearbeitung
# aufgefallen!! verwendung von Partial eigentlich nicht notwendig
# print ausgaben entfernen
# logger einbauen
# config import/export
# requirements.txt

def gesamtDurchlauf(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe - Nur ganze Zahlen verwenden!"
    else:
        antwort = "Gesamtdurchlaufsanzahl gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def X_Startwert(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe - Punkt statt Komma verwenden!"
    else:
        antwort = "X-Startwert gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def X_Endwert(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe -  Nur ganze Zahlen möglich!"
    else:
        antwort = "X-Endwert gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def DeltaX_Wert(eingabefeld, ausgabe_label):
    try:
        eingabe = float(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe -  Nur ganze Zahlen möglich!"
    else:
        antwort = "Delta X-Wert gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def Y_Startwert(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe -  Nur ganze Zahlen möglich!"
    else:
        antwort = "Y-Startwert gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def Y_Endwert(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe - Nur ganze Zahlen möglich!"
    else:
        antwort = "Y-Endwert gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def DeltaY_Wert(eingabefeld, ausgabe_label):
    try:
        eingabe = float(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe - Punkt statt Komma verwenden!"
    else:
        antwort = "Delta Y-Wert gespeichert "
    ausgabe_label["text"] = antwort
    print("Eingabe1:", eingabe)
    return eingabe


def MessungProPosition(eingabefeld, ausgabe_label):
    try:
        eingabe = int(eingabefeld.get())
    except ValueError:
        antwort = "Falsche Eingabe - Nur ganze Zahlen verwenden!"
    else:
        antwort = "Anzahl der Messungen pro Position gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe2:", eingabe)
    return eingabe


def Umrechnungsfaktor(eingabefeld, ausgabe_label):
    try:
        eingabe = float(eingabefeld.get())

    except ValueError:
        antwort = "Falsche Eingabe - Punkt statt Komma verwenden!"
    else:
        antwort = "Umrechnungsfaktor gespeichert"
    ausgabe_label["text"] = antwort
    print("Eingabe3:", eingabe)
    return eingabe


def Benutzeroberfläche():
    title = "Werte für den Verschiebetisch eintragen "
    root = tk.Tk()
    root.title(title)
    root["background"] = "white"

    tk.Label(
        root,
        text=title,
        bg="black",
        fg="white",
        font=("Arial", 12),
    ).pack(fill="both")

    ausgabe_label2 = tk.Label(
        root,
        text="Umrechnungsfaktor von Spannung in Leistung",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label2.pack()
    text = "Umrechnungsfaktor von Spannung in Leistung"
    eingabefeld2 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld2.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(Umrechnungsfaktor, eingabefeld2, ausgabe_label2),
    ).pack(fill="both")

    ausgabe_label1 = tk.Label(
        root,
        text="Anzahl der Messdurchläufe",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label1.pack()
    text = "Anzahl der Messdurchläufe "
    eingabefeld1 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld1.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(gesamtDurchlauf, eingabefeld1, ausgabe_label1),
    ).pack(fill="both")

    ausgabe_label3 = tk.Label(
        root,
        text="Anzahl der Messungen an einer Position",
        bg="white",
        fg="black",
        font=("Arial", 10),

    )
    ausgabe_label3.pack()
    text = "Anzahl der Messungen an einer Position"
    eingabefeld3 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld3.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(MessungProPosition, eingabefeld3, ausgabe_label3),
    ).pack(fill="both")

    ausgabe_label4 = tk.Label(
        root,
        text="X-Startwert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label4.pack()
    text = "X-Startwert in mm angeben"
    eingabefeld4 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld4.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(X_Startwert, eingabefeld4, ausgabe_label4),
    ).pack(fill="both")

    ausgabe_label5 = tk.Label(
        root,
        text="Y-Startwert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label5.pack()
    text = "Y-Startwert"
    eingabefeld5 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld5.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(Y_Startwert, eingabefeld5, ausgabe_label5),
    ).pack(fill="both")

    ausgabe_label6 = tk.Label(
        root,
        text="X-Endwert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label6.pack()
    text = "X-Endwert in mm angeben"
    eingabefeld6 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld6.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(X_Endwert, eingabefeld6, ausgabe_label6),
    ).pack(fill="both")

    ausgabe_label7 = tk.Label(
        root,
        text="Y-Endwert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label7.pack()
    text = "Y-Endwert"
    eingabefeld7 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld7.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(Y_Endwert, eingabefeld7, ausgabe_label7),
    ).pack(fill="both")

    ausgabe_label8 = tk.Label(
        root,
        text="Delta X-Wert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label8.pack()
    text = "Delta X-Wert in mm angeben"
    eingabefeld8 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld8.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(DeltaX_Wert, eingabefeld8, ausgabe_label8),
    ).pack(fill="both")

    ausgabe_label9 = tk.Label(
        root,
        text="Delta Y-Wert in mm angeben",
        bg="white",
        fg="black",
        font=("Arial", 10),
    )
    ausgabe_label9.pack()
    text = "Delta Y-Wert in mm angeben"
    eingabefeld9 = tk.Entry(root, font=("Arial", 10), width=len(text), text=text)
    eingabefeld9.pack(fill="both")

    tk.Button(
        root,
        text="Wert speichern",
        font=("Arial", 10),
        bg="orange",
        command=partial(DeltaY_Wert, eingabefeld9, ausgabe_label9),
    ).pack(fill="both")

    tk.Button(
        root,
        text="Messung starten",
        font=("Arial", 10),
        bg="red",
        command=partial(Verschiebetisch, eingabefeld1, ausgabe_label1, eingabefeld2, ausgabe_label2, eingabefeld3, ausgabe_label3, eingabefeld4,
                        ausgabe_label4, eingabefeld5, ausgabe_label5, eingabefeld6, ausgabe_label6, eingabefeld7,
                        ausgabe_label7, eingabefeld8, ausgabe_label8, eingabefeld9, ausgabe_label9),
    ).pack(side="right", padx=10, pady=10)

    tk.Button(
        root,
        text="Messung stoppen",
        font=("Arial", 10),
        bg="red",
        command=root.destroy
    ).pack(side="left", padx=10, pady=10)
    root.mainloop()


def Messgeraet(eingabefeld2, ausgabe_label2, eingabefeld3, ausgabe_label3):
    umrechnungsfaktor = Umrechnungsfaktor(eingabefeld2, ausgabe_label2)
    AnzahlproPosition = MessungProPosition(eingabefeld3, ausgabe_label3)
    rm = pyvisa.ResourceManager()
    Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
    Spannungsmesswerte = np.zeros( AnzahlproPosition, dtype=float)


    for i in range(AnzahlproPosition):
        Spannungsmesswerte[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )

    Leistungsmesswert = np.mean(umrechnungsfaktor * Spannungsmesswerte)
    return Leistungsmesswert


def Verschiebetisch(eingabefeld1, ausgabe_label1, eingabefeld2, ausgabe_label2, eingabefeld3, ausgabe_label3, eingabefeld4, ausgabe_label4,
                    eingabefeld5, ausgabe_label5, eingabefeld6, ausgabe_label6, eingabefeld7, ausgabe_label7,
                    eingabefeld8, ausgabe_label8, eingabefeld9, ausgabe_label9):
    '''Parameter angeben'''
    Anzahl_Messdurchlaeufe = gesamtDurchlauf(eingabefeld1, ausgabe_label1)
    Start_X = X_Startwert(eingabefeld4, ausgabe_label4)
    Start_Y = Y_Startwert(eingabefeld5, ausgabe_label5)
    Ende_X = X_Endwert(eingabefeld6, ausgabe_label6)
    Ende_Y = Y_Endwert(eingabefeld7, ausgabe_label7)
    Schrittweite_Y = DeltaY_Wert(eingabefeld8, ausgabe_label8)
    Schrittweite_X = DeltaX_Wert(eingabefeld9, ausgabe_label9)
  

    Anzahl_Y = (Ende_Y - Start_Y) / Schrittweite_Y
    Anzahl_X = (Ende_X - Start_X) / Schrittweite_X

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
            
            for i in range(Anzahl_Messdurchlaeufe): 
                for axis in Device1.axes:
                    Device1.MOV(axis, Start_Y)
                    for target1 in range(0, int(Anzahl_Y)):
                        
                        pitools.waitontarget(Device1, axes=axis)
                        position1 = Device1.qPOS(axis)[axis]
                        print('Aktuelle Position der Achse 1 ist {:.2f}'.format(position1))
                       
                        for axis in Device2.axes:
                            Device2.MOV(axis, Start_X)
                            for target2 in range(0, int(Anzahl_X)):
                                
                                time.sleep(5)
                                pitools.waitontarget(Device2, axes=axis)
                                position2 = Device2.qPOS(axis)[axis]
                                print('Aktuelle Position der Achse 2 ist {:.2f}'.format(position2))
                                                            
                                Messwerte[target1, target2] = Messgeraet(eingabefeld2, ausgabe_label2, eingabefeld3,
                                                                         ausgabe_label3, )
                                X_Werte[target1, target2] = position2
                                Y_Werte[target1, target2] = position1
                                Device2.MOV(axis, (position2 + Schrittweite_X))
                            
                            time.sleep(2)
                            
                          
                        Device1.MOV(axis, (position1 + Schrittweite_Y))
                         
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


def main():
    Benutzeroberfläche()


if __name__ == '__main__':
    main()