import numpy as np
from scipy.interpolate import CubicSpline

# Betragsfunktion aus zwei Funktionen
def betragsfunk(f, g):
    # gibt eine Funktion h(x) zurück, die |f(x) - g(x)| berechnet
    def h(x):
        return np.abs(f(x) - g(x))
    return h

def spline(pl, i):
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
    return CubicSpline(x, y)

# Betragsfunktion aus zwei Splines (gegeben durch Punktlisten)
def splinebetrag(pl):
    # Erstellung von Punktelisten
    (x1, y1) = pl[0]
    (x2, y2) = pl[1]
    #Umwandlung in arrays
    x1 = np.asarray(x1, dtype=float)
    y1 = np.asarray(y1, dtype=float)
    x2 = np.asarray(x2, dtype=float)
    y2 = np.asarray(y2, dtype=float)
    #Splineerstellung
    cs1 = CubicSpline(x1, y1)
    cs2 = CubicSpline(x2, y2)
    #Erstellung der Betragsfunktion
    def h(x):
        return np.abs(cs1(x) - cs2(x))
    return h