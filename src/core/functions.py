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
    return h

def spline(pl, i):
    """
    Baut einen CubicSpline aus der Punktliste pl[i].

    Parameter:
        pl (list): Liste von Punktlisten (x_liste, y_liste), z.B. [(x1,y1), (x2,y2), ...]
        i (int): Index des gewünschten Splines in pl (0 für ersten, 1 für zweiten, ...)

    Rückgabe:
        CubicSpline: Kubischer Spline (natural), der die Stützpunkte interpoliert
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
    return h

def randomsmonte(a,b,N,h,hs):
    """
    Erzeugt Zufallspunkte für ein Monte Carlo Verfahren und schätzt die globalen Maxima der Funktionen h und hs im Intervall [a,b].

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        N (int): Anzahl der Zufallspunkte
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)

    Rückgabe:
        tuple: (xz, yz1, yz2, y1max, y2max)
            xz (np.ndarray): Zufällige x-Werte in [a,b] (Länge N)
            yz1 (np.ndarray): Zufällige y-Werte in [0, y1max] für h (Länge N)
            yz2 (np.ndarray): Zufällige y-Werte in [0, y2max] für hs (Länge N)
            y1max (float): Approximiertes Maximum von h auf [a,b] (per Abtastung)
            y2max (float): Approximiertes Maximum von hs auf [a,b] (per Abtastung)
    """
    #Annäherung der globalen Maxima von h und hs
    xapr=np.linspace(a,b,5000)#x-Werte um Funktion abzutasten
    y1max=float(np.max(h(xapr)))#Maximum h
    y2max=float(np.max(hs(xapr)))#Maximum h
    #Punkteerstellung
    xz = np.random.uniform(a, b, N)  # Zufällige x-Werte für beide h und hs
    yz1 = np.random.uniform(0,y1max, N) # Zufällige y-Werte für h
    yz2 = np.random.uniform(0,y2max, N) # Zufällige y-Werte für hs
    return xz, yz1, yz2,y1max,y2max
