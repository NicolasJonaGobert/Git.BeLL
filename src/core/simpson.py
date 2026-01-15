import numpy as np#arrays

def simpsonregel(h,hs,ns,a,b,mode=0):
    """
    Berechnet die Simpsonregel-Näherung für das Integral auf [a,b].

    Abhängig vom Parameter mode wird entweder die Funktion h oder hs integriert.
    Die Anzahl der Teilintervalle ns muss gerade sein.

    Parameter:
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        ns (int): Anzahl der Teilintervalle (gerade Zahl)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Simpsonregel-Näherung des Integrals der gewählten Funktion
    """
    #Feinheit der Zerlegung
    dx = (b - a) / ns
    #Stützstellen
    xs = np.linspace(a, b, ns + 1)
    # Berechnung der Simpson-Summe (nur eine Funktion, je nach mode)
    if mode == 0:
        ys = h(xs)
    elif mode == 1:
        ys = hs(xs)
    # --- FIX: konstante Funktionen sauber auf Länge ns+1 aufblasen ---
    if np.isscalar(ys):
        ys = np.full_like(xs, float(ys), dtype=float)
    else:
        ys = np.asarray(ys, dtype=float)
        if ys.ndim == 0:
            ys = np.full_like(xs, float(ys), dtype=float)
        elif ys.size == 1 and xs.size > 1:
            ys = np.full_like(xs, float(ys.ravel()[0]), dtype=float)
    # ---------------------------------------------------------------
    #Berechnung Simpson
    ss = ys[0] + ys[-1]
    for i in range(1, ns):
        if i % 2 == 0:  # summe für alle geraden i
            ss += 2 * ys[i]
        elif i % 2 == 1:  # summe für alle ungeraden i
            ss += 4 * ys[i]
    #Rückgabe
    return ss * (dx / 3)


def simpsonerr(h,hs,err,a,b,Ai,k=1,mode=0):
    """
    Erhöht die Teilintervallzahl ns (in Zweierpotenzen), bis die Simpsonregel-
    Näherung den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        err (float): Fehlertoleranz für |Ai - Simpsonregel|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite für den Exponenten (ns = 2**q)
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (ns, ss)
            ns (int): Gefundene Teilintervallzahl (gerade, Potenz von 2)
            ss (float): Simpsonregel-Näherung bei diesem ns
    """
    # Start: ns = 0 (noch keine Teilintervalle), erste Rechnung bei ns = 2
    ss, ns,q = 0.0, 2,2  # Simpson-Näherung,ns und Laufvariable q
    # ns erhöhen, bis Simpsonregel nah genug am Referenzwert Ai ist
    while True:
        ss = simpsonregel(h, hs, ns, a, b, mode)
        #Stoppen wenn err erreicht
        if abs(Ai-ss) < err: break
        else:
            ns=2**q
            q+=k
    #Rückgabe
    return ns, ss
