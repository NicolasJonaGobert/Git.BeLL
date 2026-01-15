from scipy.integrate import quad

def stammint(a, b, h, hs):
    # Diese Funktion berechnet das Integral von h und hs auf [a,b]
    y1 = lambda x: float(h(x))    # float(...) stellt sicher, dass wirklich ein Skalar zurückkommt da quad nur damit arbeitet
    y2 = lambda x: float(hs(x))
    # quad gibt zwei Werte zurück
    # I  = Integralwert
    # err = geschätzter absoluter Fehler
    I1, err1 = quad(y1, a, b)
    I2, err2 = quad(y2, a, b)
    #Speicherung der Werte
    return I1, I2, err1, err2
