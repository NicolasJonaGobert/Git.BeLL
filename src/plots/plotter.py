import numpy as np
from utils.validation import _eval_y

def plot_funktionen_fläche(ax, a, b, f1, f2):
    """
    Plottet zwei Funktionen auf [a,b] und markiert die Fläche zwischen ihnen.

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f1 (callable): Erste Funktion f1(x), auswertbar für Skalar oder Array
        f2 (callable): Zweite Funktion f2(x), auswertbar für Skalar oder Array

    Rückgabe:
        None
    """
    xp = np.linspace(a, b, 10000)
    y1 = _eval_y(f1, xp)
    y2 = _eval_y(f2, xp)
    #Ausgabe Plot
    ax.plot(xp, y1, color="blue", label="$f_1(x)$")
    ax.plot(xp, y2, color="red", label="$f_2(x)$")
    ax.fill_between(
        xp, y1, y2,
        alpha=0.25,
        color="green",
        label="Fläche zwischen $f_1(x)$ und $f_2(x)$"
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()



def plot_betrag(ax, a, b, f):
    """
    Plottet eine Funktion f auf [a,b] und schattiert die Fläche unter der Kurve.

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Funktion, die geplottet werden soll (typisch: Betragsfunktion B(x))

    Rückgabe:
        None
    """
    # x-Werte für Plot
    xp = np.linspace(a, b, 10000)
    # Funktionswerte einmal berechnen
    y1 = _eval_y(f, xp)
    # Plotten der Funktion
    ax.plot(xp, y1, color="red", label="$B(x)$")  # Plot Betragsfunktion
    ax.fill_between(xp, y1, alpha=0.25, color="blue",
                    label="Fläche unter $B(x)$")  # Fläche unter B(x)
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()


def plot_riemannsumme(ax, a, b, nr, f, mode="u", k=2000):
    """
    Plottet die Funktion f auf [a,b] und zeichnet dazu Riemann-Rechtecke (Unter- oder Obersumme).

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nr (int): Anzahl der Teilintervalle (Riemann-Rechtecke)
        f (callable): Funktion, die geplottet und über Rechtecke angenähert wird
        mode (str): "u" für Untersumme (Minimum je Teilintervall), "o" für Obersumme (Maximum je Teilintervall)
        k (int): Anzahl Abtastpunkte pro Teilintervall zur Min/Max-Bestimmung

    Rückgabe:
        None
    """
    """
    Plottet die Betragsfunktion B(x) und Riemann-Rechtecke.
    mode:
      "u" -> Untersumme (min auf dem Teilintervall)
      "o" -> Obersumme  (max auf dem Teilintervall)

    k = Anzahl Abtastpunkte pro Teilintervall (größer -> genauer, langsamer)
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = _eval_y(f, xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")
    # Stützstellen der Zerlegung
    dx = (b - a) / nr
    xre = np.linspace(a, b, nr + 1)
    # Rechteckhöhen: wirkliches Min/Max pro Teilintervall über Abtastung
    heights = np.zeros(nr)
    for i in range(nr):
        xseg = np.linspace(xre[i], xre[i + 1], k)  # Abtastpunkte im Teilintervall
        yseg = _eval_y(f, xseg)                           # Funktionswerte dort
        if mode == "u":
            heights[i] = float(np.min(yseg))       # Minimum im Teilintervall
        elif mode == "o":
            heights[i] = float(np.max(yseg))       # Maximum im Teilintervall
        else:
            raise ValueError("mode muss 'u' oder 'o' sein")
    # Farben/Labels
    if mode == "u":
        label_rect = "Untersumme"
        color_rect = "green"
    else:
        label_rect = "Obersumme"
        color_rect = "blue"
    # Rechtecke zeichnen (linke Kante bei xre[:-1])
    ax.bar(
        xre[:-1],
        heights,
        width=dx,
        align="edge",
        alpha=0.3,
        color=color_rect,
        edgecolor="black",
        label=label_rect,
        zorder=3
    )
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    if nr >= 500:
        ax.legend(loc="upper left")
    else:
        ax.legend(loc="best")



def plot_trapezregel(ax, a, b, nt, f):
    """
    Plottet die Funktion f auf [a,b] und visualisiert die Trapezregel durch gefüllte Trapezflächen.

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nt (int): Anzahl der Teilintervalle für die Trapezregel
        f (callable): Funktion, die geplottet und per Trapezen angenähert wird

    Rückgabe:
        None
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = _eval_y(f, xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")
    # Plot der Trapeze
    xt = np.linspace(a, b, nt + 1)  # Stützstellen
    yt = _eval_y(f, xt)
    # Plotten von nt Trapezen
    for i in range(nt):
        # Label soll nur einmal erscheinen
        if i == 0:
            ax.fill_between(
                xt[i:i+2], 0, yt[i:i+2],
                alpha=0.25,
                color="green",
                label="Trapeze unter $B(x)$"
            )
        else:
            ax.fill_between(
                xt[i:i+2], 0, yt[i:i+2],
                alpha=0.25,
                color="green"
            )
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    if nt >= 500:
        ax.legend(loc="upper left")
    else:
        ax.legend(loc="best")


def plot_simpson(ax, a, b, ns, f):
    """
    Plottet die Funktion f auf [a,b] und visualisiert die Simpsonregel über Interpolationsparabeln.

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        ns (int): Anzahl der Teilintervalle (muss gerade sein, da Simpson über Zweierintervalle arbeitet)
        f (callable): Funktion, die geplottet und per Simpson-Interpolation angenähert wird

    Rückgabe:
        None
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = _eval_y(f, xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")

    # Plot Interpolationspolynome
    # Feinheit der Zerlegung
    h = (b - a) / ns
    # Stützstellen
    xp = np.linspace(a, b, ns + 1)
    ys = _eval_y(f, xp)
    # Interpolationsparabel
    def p(x, index, h, xp):
        return (1 / (h ** 2)) * (
            0.5 * ys[index] * (x - xp[index + 1]) * (x - xp[index + 2])
            - ys[index+1] * (x - xp[index]) * (x - xp[index + 2])
            + 0.5 * ys[index+2] * (x - xp[index]) * (x - xp[index + 1])
        )
    # Plot Parabeln in Zweierintervallen
    for i in range(0, ns, 2):
        xp1 = np.linspace(xp[i], xp[i + 2], 2000)
        yint = p(xp1, i, h, xp)
        if i == 0:
            ax.plot(xp1, yint, color="green", label="Interpolationsparabeln")
            ax.fill_between(
                xp1, 0, yint,
                color="blue",
                alpha=0.25,
                edgecolor="black",
                linewidth=2,
                zorder=3,
                label="Fläche unter Parabeln"
            )
        else:
            ax.plot(xp1, yint, color="green")
            ax.fill_between(
                xp1, 0, yint,
                color="blue",
                alpha=0.25,
                edgecolor="black",
                linewidth=2,
                zorder=3
            )
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    if ns>=500:
        ax.legend(loc="upper left")
    else:
        ax.legend(loc="best")


def plot_monte(ax, a, b, N,f,kma,xz,yz,T,w="h"):
    """
    Plottet die Funktion f auf [a,b] und zeigt dazu die Monte-Carlo-Zufallspunkte (mit Trefferanzahl).

    Parameter:
        ax (matplotlib.axes.Axes): Ziel-Achse, in die gezeichnet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        N (int): Anzahl der Monte-Carlo-Zufallspunkte
        f (callable): Funktion, zu der Monte Carlo visualisiert wird (B(x) oder B_s(x))
        kma (int): Parameter/Steuergröße aus dem Programmkontext (hier nicht direkt verwendet)
        xz (array-like): x-Koordinaten der Zufallspunkte
        yz (array-like): y-Koordinaten der Zufallspunkte
        T (int): Trefferanzahl (Punkte unter der Kurve)
        w (str): "h" für B(x), "hs" für B_s(x) (nur für Labeling)

    Rückgabe:
        None
    """
    """
    w = "h"  -> Monte Carlo für h
    w = "hs" -> Monte Carlo für hs
    """
    # Feiner Plot der Kurve
    xp = np.linspace(a, b, 10000)
    # Zufallspunkte und Funktion Plotten
    if w=="hs":
        ax.plot(xp, _eval_y(f,xp), color="red", label="$B_s(x)$")
    else:
        ax.plot(xp, _eval_y(f,xp), color="red", label="$B(x)$")
    ax.plot(xz, yz,
            'o',
            color="blue",
            markersize=3,
            label=f"Zufallspunkte mit {T} Treffern (N={N})")
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    if N >= 500:
        ax.legend(loc="upper left")
    else:
        ax.legend(loc="best")
