import numpy as np

def simpsonregel(h,hs,ns,a,b):
    #Feinheit der Zerlegung
    dx = (b - a) / ns
    #Stützstellen
    xs=np.linspace(a,b,ns+1)
    # Berechnung der Simpson-Summen
    ss1,ss2 = h(xs[0])+h(xs[-1]),hs(xs[0])+hs(xs[-1])
    for i in range(1, ns):
        if i % 2 == 0:  # summe für alle geraden i
            ss1+=2*h(xs[i])
            ss2+=2*hs(xs[i])
        elif i % 2 == 1:  # summe für alle ungeraden i
            ss1 += 4 * h(xs[i])
            ss2 += 4 * hs(xs[i])
    return  ss1*(dx/3), ss2*(dx/3)