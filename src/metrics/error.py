import numpy as np#arrays

def error(wert1,wert2,I1,I2,a,b):
    """
    Berechnet absolute und prozentuale Abweichungen zweier Näherungswerte vom jeweiligen Referenzintegral.

    Parameter:
        wert1 (float): Näherungswert für das erste Integral
        wert2 (float): Näherungswert für das zweite Integral
        I1 (float): Referenzintegralwert für das erste Integral
        I2 (float): Referenzintegralwert für das zweite Integral
        a (float): Linke Intervallgrenze (wird nicht direkt verwendet)
        b (float): Rechte Intervallgrenze (wird nicht direkt verwendet)

    Rückgabe:
        tuple: (abs1, abs2, pf1, pf2)
            abs1 (float): Absoluter Fehler von wert1
            abs2 (float): Absoluter Fehler von wert2
            pf1 (float): Prozentualer Fehler von wert1
            pf2 (float): Prozentualer Fehler von wert2
    """
    #Berechnung Integralwert
    A1=I1
    A2=I2
    #Berechnung Betrag der Fehler
    #Absolute Fehler
    abs1=abs(A1-wert1)
    abs2=abs(A2-wert2)
    #Fehler in %
    if A1>0 and A2>0:
        pf1=(abs1*100)/abs(A1)
        pf2=(abs2*100)/abs(A2)
        return abs1, abs2, pf1, pf2
    elif A1==0 and A2>0:
        pf2 = (abs2 * 100) / abs(A2)
        return abs1, abs2, 0, pf2
    elif A1>0 and A2==0:
        pf1 = (abs1 * 100) / abs(A1)
        return abs1, abs2, pf1, 0
    elif A1==0 and A2==0:
        return abs1, abs2, 0, 0
