import numpy as np

def simpsonregel(h,hs,ns,a,b,mode=0):
    """
    Berechnet die Simpsonregel-Näherung für h oder hs auf dem Intervall [a,b] mit ns Teilintervallen.

    Parameter:
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        ns (int): Anzahl der Teilintervalle der Zerlegung (muss gerade sein)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Simpsonregel-Näherungswert der gewählten Funktion auf [a,b]
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
    #Berechnung Simpson
    ss = ys[0] + ys[-1]
    for i in range(1, ns):
        if i % 2 == 0:  # summe für alle geraden i
            ss += 2 * ys[i]
        elif i % 2 == 1:  # summe für alle ungeraden i
            ss += 4 * ys[i]
    #Rückgabe
    return ss * (dx / 3)


from core.analytisch import stammint

def simpsonerr(h,hs,err,a,b,k=2,mode=0):
    """
    Ermittelt eine gerade Teilintervallzahl ns (in Schritten von k), sodass die Simpsonregel den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        err (float): Fehlertoleranz für |I_ref - S|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der ns erhöht wird (standardmäßig 2, damit ns gerade bleibt)
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (ns, ss)
            ns (int): Teilintervallzahl (gerade), bei der der Fehler <= err ist
            ss (float): Simpsonregel-Wert der Zielfunktion bei ns
    """
    # Referenzintegrale
    Ai,_ = stammint(a, b, h, hs,mode)
    # Start: ns = 0 (noch keine Teilintervalle), erste Rechnung bei ns = 2
    ss, ns = 0.0, 0  # Simpson-Näherung und ns
    # ns erhöhen, bis Simpsonregel nah genug am Referenzwert Ai ist
    while True:
        ns += k  # n muss immer gerade sein
        ss = simpsonregel(h, hs, ns, a, b, mode)
        #Stoppen wenn err erreicht
        if abs(Ai-ss) < err: break
    #Rückgabe
    return ns, ss
