import numpy as np#arrays

class CountedFunction:
    """
    Verpackt eine Funktion so, dass die Anzahl ihrer Auswertungen gezählt wird.

    Jede Auswertung von func(x) wird als Funktionsaufruf gezählt, unabhängig davon,
    ob x ein Skalar oder ein NumPy-Array ist.
    """

    def __init__(self, func, name="f"):
        """
        Initialisiert eine gezählte Funktion.

        Parameter:
            func (callable): Die eigentliche Funktion, z.B. h oder hs
            name (str): Optionaler Name der Funktion (nur zur Übersicht)

        Rückgabe:
            keine
        """
        self.func = func
        self.name = name
        self.calls = 0   # Startwert: noch keine Auswertung erfolgt

    def __call__(self, x):
        """
        Wertet die Funktion an der Stelle x aus und erhöht den Aufrufzähler.

        Parameter:
            x (float | int | np.ndarray): Auswertestelle(n) der Funktion

        Rückgabe:
            float | np.ndarray: Funktionswert(e) von func(x)
        """

        # Fall 1: x ist ein NumPy-Array (z.B. aus np.linspace)
        # Dann entspricht jede Komponente von x einer Funktionsauswertung
        if isinstance(x, np.ndarray):
            self.calls += x.size   # Anzahl der Punkte im Array addieren

        # Fall 2: x ist ein einzelner Wert (float oder int)
        # Dann wurde die Funktion genau einmal ausgewertet
        else:
            self.calls += 1

        # Rückgabe des eigentlichen Funktionswertes
        return self.func(x)

    def reset(self):
        """
        Setzt den Funktionsaufruf-Zähler auf 0 zurück.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        self.calls = 0
