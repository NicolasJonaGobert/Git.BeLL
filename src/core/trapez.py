import numpy as np

def trapezregel(nt,h,hs,a,b,mode=0):
    """
    Berechnet die Trapezregel-Näherung für h oder hs auf dem Intervall [a,b] mit nt Teilintervallen.

    Parameter:
        nt (int): Anzahl der Teilintervalle der Zerlegung
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Trapezregel-Näherungswert der gewählten Funktion auf [a,b]
    """
    #Feinheit der Zerlegung
    dx=(b-a)/nt
    #Stützstellen
    xt=np.linspace(a,b,nt+1)
    #Berechnung der Trapezsumme
    if mode==0:
        yt=h(xt)#y-Werte h
    elif mode==1:
        yt=hs(xt)#y-Werte hs
    ts=(yt[0]+yt[-1])*0.5+np.sum(yt[1:-1])#Berechnung der Trapezsumme für hs
    return ts*dx

from core.analytisch import stammint

def trapezerr(err, h, hs, a, b, k=1, mode=0):
    """
    Ermittelt eine Teilintervallzahl nt (in Schritten von k), sodass die Trapezregel den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - T|
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der nt erhöht wird
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (nt, ts)
            nt (int): Teilintervallzahl, bei der der Fehler <= err ist
            ts (float): Trapezregel-Wert der Zielfunktion bei nt
    """
    # Referenzintegral
    Ai,_ = stammint(a, b, h, hs,mode)
    # Startwerte
    ts, nt = 0.0, 0
    # nt erhöhen, bis Fehler klein genug ist
    while True:
        nt += k
        ts = trapezregel(nt, h, hs, a, b, mode)
        if abs(ts-Ai) < err:
            break
    #Rückgabe
    return nt, ts
