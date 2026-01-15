import numpy as np#arrays

def trapezregel(nt,h,hs,a,b,mode=0):
    """
    Berechnet die Trapezregel-Näherung für das Integral auf [a,b], je nach mode für h oder hs.

    Parameter:
        nt (int): Anzahl der Teilintervalle der Zerlegung
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Trapezregel-Näherung des Integrals der gewählten Funktion auf [a,b]
    """
    #Berechnet Trapezsumme
    #Feinheit der Zerlegung
    dx=(b-a)/nt
    #Stützstellen
    xt=np.linspace(a,b,nt+1)
    #Berechnung der Trapezsumme
    if mode==0:
        yt=h(xt)#y-Werte h
    elif mode==1:
        yt=hs(xt)#y-Werte hs
    # --- FIX: konstant -> broadcast ---
    if np.isscalar(yt):
        yt = np.full_like(xt, float(yt), dtype=float)
    else:
        yt = np.asarray(yt, dtype=float)
        if yt.ndim == 0:
            yt = np.full_like(xt, float(yt), dtype=float)
        elif yt.size == 1 and xt.size > 1:
            yt = np.full_like(xt, float(yt.ravel()[0]), dtype=float)
    # -------------------------------
    ts=(yt[0]+yt[-1])*0.5+np.sum(yt[1:-1])#Berechnung der Trapezsumme für hs
    return ts*dx


def trapezerr(err, h, hs, a, b,Ai, k=1, mode=0):
    """
    Erhöht nt iterativ (Potenzen von 2), bis die Trapezregel-Näherung den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |Ai - Trapezregel|
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite, mit der der Exponent q erhöht wird (nt = 2**q)
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (nt, ts)
            nt (int): Gefundene Teilintervallzahl (als Potenz von 2)
            ts (float): Trapezregel-Näherung bei diesem nt
    """
    #Berechnet Trapezregel so lange bis err erreicht
    # Startwerte
    ts, nt,q = 0.0, 1,1
    # nt erhöhen, bis Fehler klein genug ist
    while True:
        ts = trapezregel(nt, h, hs, a, b, mode)#berechnung
        #Stoppen wenn err erreicht
        if abs(ts-Ai) < err:
            break
        else:
            nt=2**q
            q+=k
    #Rückgabe
    return nt, ts
