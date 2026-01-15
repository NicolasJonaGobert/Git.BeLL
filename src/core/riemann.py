import numpy as np

def riemann_untersumme(nr, a, b, f,f_raw,k=2000):
    """
    Berechnet eine approximierte Riemann-Untersumme auf [a,b], indem pro Teilintervall das Minimum durch feines Abtasten angenähert wird.
    Zusätzlich wird pro Teilintervall genau ein gezählter Funktionsaufruf über f(x) durchgeführt (Fairness), während die Abtastung über f_raw ungezählt bleibt.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Gezählt ausgewertete Funktion (z.B. CountedFunction), dient nur zur Aufrufzählung
        f_raw (callable): Ungezählte Funktion für das feine Abtasten (liefert Werte für Min-Approximation)
        k (int): Anzahl der Abtastpunkte pro Teilintervall zur Approximation des Minimums

    Rückgabe:
        float: Approximierte Untersumme (Integralnäherung) auf [a,b]
    """
    # Berechnet die untersumme (angenähert da ymin nur approximiert)
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rsu = 0.0   # noch Null
    fr=f_raw#Ungezählte Abtast-Funktion
    for i in range(nr):
        # 1 gezählter Call pro Intervall (Fairness)
        xm = 0.5 * (xr[i] + xr[i+1])
        _ = f(xm)  # zählt genau 1 Call (Wert wird nicht benutzt)
        # Feines Abtasten im i-ten Teilintervall
        xapr=np.linspace(xr[i], xr[i+1], k)#x-Werte auf i Intervall
        ym=fr(xapr)#jeweilige y-Werte
        ymin=float(np.min(ym))#kleinsten Speichern
        rsu+=ymin
    # mit dx multiplizieren
    return rsu * dx

def riemann_obersumme(nr, a, b, f,f_raw,k=2000):
    """
    Berechnet eine approximierte Riemann-Obersumme auf [a,b], indem pro Teilintervall das Maximum durch feines Abtasten angenähert wird.
    Zusätzlich wird pro Teilintervall genau ein gezählter Funktionsaufruf über f(x) durchgeführt (Fairness), während die Abtastung über f_raw ungezählt bleibt.

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Gezählt ausgewertete Funktion (z.B. CountedFunction), dient nur zur Aufrufzählung
        f_raw (callable): Ungezählte Funktion für das feine Abtasten (liefert Werte für Max-Approximation)
        k (int): Anzahl der Abtastpunkte pro Teilintervall zur Approximation des Maximums

    Rückgabe:
        float: Approximierte Obersumme (Integralnäherung) auf [a,b]
    """
    #Berechnet die obersumme (angenähert da ymax nur approximiert)
    # Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rso = 0.0  # noch Null
    fr = f_raw  # Ungezählte Abtast-Funktion
    for i in range(nr):
        # 1 gezählter Call pro Intervall (Fairness)
        xm = 0.5 * (xr[i] + xr[i+1])
        _ = f(xm)  # zählt genau 1 Call (Wert wird nicht benutzt)
        # Feines Abtasten im i-ten Teilintervall
        xapr = np.linspace(xr[i], xr[i + 1], k)  # x-Werte auf i Intervall
        ym = fr(xapr)  # jeweilige y-Werte
        ymax = float(np.max(ym))  # größten Speichern
        rso += ymax
    # mit dx multiplizieren
    return rso * dx

def mittel_riemann(nr, a, b, h, hs,f_raw,k=2000,mode=0):
    """
    Berechnet den Mittelwert aus approximierter Unter- und Obersumme (Riemann-Ø) für h oder hs auf [a,b].

    Parameter:
        nr (int): Anzahl der Teilintervalle der Zerlegung
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Gezählt ausgewertete Funktion h(x)
        hs (callable): Gezählt ausgewertete Funktion hs(x)
        f_raw (callable): Ungezählte Funktion für feines Abtasten in Unter-/Obersumme
        k (int): Anzahl der Abtastpunkte pro Teilintervall in Unter-/Obersumme
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        float: Riemann-Mittelwert (Durchschnitt aus Unter- und Obersumme) der gewählten Funktion auf [a,b]
    """
    #Berechnung des Durchschnitts aus OS und US
    if mode == 0:
        u, o = riemann_untersumme(nr, a, b, h,f_raw, k),riemann_obersumme(nr, a, b, h,f_raw, k)#Untersummenwerte
    elif mode == 1:
        u, o = riemann_untersumme(nr, a, b, hs,f_raw, k),riemann_obersumme(nr, a, b, hs,f_raw, k)#Obersummenwerte
    return (u + o) / 2#Berechnung Durchschnitt


def errunter(err,h,hs,a,b,f_raw,Ai,k=1,k1=2000,mode=0):
    """
    Erhöht n iterativ (potenzen von 2), bis die approximierte Untersumme den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |Ai - Untersumme|
        h (callable): Gezählt ausgewertete Funktion h(x)
        hs (callable): Gezählt ausgewertete Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f_raw (callable): Ungezählte Funktion für feines Abtasten in der Untersumme
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite, mit der der Exponent q erhöht wird (n = 2**q)
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall zur Minimum-Approximation
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (n, us)
            n (int): Gefundene Teilintervallzahl (als Potenz von 2)
            us (float): Untersummen-Näherung bei diesem n
    """
    # Funktion die untersumme solange ausführt bis err erreicht
    """
 Wenn mode==0 dann h, wenn mode==1 dann hs
    """
    # Start: n = 0 (noch keine Teilintervalle)
    us,n,q=0.0,1,1
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 2
    while True:
        if mode==0:
            us = riemann_untersumme(n, a, b, h,f_raw, k1)
            # Stoppen wenn err erreicht
            if abs(Ai-us)<err:
                break
            else:
                n = 2 ** q
                q+=k
        elif mode==1:
            us = riemann_untersumme(n, a, b, hs,f_raw, k1)
            # Stoppen wenn err erreicht
            if abs(Ai - us) < err:
                break
            else:
                n = 2 ** q
                q+=k
    #Speicherung
    return n,us

def errober(err, h, hs, a, b,f_raw,Ai, k=1, k1=2000, mode=0):
    """
    Erhöht n iterativ (potenzen von 2), bis die approximierte Obersumme den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |Ai - Obersumme|
        h (callable): Gezählt ausgewertete Funktion h(x)
        hs (callable): Gezählt ausgewertete Funktion hs(x)
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f_raw (callable): Ungezählte Funktion für feines Abtasten in der Obersumme
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite, mit der der Exponent q erhöht wird (n = 2**q)
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall zur Maximum-Approximation
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (n, os)
            n (int): Gefundene Teilintervallzahl (als Potenz von 2)
            os (float): Obersummen-Näherung bei diesem n
    """
    # Funktion die obersumme solange ausführt bis err erreicht
    """
 Wenn mode==0 dann h, wenn mode==1 dann hs
    """
    # Start: n = 0 (noch keine Teilintervalle)
    os, n,q = 0.0, 1,1
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 1
    while True:
        if mode==0:
            os = riemann_obersumme(n, a, b, h,f_raw, k1)
            # Stoppen wenn err erreicht
            if abs(Ai-os)<err:
                break
            #Erhöhen n und k
            else:
                n = 2 ** q
                q+=k
        elif mode==1:
            os = riemann_obersumme(n, a, b, hs,f_raw, k1)
            # Stoppen wenn err erreicht
            if abs(Ai - os) < err:
                break
            else:
                n = 2 ** q
                q+=k
    # Speicherung
    return n, os

def err_mittel_riemann(err,a,b,h,hs,f_raw,Ai,k=1,k1=2000,mode=0):
    """
    Erhöht n iterativ (potenzen von 2), bis der Mittelwert aus Unter- und Obersumme (Riemann-Ø) den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |Ai - RiemannØ|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Gezählt ausgewertete Funktion h(x)
        hs (callable): Gezählt ausgewertete Funktion hs(x)
        f_raw (callable): Ungezählte Funktion für feines Abtasten in Unter-/Obersumme
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite, mit der der Exponent q erhöht wird (n = 2**q)
        k1 (int): Anzahl der Abtastpunkte pro Teilintervall in Unter-/Obersumme
        mode (int): 0 nutzt h, 1 nutzt hs

    Rückgabe:
        tuple: (n, rs)
            n (int): Gefundene Teilintervallzahl (als Potenz von 2)
            rs (float): Riemann-Ø Näherung bei diesem n
    """
    #Funktion die mittelriemann solange ausführt bis err erreicht
    # Start: n = 0 (noch keine Teilintervalle)
    rs,n,q=0.0,1,1
    # Erhöhe n so lange, bis der Fehler klein genug ist
    # Erste Rechnung erfolgt bei n = 1
    while True:
        if mode==0:
            rs = mittel_riemann(n, a, b, h, hs,f_raw,k,mode)#berechnung
            #Stoppen wenn err erreicht
            if abs(Ai-rs)<err:
                break
            else:
                n = 2 ** q
                q+=k
        elif mode==1:
            rs = mittel_riemann(n, a, b, h, hs,f_raw,k,mode)#berechnung
            # Stoppen wenn err erreicht
            if abs(Ai - rs) < err:
                break
            else:
                n = 2 ** q
                q+=k
    #Speicherung
    return n,rs
