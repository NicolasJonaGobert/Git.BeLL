import numpy as np

def riemann_untersumme(nr, a, b, f,k=2000):
    """
    Berechnet eine approximierte Riemann Untersumme für f auf [a,b], indem in jedem Teilintervall das Minimum durch feines Abtasten geschätzt wird.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Funktion f(x), die integriert/ausgewertet wird
        k (int): Anzahl der Abtastpunkte pro Teilintervall zur Minimum-Schätzung

    Rückgabe:
        float: Approximierte Untersumme von f auf [a,b]
    """
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rsu = 0.0   # noch Null
    for i in range(nr):
        # Feines Abtasten im i-ten Teilintervall
        xapr=np.linspace(xr[i], xr[i+1], k)#x-Werte auf i Intervall
        ym=f(xapr)#jeweilige y-Werte
        ymin=float(np.min(ym))#kleinsten Speichern
        rsu+=ymin
    # mit dx multiplizieren
    return rsu * dx

def riemann_obersumme(nr, a, b, f,k=2000):
    """
    Berechnet eine approximierte Riemann Obersumme für f auf [a,b], indem in jedem Teilintervall das Maximum durch feines Abtasten geschätzt wird.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Funktion f(x), die integriert/ausgewertet wird
        k (int): Anzahl der Abtastpunkte pro Teilintervall zur Maximum-Schätzung

    Rückgabe:
        float: Approximierte Obersumme von f auf [a,b]
    """
    # Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rso = 0.0  # noch Null
    for i in range(nr):
        # Feines Abtasten im i-ten Teilintervall
        xapr = np.linspace(xr[i], xr[i + 1], k)  # x-Werte auf i Intervall
        ym = f(xapr)  # jeweilige y-Werte
        ymax = float(np.max(ym))  # größten Speichern
        rso += ymax
    # mit dx multiplizieren
    return rso * dx

def mittel_riemann(nr, a, b, h, hs,k=2000,mode=0):
    """
    Berechnet den Mittelwert aus approximierter Unter- und Obersumme (Riemann Ø) für h oder hs auf [a,b].

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        k (int): Anzahl der Abtastpunkte pro Teilintervall zur Min/Max-Schätzung
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Approximierter Riemann-Ø Wert (Durchschnitt aus Unter- und Obersumme) der gewählten Funktion
    """
    if mode == 0:
        u, o = riemann_untersumme(nr, a, b, h, k),riemann_obersumme(nr, a, b, h, k)#Untersummenwerte
    elif mode == 1:
        u, o = riemann_untersumme(nr, a, b, hs, k),riemann_obersumme(nr, a, b, hs, k)#Obersummenwerte
    return (u + o) / 2#Berechnung Durchschnitt

from core.analytisch import stammint

def errunter(err,h,hs,a,b,k=1,k1=2000,mode=0):
    """
    Ermittelt eine Teilintervallzahl n (in Schritten von k), sodass die approximierte Untersumme den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - U|
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der n erhöht wird
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall zur Minimum-Schätzung
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (n, us)
            n (int): Teilintervallzahl, bei der der Fehler <= err ist
            us (float): Untersummenwert der Zielfunktion bei n
    """
    """
 Wenn mode==0 dann h, wenn mode==1 dann hs
    """
    # Referenzintegrale
    Ai,_ = stammint(a, b, h, hs,mode)
    # Start: n = 0 (noch keine Teilintervalle)
    us,n=0.0,0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = k
    while True:
        if mode==0:
            n += k
            us = riemann_untersumme(n, a, b, h, k1)
            if abs(Ai-us)<err:
                break
        elif mode==1:
            n += k
            us = riemann_untersumme(n, a, b, hs, k1)
            if abs(Ai - us) < err:
                break
    #Speicherung
    return n,us

def errober(err, h, hs, a, b, k=1, k1=2000, mode=0):
    """
    Ermittelt eine Teilintervallzahl n (in Schritten von k), sodass die approximierte Obersumme den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - O|
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        k (int): Schrittweite, mit der n erhöht wird
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall zur Maximum-Schätzung
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (n, os)
            n (int): Teilintervallzahl, bei der der Fehler <= err ist
            os (float): Obersummenwert der Zielfunktion bei n
    """
    """
 Wenn mode==0 dann h, wenn mode==1 dann hs
    """
    # Referenzintegrale
    Ai,_ = stammint(a, b, h, hs,mode)
    # Start: n = 0 (noch keine Teilintervalle)
    os, n = 0.0, 0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = k
    while True:
        if mode==0:
            n += k
            os = riemann_obersumme(n, a, b, h, k1)
            if abs(Ai-os)<err:
                break
        elif mode==1:
            n += k
            os = riemann_obersumme(n, a, b, hs, k1)
            if abs(Ai - os) < err:
                break
    # Speicherung
    return n, os

def err_mittel_riemann(err,a,b,h,hs,k=1,k1=2000,mode=0):
    """
    Ermittelt eine Teilintervallzahl n (in Schritten von k), sodass der approximierte Riemann-Ø Wert den Fehler err gegenüber dem Referenzintegral unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |I_ref - R|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        k (int): Schrittweite, mit der n erhöht wird
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall zur Min/Max-Schätzung
        mode (int): 0 nutzt h als Zielfunktion, 1 nutzt hs als Zielfunktion

    Rückgabe:
        tuple: (n, rs)
            n (int): Teilintervallzahl, bei der der Fehler <= err ist
            rs (float): Riemann-Ø Wert der Zielfunktion bei n
    """
    # Referenzintegrale
    Ai,_ = stammint(a, b, h, hs,mode)
    # Start: n = 0 (noch keine Teilintervalle)
    rs,n=0.0,0
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = k
    while True:
        if mode==0:
            n += k
            rs = mittel_riemann(n, a, b, h, hs,k,mode)
            if abs(Ai-rs)<err:
                break
        elif mode==1:
            n += k
            rs = mittel_riemann(n, a, b, h, hs,k,mode)
            if abs(Ai - rs) < err:
                break
    #Speicherung
    return n,rs
