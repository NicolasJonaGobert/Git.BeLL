import numpy as np

def riemann_untersumme(nr, a, b, h, hs):
    """
    Berechnet die Riemann Untersumme für zwei Funktionen h und hs auf dem Intervall [a,b] mit nr Teilintervallen.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)

    Rückgabe:
        tuple: (U_h, U_hs)
            U_h (float): Untersumme von h auf [a,b]
            U_hs (float): Untersumme von hs auf [a,b]
    """
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rsu1 = 0.0   # für h
    rsu2 = 0.0   # für hs
    v=h(xr)#y Werte h
    w=hs(xr)#y Werte hs
    for i in range(nr):
        # Untersumme: kleinerer Wert
        rsu1 += min(v[i], v[i+1])
        rsu2 += min(w[i], w[i+1])
    # mit dx multiplizieren
    return rsu1 * dx, rsu2 * dx

def riemann_obersumme(nr, a, b, h, hs):
    """
    Berechnet die Riemann Obersumme für zwei Funktionen h und hs auf dem Intervall [a,b] mit nr Teilintervallen.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)

    Rückgabe:
        tuple: (O_h, O_hs)
            O_h (float): Obersumme von h auf [a,b]
            O_hs (float): Obersumme von hs auf [a,b]
    """
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rso1 = 0.0   # für h
    rso2 = 0.0   # für hs
    v=h(xr)#y Werte h
    w=hs(xr)#y Werte hs
    for i in range(nr):
        # Obersumme : größerer Wert
        rso1 += max(v[i], v[i+1])
        rso2 += max(w[i], w[i+1])
    # mit dx multiplizieren
    return rso1 * dx, rso2 * dx

def mittel_riemann(nr, a, b, h, hs):
    """
    Berechnet den Mittelwert aus Unter und Obersumme (Riemann Ø) für zwei Funktionen h und hs auf [a,b].

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)

    Rückgabe:
        tuple: (R_h, R_hs)
            R_h (float): Durchschnitt aus Unter und Obersumme von h
            R_hs (float): Durchschnitt aus Unter und Obersumme von hs
    """
    u1, u2 = riemann_untersumme(nr, a, b, h, hs)#Untersummenwerte
    o1, o2 = riemann_obersumme(nr, a, b, h, hs)#Obersummenwerte
    return (u1 + o1) / 2, (u2 + o2) / 2 #Berechnung Durchschnitt

from core.analytisch import stammint

def errunter(err,h,hs,a,b,k=1):
    """
    Ermittelt die kleinste Teilintervallzahl (in Schritten von k), sodass die Untersumme den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - U|
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der nr erhöht wird

    Rückgabe:
        tuple: (n1, n2, us1, us2)
            n1 (int): Teilintervallzahl für h, bei der der Fehler <= err ist
            n2 (int): Teilintervallzahl für hs, bei der der Fehler <= err ist
            us1 (float): Untersummenwert von h bei n1
            us2 (float): Untersummenwert von hs bei n2
    """
    # Referenzintegrale
    A1,A2,_,_= stammint(a,b,h,hs)
    # Start: n = 0 (noch keine Teilintervalle)
    us1,n1=0.0,0
    us2,n2=0.0,0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 1
    while abs(A1-us1)>err:
        n1 += k
        us1 = riemann_untersumme(n1,a,b,h,hs)[0]
    while abs(A2-us2)>err:
        n2 += k
        us2 = riemann_untersumme(n2,a,b,h,hs)[1]
    #Speicherung
    return n1,n2,us1,us2

def errober(err,h,hs,a,b,k=1):
    """
    Ermittelt die kleinste Teilintervallzahl (in Schritten von k), sodass die Obersumme den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - O|
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der nr erhöht wird

    Rückgabe:
        tuple: (n1, n2, os1, os2)
            n1 (int): Teilintervallzahl für h, bei der der Fehler <= err ist
            n2 (int): Teilintervallzahl für hs, bei der der Fehler <= err ist
            os1 (float): Obersummenwert von h bei n1
            os2 (float): Obersummenwert von hs bei n2
    """
    # Referenzintegrale
    A1,A2,_,_= stammint(a,b,h,hs)
    # Start: n = 0 (noch keine Teilintervalle)
    os1,n1=0.0,0
    os2,n2=0.0,0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 1
    while abs(A1-os1)>err:
        n1 += k
        os1 = riemann_obersumme(n1,a,b,h,hs)[0]
    while abs(A2-os2)>err:
        n2 += k
        os2 = riemann_obersumme(n2,a,b,h,hs)[1]
    #Speicherung
    return n1,n2,os1,os2

def err_mittel_riemann(err,a,b,h,hs,k=1):
    """
    Ermittelt die kleinste Teilintervallzahl (in Schritten von k), sodass der Mittelwert aus Unter und Obersumme den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - R|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Erste Funktion h(x)
        hs (callable): Zweite Funktion hs(x)
        k (int): Schrittweite, mit der nr erhöht wird

    Rückgabe:
        tuple: (nr1, nr2, rs1, rs2)
            nr1 (int): Teilintervallzahl für h, bei der der Fehler <= err ist
            nr2 (int): Teilintervallzahl für hs, bei der der Fehler <= err ist
            rs1 (float): Riemann-Ø Wert von h bei nr1
            rs2 (float): Riemann-Ø Wert von hs bei nr2
    """
    # Referenzintegrale
    A1, A2, _, _ = stammint(a, b, h, hs)
    # Start: n = 0 (noch keine Teilintervalle)
    rs1,rs2=0.0,0.0
    nr1,nr2=0,0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 1
    while abs(A1-rs1)>err:
        nr1 += k
        rs1 = mittel_riemann(nr1, a, b, h, hs)[0]
    while abs(A2-rs2)>err:
        nr2 += k
        rs2 = mittel_riemann(nr2, a, b, h, hs)[1]
    #Speicherung
    return nr1,nr2,rs1,rs2
