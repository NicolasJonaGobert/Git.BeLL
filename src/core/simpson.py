import numpy as np

def simpsonregel(h,hs,ns,a,b):
    """
    Berechnet die Simpsonregel-Näherung für zwei Funktionen h und hs auf dem Intervall [a,b] mit ns Teilintervallen.

    Parameter:
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        ns (int): Anzahl der Teilintervalle der Zerlegung (muss gerade sein)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze

    Rückgabe:
        tuple: (S_h, S_hs)
            S_h (float): Simpsonregel-Näherung für h auf [a,b]
            S_hs (float): Simpsonregel-Näherung für hs auf [a,b]
    """
    #Feinheit der Zerlegung
    dx = (b - a) / ns
    #Stützstellen
    xs=np.linspace(a,b,ns+1)
    # Berechnung der Simpson-Summen
    ys1=h(xs)
    ys2=hs(xs)
    ss1,ss2 = ys1[0]+ys1[-1],ys2[0]+ys2[-1]
    for i in range(1, ns):
        if i % 2 == 0:  # summe für alle geraden i
            ss1+=2*ys1[i]
            ss2+=2*ys2[i]
        elif i % 2 == 1:  # summe für alle ungeraden i
            ss1 += 4 * ys1[i]
            ss2 += 4 * ys2[i]
    return  ss1*(dx/3), ss2*(dx/3)

from core.analytisch import stammint

def simpsonerr(h,hs,err,a,b,k=2):
    """
    Ermittelt die kleinste gerade Teilintervallzahl (in Schritten von k), sodass die Simpsonregel den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        err (float): Fehlertoleranz für |I_ref - S|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der ns erhöht wird (standardmäßig 2, damit ns gerade bleibt)

    Rückgabe:
        tuple: (ns1, ns2, ss1, ss2)
            ns1 (int): Teilintervallzahl für h (gerade), bei der der Fehler <= err ist
            ns2 (int): Teilintervallzahl für hs (gerade), bei der der Fehler <= err ist
            ss1 (float): Simpsonregel-Wert für h bei ns1
            ss2 (float): Simpsonregel-Wert für hs bei ns2
    """
    # Referenzintegrale
    A1, A2, _, _ = stammint(a, b, h, hs)
    # Start: ns = 0 (noch keine Teilintervalle), erste Rechnung bei ns = 2
    ss1, ns1 = 0.0,0# Simpson-Näherung und ns1 für h
    ss2, ns2 = 0.0,0# Simpson-Näherung und ns2 für hs
    # ns1 erhöhen, bis Simpsonregel für h nah genug am Referenzwert A1 ist
    while abs(A1-ss1)>err:
        ns1+=k #n muss immer gerade sein
        ss1 = simpsonregel(h,hs,ns1,a,b)[0]
    # ns2 erhöhen, bis Simpsonregel für hs nah genug am Referenzwert A2 ist
    while abs(A2-ss2)>err:
        ns2 += k #n muss immer gerade sein
        ss2 = simpsonregel(h,hs,ns2,a,b)[1]
    #Rückgabe
    return ns1,ns2,ss1,ss2
