import numpy as np

def geomonte(N,a,b,h,hs):
    #Annäherung der globalen Maxima von h und hs
    xapr=np.linspace(a,b,5000)#x-Werte um Funktion abzutasten
    y1max=float(max(h(xapr)))#Maximum h
    y2max=float(max(hs(xapr)))#Maximum h
    #Berechnung Rechteckfläche
    A1,A2=(b-a)*y1max,(b-a)*y2max
    #Zufallsgenerierung der Punkte
    xz = np.random.uniform(a, b, N)  # Zufällige x-Werte für beide h und hs
    yz1 = np.random.uniform(0,y1max, N) # Zufällige y-Werte für h
    yz2 = np.random.uniform(0,y2max, N) # Zufällige y-Werte für hs
    #Zählung der Treffer
    Zi,Zis=0,0
    for i in range(N):
        if h(xz[i])>=yz1[i]:
            Zi += 1
        if hs(xz[i])>=yz2[i]:
            Zis += 1
    return A1*(Zi/N), A2*(Zis/N)