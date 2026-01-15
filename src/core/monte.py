import numpy as np
from core.functions import randomsmonte

def geomonte(N, a, b, h, hs,kma, mode=0):
    """
    Führt ein geometrisches Monte Carlo Verfahren für h oder hs auf [a,b] aus und gibt Näherung, Trefferzahl und Zufallspunkte zurück.

    Parameter:
        N (int): Anzahl der Zufallspunkte
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Parameter zur Maximum-Approximation innerhalb randomsmonte
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (mc, Zi, xz, yz)
            mc (float): Monte Carlo Näherungswert des Integrals der gewählten Funktion
            Zi (int): Anzahl der Trefferpunkte unter der Kurve
            xz (np.ndarray): Zufällige x-Werte in [a,b] (Länge N)
            yz (np.ndarray): Zufällige y-Werte in [0, ymax] (Länge N)
    """
    # Zufallsgenerierung der Punkte über externe Funktion (unverändert)
    xz, yz,ymax=randomsmonte(a,b,N,h,hs,kma,mode)
    # Berechnung Rechteckfläche und Zählung der Treffer für h
    if mode == 0:
        A = (b - a) * ymax #Rechteck
        yh = h(xz) #y-Werte
        Zi = 0 #Anzahl Treffer
        #Überprüfen für jedes N
        for i in range(N):
            if yh[i] >= yz[i]:
                Zi += 1
        return A * (Zi / N),Zi,xz,yz
    # Berechnung Rechteckfläche und Zählung der Treffer für hs (Prinzip wie bei h)
    elif mode == 1:
        A = (b - a) * ymax
        yhs = hs(xz)
        Zi = 0
        for i in range(N):
            if yhs[i] >= yz[i]:
                Zi += 1
        return A * (Zi / N),Zi,xz,yz


from core.analytisch import stammint

def errmonte(err, a, b, h, hs,kma, k=10, mode=0):
    """
    Ermittelt eine Stichprobengröße N (in Schritten von k), sodass die Monte Carlo Näherung den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - MC|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Parameter zur Maximum-Approximation innerhalb randomsmonte
        k (int): Schrittweite, mit der N erhöht wird
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (N, mc)
            N (int): Stichprobengröße, bei der der Fehler <= err ist
            mc (float): Monte Carlo Näherungswert der Zielfunktion bei N
    """
    # Referenzintegral
    Ai,_ = stammint(a, b, h, hs,mode)
    # Startwerte
    mc, N = 0.0, 0
    # Monte-Carlo konvergiert nicht monoton (Zufallsverfahren)
    while True:
        N += k
        mc,_,_,_ = geomonte(N, a, b, h, hs,kma, mode)
        if abs(mc - Ai) < err:
            break
    # Rückgabe
    return N, mc
