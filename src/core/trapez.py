import numpy as np

def trapezregel(nt,h,hs,a,b):
    #Feinheit der Zerlegung
    dx=(b-a)/nt
    #Stützstellen
    xt=np.linspace(a,b,nt+1)
    #Berechnung der Trapezsumme
    ts1,ts2=(h(xt[0])+h(xt[-1]))*0.5+np.sum(h(xt[1:-1])),(hs(xt[0])+hs(xt[-1]))*0.5+np.sum(hs(xt[1:-1]))
    return ts1*dx, ts2*dx