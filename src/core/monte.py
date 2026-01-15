import numpy as np
from core.functions import randomsmonte

def geomonte(N,a,b,h,hs):
    """
    Berechnet eine geometrische Monte Carlo Näherung der Integrale von h und hs auf dem Intervall [a,b].

    Parameter:
        N (int): Anzahl der Zufallspunkte
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)

    Rückgabe:
        tuple: (MC_h, MC_hs)
            MC_h (float): Monte Carlo Näherung für das Integral von h auf [a,b]
            MC_hs (float): Monte Carlo Näherung für das Integral von hs auf [a,b]
    """
    #Zufallsgenerierung der Punkte über externe Funktions
    xz ,yz1 ,yz2,y1max,y2max=randomsmonte(a,b,N,h,hs)
    #Berechnung Rechteckfläche
    A1,A2=(b-a)*y1max,(b-a)*y2max
    #Zählung der Treffer
    Zi,Zis=0,0
    yh=h(xz)
    yhs=hs(xz)
    for i in range(N):
        if yh[i]>=yz1[i]:
            Zi += 1
        if yhs[i]>=yz2[i]:
            Zis += 1
    #Rückgabe Näherung
    return A1*(Zi/N), A2*(Zis/N)

from core.analytisch import stammint

def errmonte(err, a, b, h, hs,k=10):
    """
    Ermittelt eine Stichprobengröße N (in Schritten von k), sodass die Monte Carlo Näherung den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - MC|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        k (int): Schrittweite, mit der N erhöht wird

    Rückgabe:
        tuple: (N1, N2, mc1, mc2)
            N1 (int): Stichprobengröße für h, bei der der Fehler <= err ist
            N2 (int): Stichprobengröße für hs, bei der der Fehler <= err ist
            mc1 (float): Monte Carlo Näherungswert für h bei N1
            mc2 (float): Monte Carlo Näherungswert für hs bei N2
    """
    # Referenzintegrale (sehr genau)
    A1, A2, _, _ = stammint(a, b, h, hs)
    # Startwerte
    mc1, N1 = 0.0, 0
    mc2, N2 = 0.0, 0
    # Monte-Carlo konvergiert nicht monoton ist ja zufallsbasiert!
    # Deswegen können diese Schleifen schon etwas lange laufen.=> zeigt Schwäche Monte Carlo
    while abs(A1 - mc1) > err:
        N1 += k
        mc1 = geomonte(N1, a, b, h, hs)[0]
    while abs(A2 - mc2) > err:
        N2 += k
        mc2 = geomonte(N2, a, b, h, hs)[1]
    #Rückgabe
    return N1, N2, mc1, mc2
