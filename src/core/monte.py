import numpy as np
from core.functions import randomsmonte
from utils.validation import _eval_y

def geomonte(N, a, b, h, hs, kma, f_raw, mode=0, eps=1e-12):
    """
    Führt eine geometrische Monte-Carlo-Integration (Treffer-Methode) auf [a,b] für h oder hs aus.

    Es werden Zufallspunkte (xz, yz) in einem Rechteck der Höhe ymax erzeugt.
    Anschließend wird gezählt, wie viele Punkte unter der Kurve liegen (Treffer Zi).
    Die Funktion wird robust über _eval_y ausgewertet (z.B. für numerische Stabilität).

    Parameter:
        N (int): Anzahl der Zufallspunkte
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Anzahl der Abtastpunkte zur ymax-Approximation in randomsmonte
        f_raw (callable): Ungezählte/robuste Rohfunktion für die ymax-Bestimmung in randomsmonte
        mode (int): 0 nutzt h, 1 nutzt hs
        eps (float): Toleranz/Schutzparameter, wird an _eval_y weitergegeben

    Rückgabe:
        tuple: (I, Zi, xz, yz)
            I (float): Monte-Carlo-Näherung des Integrals
            Zi (int): Anzahl der Trefferpunkte (unter der Kurve)
            xz (np.ndarray): Zufällige x-Koordinaten
            yz (np.ndarray): Zufällige y-Koordinaten
    """
    # Zufallspunkte + ymax
    xz, yz, ymax = randomsmonte(a, b, N, h, hs, kma, f_raw, mode)
    # auf Arrays ziehen (der Rest wird über _eval_y abgefangen)
    xz = np.asarray(xz, dtype=float).ravel()
    yz = np.asarray(yz, dtype=float).ravel()
    ymax = float(np.asarray(ymax).ravel()[0])
    # Rechteckfläche
    A = (b - a) * ymax
    # passende Kurve wählen und robust auswerten
    f = h if mode == 0 else hs
    ycurve = _eval_y(f, xz, eps)
    # Treffer (vektorisiert)
    Zi = int(np.sum(ycurve >= yz))
    #Speicherung
    return A * (Zi / N), Zi, xz, yz

def errmonte(err, a, b, h, hs, kma, f_raw, Ai, k=10, mode=0, eps=1e-12):
    """
    Führt geomonte iterativ aus und erhöht N (als Potenz von 2), bis der Fehler err gegenüber dem Referenzwert Ai unterschritten wird.

    Parameter:
        err (float): Fehlertoleranz für |MonteCarlo - Ai|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Anzahl der Abtastpunkte zur ymax-Approximation in randomsmonte
        f_raw (callable): Ungezählte/robuste Rohfunktion für die ymax-Bestimmung in randomsmonte
        Ai (float): Referenzintegralwert der Zielfunktion
        k (int): Schrittweite für den Exponenten q (N = 2**q)
        mode (int): 0 nutzt h, 1 nutzt hs
        eps (float): Toleranz/Schutzparameter, wird an _eval_y weitergegeben

    Rückgabe:
        tuple: (N, mc, Zi)
            N (int): Verwendete Stichprobengröße (Potenz von 2)
            mc (float): Monte-Carlo-Näherung bei diesem N
            Zi (int): Trefferzahl aus dem letzten Lauf
    """
    #Funktion die MC berechnet bis err erreicht
    # Startwerte
    mc, N, q = 0.0, 1, 1
    # Monte-Carlo konvergiert nicht monoton (Zufallsverfahren)
    while True:
        mc, Zi, _, _ = geomonte(N, a, b, h, hs, kma, f_raw, mode) #Berechnung Annäherung und Treffer
        if abs(mc - Ai) < err:
            break
        else:
            N = 2 ** q  # neues N berechnen
            q += k
    # Rückgabe
    return N, mc, Zi

def mittel_monte(N, a, b, h, hs, kma, f_raw, wm, mode=0, eps=1e-12):
    """
    Berechnet den Mittelwert aus wm Monte-Carlo-Durchläufen (geomonte) mit festem N.

    Parameter:
        N (int): Anzahl der Zufallspunkte pro Monte-Carlo-Lauf
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Anzahl der Abtastpunkte zur ymax-Approximation in randomsmonte
        f_raw (callable): Ungezählte/robuste Rohfunktion für die ymax-Bestimmung in randomsmonte
        wm (int): Anzahl der Wiederholungen (Runs), über die gemittelt wird
        mode (int): 0 nutzt h, 1 nutzt hs
        eps (float): Toleranz/Schutzparameter (wird hier nicht direkt genutzt, ist als Parameter vorhanden)

    Rückgabe:
        float: Mittelwert der Monte-Carlo-Schätzer über wm Läufe
    """
    #Berechnet Mittelwert aus wm monte Carlo Durchläufen
    #Schätzer auf Null
    Is=0
    #wm Wiederholungen
    for i in range(wm):
        #Schätzer addieren
        Is += geomonte(N, a, b, h, hs, kma, f_raw, mode)[0]
    #Rückgabe Mittelwert
    return Is/wm

def err_mittel_monte(err, a, b, h, hs, kma, f_raw, wm, kmi, Ai, mode=0, eps=1e-12):
    """
    Erhöht N (als Potenz von 2), bis der Mittelwert aus wm Monte-Carlo-Läufen (mittel_monte)
    den Fehler err gegenüber dem Referenzwert Ai unterschreitet.

    Parameter:
        err (float): Fehlertoleranz für |Mittelwert - Ai|
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        kma (int): Anzahl der Abtastpunkte zur ymax-Approximation in randomsmonte
        f_raw (callable): Ungezählte/robuste Rohfunktion für die ymax-Bestimmung in randomsmonte
        wm (int): Anzahl der Wiederholungen für den Mittelwert-Schätzer
        kmi (int): Schrittweite für den Exponenten q (N = 2**q)
        Ai (float): Referenzintegralwert der Zielfunktion
        mode (int): 0 nutzt h, 1 nutzt hs
        eps (float): Toleranz/Schutzparameter (wird hier nicht direkt genutzt, ist als Parameter vorhanden)

    Rückgabe:
        tuple: (N, Am)
            N (int): Verwendete Stichprobengröße (Potenz von 2)
            Am (float): Mittelwert-Schätzer bei diesem N
    """
    #Berechnet mittel_monte bis err unterschritten
    #N,q auf 1
    N,q=1,1
    #Beginn der Schleife
    while True:
        #Berechnung des Mittelwerts aus wm Durchläufen
        Am=mittel_monte(N, a, b, h, hs, kma, f_raw,wm, mode)
        #Stopp wenn err unterschritten
        if abs(Am - Ai) < err:
            break
        else:
            N = 2 ** q
            q+=kmi
    #Rückgabe
    return N,Am
