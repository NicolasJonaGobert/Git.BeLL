def riemann_untersumme(nr, a, b, h, hs):
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rsu1 = 0.0   # für h
    rsu2 = 0.0   # für hs
    for i in range(nr):
        # Werte an den Intervallrändern
        v1 = h(xr[i])
        v2 = h(xr[i + 1])
        w1 = hs(xr[i])
        w2 = hs(xr[i + 1])
        # Untersumme: kleinerer Wert
        rsu1 += min(v1, v2)
        rsu2 += min(w1, w2)
    # mit dx multiplizieren
    return rsu1 * dx, rsu2 * dx

def riemann_obersumme(nr, a, b, h, hs):
    #Feinheit der Zerlegung
    dx = (b - a) / nr
    # Teilpunkte
    xr = np.linspace(a, b, nr + 1)
    # Summen
    rso1 = 0.0   # für h
    rso2 = 0.0   # für hs
    for i in range(nr):
        # Werte an den Intervallrändern
        v1 = h(xr[i])
        v2 = h(xr[i + 1])
        w1 = hs(xr[i])
        w2 = hs(xr[i + 1])
        # Obersumme : größerer Wert
        rso1 += max(v1, v2)
        rso2 += max(w1, w2)
    # mit dx multiplizieren
    return rso1 * dx, rso2 * dx

def mittel_riemann(nr, a, b, h, hs):
    u1, u2 = riemann_untersumme(nr, a, b, h, hs)#Untersummenwerte
    o1, o2 = riemann_obersumme(nr, a, b, h, hs)#Obersummenwerte
    return (u1 + o1) / 2, (u2 + o2) / 2 #Berechnung Durchschnitt
