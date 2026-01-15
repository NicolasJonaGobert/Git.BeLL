import numpy as np
from scipy.interpolate import CubicSpline

# Betragsfunktion aus zwei Funktionen
def betragsfunk(f, g):
    """
    Erstellt aus zwei Funktionen f und g eine neue Funktion h(x), die den Betrag der Differenz berechnet.

    Parameter:
        f (callable): Erste Funktion f(x)
        g (callable): Zweite Funktion g(x)

    Rückgabe:
        callable: Funktion h(x) = |f(x) - g(x)|
    """
    # gibt eine Funktion h(x) zurück, die |f(x) - g(x)| berechnet
    def h(x):
        return np.abs(f(x) - g(x))
    #Speicherung Funktion
    return h

def spline(pl, i):
    """
    Baut einen CubicSpline aus einer Punktliste pl[i].

    Parameter:
        pl (list): Liste von Punktlisten (x_liste, y_liste), z.B. [(x1,y1), (x2,y2), ...]
        i (int): Index der gewünschten Punktliste in pl

    Rückgabe:
        CubicSpline: Natural CubicSpline, der die Stützpunkte interpoliert
    """
    """
    Baut einen CubicSpline aus der Punktliste pl[index].
    pl: Liste von Punktlisten [(x1,y1), (x2,y2), ...]
    index: 0 für ersten Spline, 1 für zweiten
    """
    # Punkte aus der Liste holen
    x, y = pl[i]
    # In numpy arrays umwandeln
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    # Spline erzeugen und zurückgeben
    return CubicSpline(x, y,bc_type='natural')

# Betragsfunktion aus zwei Splines (gegeben durch Punktlisten)
def splinebetrag(pl):
    """
    Erstellt aus zwei Splines (aus den ersten beiden Punktlisten in pl) eine Funktion h(x), die den Betrag ihrer Differenz berechnet.

    Parameter:
        pl (list): Liste mit mindestens zwei Elementen, jeweils (x_liste, y_liste) für die Spline-Stützpunkte

    Rückgabe:
        callable: Funktion h(x) = |cs1(x) - cs2(x)|, wobei cs1 und cs2 natural CubicSplines sind
    """
    # Erstellung von Punktelisten
    (x1, y1) = pl[0]
    (x2, y2) = pl[1]
    #Umwandlung in arrays
    x1 = np.asarray(x1, dtype=float)
    y1 = np.asarray(y1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    y2 = np.asarray(y2, dtype=float)
    #Splineerstellung
    cs1 = CubicSpline(x1, y1,bc_type='natural')
    cs2 = CubicSpline(x2, y2,bc_type='natural')
    #Erstellung der Betragsfunktion
    def h(x):
        return np.abs(cs1(x) - cs2(x))
    # Speicherung
    return h

def randomsmonte(a,b,N,h,hs,kma,f_raw,mode=0):
    """
    Erzeugt Zufallspunkte für ein geometrisches Monte Carlo Verfahren und schätzt ein ymax im Intervall [a,b] durch Abtastung.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        N (int): Anzahl der Zufallspunkte
        h (callable): Funktion h(x), wird je nach mode einmal ausgewertet (z.B. für Funktionsaufruf-Zählung)
        hs (callable): Funktion hs(x), wird je nach mode einmal ausgewertet (z.B. für Funktionsaufruf-Zählung)
        kma (int): Anzahl der Abtastpunkte zur Approximation des Maximums
        f_raw (callable): Funktion, die für die Maximumsuche abgetastet wird (nicht gezählt)
        mode (int): 0 nutzt h für den Zählaufruf, 1 nutzt hs für den Zählaufruf

    Rückgabe:
        tuple: (xz, yz, ymax)
            xz (np.ndarray): Zufällige x-Werte in [a,b] (Länge N)
            yz (np.ndarray): Zufällige y-Werte in [0, ymax] (Länge N)
            ymax (float): Approximiertes Maximum der abgetasteten Funktion f_raw auf [a,b]
    """
    #Funktion die Zufallspunkte erstellt
    #Annäherung der globalen Maxima von h und hs
    xapr=np.linspace(a,b,kma)#x-Werte um Funktion abzutasten
    fr = f_raw#Funktion die nicht gezählt wird (Zähler durch fr +1 pro durchlauf)
    #Berechnung je nach Mode
    if mode==0:
        ymax=float(np.max(fr(xapr)))#Maximum h
        xm=(a+b)/2#x-Wert für Zählung
        _=h(xm)#Funktionsaufruf
    elif mode==1:
        ymax=float(np.max(fr(xapr)))#Maximum h
        xm=(a+b)/2
        _=hs(xm)
    #Punkteerstellung
    xz = np.random.uniform(a, b, N)  # Zufällige x-Werte
    yz = np.random.uniform(0,ymax, N) # Zufällige y-Werte für f
    #Speicherung
    return xz, yz,ymax
