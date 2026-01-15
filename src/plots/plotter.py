import matplotlib.pyplot as plt
import numpy as np

def plot_funktionen_fläche(a,b,f1,f2):
    """
    Plottet zwei Funktionen f1 und f2 auf [a,b] und markiert die Fläche zwischen ihnen.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f1 (callable): Erste Funktion f1(x)
        f2 (callable): Zweite Funktion f2(x)

    Rückgabe:
        keine
    """
    #x-Werte für Plot
    xp=np.linspace(a,b,10000)
    # Funktionswerte einmal berechnen
    y1 = f1(xp)
    y2 = f2(xp)
    #Plotten der Funktion
    plt.plot(xp,y1,color="blue",label="$f_1(x)$") #Plot f1
    plt.plot(xp,y2,color="red",label="$f_2(x)$") #Plot f2
    plt.fill_between(xp,y1,y2,alpha=0.25,color="green",label="Fläche zwischen $f_1(x)$ und $f_2(x)$")#Fläche zwischen f1 und f2 grün makieren
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    #Ausgabe
    plt.show()

def plot_betrag(a,b,f):
    """
    Plottet eine Funktion f auf [a,b] und markiert die Fläche unter der Kurve.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Funktion f(x), die geplottet werden soll

    Rückgabe:
        keine
    """
    # x-Werte für Plot
    xp = np.linspace(a,b,10000)
    # Funktionswerte einmal berechnen
    y1 = f(xp)
    # Plotten der Funktion
    plt.plot(xp,y1,color="red",label="$B(x)$")#Plot Betragsfunktion
    plt.fill_between(xp,y1,alpha=0.25,color="green",label="Fläche unter $B(x)$")#Fläche unter B(x)
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    #Ausgabe
    plt.show()

def plot_riemannsumme(a, b, nr, f, mode="u"):
    """
    Plottet die Funktion f auf [a,b] und visualisiert Riemann-Rechtecke (Unter- oder Obersumme).

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nr (int): Anzahl der Teilintervalle der Zerlegung
        f (callable): Funktion f(x), die geplottet und angenähert wird
        mode (str): "u" für Untersumme, "o" für Obersumme

    Rückgabe:
        keine
    """
    """
    Plottet die Betragsfunktion B(x) und Riemann-Rechtecke.
    mode:
      "unter" -> Untersumme (min an Intervallenden)
      "ober"  -> Obersumme  (max an Intervallenden)
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    plt.plot(xp, yp, color="red", label="$B(x)$")
    # Stützstellen der Zerlegung
    dx = (b - a) / nr #Feinheit
    xre = np.linspace(a, b, nr + 1)
    # Funktionswerte an Stützstellen nur einmal berechnen
    yre = f(xre)
    # Rechteckhöhen pro Intervall aus Endpunkten bestimmen
    y_left  = yre[:-1]
    y_right = yre[1:]
    if mode == "u":
        heights = np.minimum(y_left, y_right)
        label_rect = "Untersumme"
        color_rect = "blue"
    elif mode == "o":
        heights = np.maximum(y_left, y_right)
        label_rect = "Obersumme"
        color_rect = "green"
    else:
        raise ValueError("mode muss 'unter' oder 'ober' sein")#Fehler wenn mode flasch eingegeben
    # Rechtecke zeichnen (linke Kante bei xre[:-1])
    plt.bar(
        xre[:-1],
        heights,
        width=dx,
        align="edge",
        alpha=0.3,
        color=color_rect,
        edgecolor="black",
        label=label_rect,
        zorder=3
    )
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    #Ausgabe
    plt.show()

def plot_trapezregel(a,b,nt,f):
    """
    Plottet die Funktion f auf [a,b] und visualisiert die Trapeze der Trapezregel mit nt Teilintervallen.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nt (int): Anzahl der Teilintervalle der Zerlegung
        f (callable): Funktion f(x), die geplottet und durch Trapeze angenähert wird

    Rückgabe:
        keine
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    plt.plot(xp, yp, color="red", label="$B(x)$")
    #Plot der Trapeze
    xt=np.linspace(a,b,nt+1)#Stützstellen
    yt = f(xt)
    #Plotten von nt Trapezen
    for i in range(nt):
        #Label soll nur einmal erscheinen
        if i==0:
            plt.fill_between(xt[i:i+2],0,yt[i:i+2],alpha=0.25,color="green",label="Trapeze unter $B(x)$")
        else:
            plt.fill_between(xt[i:i+2],0,yt[i:i+2],alpha=0.25,color="green")
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    #Ausgabe
    plt.show()

def plot_simpson(a,b,ns,f):
    """
    Plottet die Funktion f auf [a,b] und visualisiert die Simpson-Interpolation (Parabeln) für ns Teilintervalle.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        ns (int): Anzahl der Teilintervalle der Zerlegung (muss gerade sein)
        f (callable): Funktion f(x), die geplottet und durch Parabeln angenähert wird

    Rückgabe:
        keine
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    plt.plot(xp, yp, color="red", label="$B(x)$")
    #Plot Interpolationspolynome
    #Feinheit der Zerlegung
    h=(b-a)/(ns)
    #Stützstellen
    xp=np.linspace(a,b,ns+1)
    # Parabeln
    def p(x, index, h, xp):
        return (1 / (h ** 2)) * (0.5 * f(xp[index]) * (x - xp[index + 1]) * (x - xp[index + 2]) - f(xp[index + 1]) * (x - xp[index]) * (x - xp[index + 2]) + f(xp[index + 2]) * 0.5 * (x - xp[index]) * (x - xp[index + 1]))  #Allgemeine Interpolationsparabel

    #Plot Parabeln in zweier Intervall-Schritten
    for i in range(0,ns,2):
        xp1 = np.linspace(xp[i],xp[i+2],2000) #x-Werte für Plot in [x_i;x_i+2]
        yint=p(xp1,i,h,xp) #y-Werte Parabel des jeweiligen Intervalls
        if i==0:
            plt.plot(xp1, yint, color="blue", label="Interpolationsparabeln") #Plot Parabel
            plt.fill_between(xp1, 0,yint, color="green", alpha=0.25,
                             edgecolor="black", linewidth=2, zorder=3,label="Fläche unter Parabeln")  # Plot der Fläche unter den Parabeln
        else:
            plt.plot(xp1, yint, color="blue")  # Plot Parabel
            plt.fill_between(xp1,0, yint, color="green", alpha=0.25,
                             edgecolor="black", linewidth=2, zorder=3)  # Plot der Fläche unter den Parabeln
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    #Ausgabe
    plt.show()

from functions import randomsmonte

def plot_monte(a, b, N, h, hs, w="h"):
    """
    Visualisiert die Monte Carlo Zufallspunkte und die zugehörige Funktion (h oder hs) auf dem Intervall [a,b].

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        N (int): Anzahl der Zufallspunkte
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        w (str): Auswahl der Funktion, "h" oder "hs"

    Rückgabe:
        keine
    """
    """
    which = "h"  -> Monte Carlo für h
    which = "hs" -> Monte Carlo für hs
    """
    # Feiner Plot der Kurve
    xp = np.linspace(a, b, 10000)
    # Zufallspunkte erzeugen
    xz, yz1, yz2, y1max, y2max = randomsmonte(a, b, N, h, hs)
    #Welche Funktion soll geplottet werden ?
    if w == "h":
        plt.plot(xp, h(xp), color="red", label="$B(x)$")
        plt.plot(xz, yz1, 'o', color="blue", markersize=3,
                 label=f"Zufallspunkte (N={N})")

    elif w == "hs":
        plt.plot(xp, hs(xp), color="red", label="$B(x)$")
        plt.plot(xz, yz2, 'o', color="blue", markersize=3,
                 label=f"Zufallspunkte (N={N})")
    else:
        raise ValueError("which muss 'h' oder 'hs' sein")
    #Bearbeiten Koordinatensystem
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    #Ausgabe
    plt.show()
