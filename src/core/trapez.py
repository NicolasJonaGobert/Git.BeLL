def trapezregel(nt,h,hs,a,b):
    """
    Berechnet die Trapezregel-Näherung für zwei Funktionen h und hs auf dem Intervall [a,b] mit nt Teilintervallen.

    Parameter:
        nt (int): Anzahl der Teilintervalle der Zerlegung
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze

    Rückgabe:
        tuple: (T_h, T_hs)
            T_h (float): Trapezregel-Näherung für h auf [a,b]
            T_hs (float): Trapezregel-Näherung für hs auf [a,b]
    """
    #Feinheit der Zerlegung
    dx=(b-a)/nt
    #Stützstellen
    xt=np.linspace(a,b,nt+1)
    #Berechnung der Trapezsumme
    yt1=h(xt)#y-Werte h
    yt2=hs(xt)#y-Werte hs
    ts1,ts2=(yt1[0]+yt1[-1])*0.5+np.sum(yt1[1:-1]),(yt2[0]+yt2[-1])*0.5+np.sum(yt2[1:-1])#Berechnung der Trapezsumme für h und hs
    return ts1*dx, ts2*dx

from core.analytisch import stammint

def trapezerr(err,h,hs,a,b,k=1):
    """
    Ermittelt die kleinste Teilintervallzahl (in Schritten von k), sodass die Trapezregel den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - T|
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der nt erhöht wird

    Rückgabe:
        tuple: (nt1, nt2, ts1, ts2)
            nt1 (int): Teilintervallzahl für h, bei der der Fehler <= err ist
            nt2 (int): Teilintervallzahl für hs, bei der der Fehler <= err ist
            ts1 (float): Trapezregel-Wert für h bei nt1
            ts2 (float): Trapezregel-Wert für hs bei nt2
    """
    # Referenzintegrale
    A1,A2,_,_=stammint(a,b,h,hs)
    # Start: nt = 0 (noch keine Teilintervalle), erste Rechnung bei nt = 1
    ts1,nt1=0.0,0
    ts2,nt2=0.0,0
    # nt1 erhöhen, bis Trapezregel für h nah genug am Referenzwert A1 ist
    while abs(A1-ts1)>err:
        nt1+=k
        ts1=trapezregel(nt1,h,hs,a,b)[0]
    # nt2 erhöhen, bis Trapezregel für hs nah genug am Referenzwert A2 ist
    while abs(A2-ts2)>err:
        nt2+=k
        ts2=trapezregel(nt2,h,hs,a,b)[1]
    # Rückgabe
    return nt1,nt2,ts1,ts2
