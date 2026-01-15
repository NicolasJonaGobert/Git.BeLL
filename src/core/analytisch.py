from scipy.integrate import quad#Methode zur Integration

def stammint(a, b, h, hs,mode=0):
    """
    Berechnet das Referenzintegral auf [a,b] mit quad, je nach mode für h oder hs, und gibt Integralwert und Fehlerabschätzung zurück.

    Parameter:
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        mode (int): 0 integriert h, 1 integriert hs

    Rückgabe:
        tuple: (I, err)
            I (float): Integralwert der gewählten Funktion auf [a,b]
            err (float): Von quad geschätzter absoluter Fehler
    """
    y1 = lambda x: float(h(x))   #Umwandeln in From mit der quad umgehen kann
    y2 = lambda x: float(hs(x))# float(...) stellt sicher, dass wirklich ein Skalar zurückkommt da quad nur damit arbeitet
    # quad gibt zwei Werte zurück
    # I  = Integralwert
    # err = geschätzter absoluter Fehler
    #Berechnung je nach Mode
    if mode == 0:
        I, err = quad(y1, a, b)
    elif mode == 1:
        I, err = quad(y2, a, b)
    #Speicherung der Werte
    return I, err
