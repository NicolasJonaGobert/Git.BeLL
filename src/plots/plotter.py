import matplotlib.pyplot as plt
import numpy as np

def plot_funktionen_fläche(ax, a, b, f1, f2):
    """
    Plottet zwei Funktionen f1 und f2 auf [a,b] in ein gegebenes Axes-Objekt und markiert die Fläche zwischen ihnen.

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f1 (callable): Erste Funktion f1(x)
        f2 (callable): Zweite Funktion f2(x)

    Rückgabe:
        keine
    """
    # x-Werte für Plot
    xp = np.linspace(a, b, 10000)
    # Funktionswerte einmal berechnen
    y1 = f1(xp)
    y2 = f2(xp)
    # Plotten der Funktionen
    ax.plot(xp, y1, color="blue", label="$f_1(x)$")   # Plot f1
    ax.plot(xp, y2, color="red", label="$f_2(x)$")    # Plot f2
    # Fläche zwischen den Funktionen
    ax.fill_between(
        xp, y1, y2,
        alpha=0.25,
        color="green",
        label="Fläche zwischen $f_1(x)$ und $f_2(x)$"
    )
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()


def plot_betrag(ax, a, b, f):
    """
    Plottet eine Funktion f auf [a,b] in ein gegebenes Axes-Objekt und markiert die Fläche unter der Kurve.

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        f (callable): Funktion f(x), die geplottet werden soll

    Rückgabe:
        keine
    """
    # x-Werte für Plot
    xp = np.linspace(a, b, 10000)
    # Funktionswerte einmal berechnen
    y1 = f(xp)
    # Plotten der Funktion
    ax.plot(xp, y1, color="red", label="$B(x)$")  # Plot Betragsfunktion
    ax.fill_between(xp, y1, alpha=0.25, color="green",
                    label="Fläche unter $B(x)$")  # Fläche unter B(x)
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()


def plot_riemannsumme(ax, a, b, nr, f, mode="u"):
    """
    Plottet die Funktion f auf [a,b] in ein gegebenes Axes-Objekt und visualisiert Riemann-Rechtecke (Unter- oder Obersumme).

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nr (int): Anzahl der Teilintervalle der Zerlegung
        f (callable): Funktion f(x), die geplottet und angenähert wird
        mode (str): "u" für Untersumme, "o" für Obersumme

    Rückgabe:
        keine
    """
    """
    Plottet die Betragsfunktion B(x) und Riemann-Rechtecke.
    mode:
      "u" -> Untersumme (min an Intervallenden)
      "o" -> Obersumme  (max an Intervallenden)
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")
    # Stützstellen der Zerlegung
    dx = (b - a) / nr  # Feinheit
    xre = np.linspace(a, b, nr + 1)
    # Funktionswerte an Stützstellen nur einmal berechnen
    yre = f(xre)
    # Rechteckhöhen pro Intervall aus Endpunkten bestimmen
    y_left = yre[:-1]
    y_right = yre[1:]
    if mode == "u":
        heights = np.minimum(y_left, y_right)
        label_rect = "Untersumme"
        color_rect = "blue"
    elif mode == "o":
        heights = np.maximum(y_left, y_right)
        label_rect = "Obersumme"
        color_rect = "green"
    else:
        raise ValueError("mode muss 'u' oder 'o' sein")
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
    ax.legend()


def plot_trapezregel(ax, a, b, nt, f):
    """
    Plottet die Funktion f auf [a,b] in ein gegebenes Axes-Objekt und visualisiert die Trapeze der Trapezregel mit nt Teilintervallen.

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        nt (int): Anzahl der Teilintervalle der Zerlegung
        f (callable): Funktion f(x), die geplottet und durch Trapeze angenähert wird

    Rückgabe:
        keine
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")
    # Plot der Trapeze
    xt = np.linspace(a, b, nt + 1)  # Stützstellen
    yt = f(xt)
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
    ax.legend()


def plot_simpson(ax, a, b, ns, f):
    """
    Plottet die Funktion f auf [a,b] in ein gegebenes Axes-Objekt und visualisiert die Simpson-Interpolation (Parabeln) für ns Teilintervalle.

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        ns (int): Anzahl der Teilintervalle der Zerlegung (muss gerade sein)
        f (callable): Funktion f(x), die geplottet und durch Parabeln angenähert wird

    Rückgabe:
        keine
    """
    # Kurve fein plotten
    xp = np.linspace(a, b, 10000)
    yp = f(xp)
    ax.plot(xp, yp, color="red", label="$B(x)$")

    # Plot Interpolationspolynome
    # Feinheit der Zerlegung
    h = (b - a) / ns
    # Stützstellen
    xp = np.linspace(a, b, ns + 1)
    # Interpolationsparabel
    def p(x, index, h, xp):
        return (1 / (h ** 2)) * (
            0.5 * f(xp[index]) * (x - xp[index + 1]) * (x - xp[index + 2])
            - f(xp[index + 1]) * (x - xp[index]) * (x - xp[index + 2])
            + 0.5 * f(xp[index + 2]) * (x - xp[index]) * (x - xp[index + 1])
        )
    # Plot Parabeln in Zweierintervallen
    for i in range(0, ns, 2):
        xp1 = np.linspace(xp[i], xp[i + 2], 2000)
        yint = p(xp1, i, h, xp)
        if i == 0:
            ax.plot(xp1, yint, color="blue", label="Interpolationsparabeln")
            ax.fill_between(
                xp1, 0, yint,
                color="green",
                alpha=0.25,
                edgecolor="black",
                linewidth=2,
                zorder=3,
                label="Fläche unter Parabeln"
            )
        else:
            ax.plot(xp1, yint, color="blue")
            ax.fill_between(
                xp1, 0, yint,
                color="green",
                alpha=0.25,
                edgecolor="black",
                linewidth=2,
                zorder=3
            )
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()


from core.functions import randomsmonte

def plot_monte(ax, a, b, N, h, hs, w="h"):
    """
    Visualisiert die Monte Carlo Zufallspunkte und die zugehörige Funktion (h oder hs) in ein gegebenes Axes-Objekt auf dem Intervall [a,b].

    Parameter:
        ax (matplotlib.axes.Axes): Achse, in die geplottet wird
        a (float): Linke Intervallgrenze
        b (float): Rechte Intervallgrenze
        N (int): Anzahl der Zufallspunkte
        h (callable): Funktion h(x)
        hs (callable): Funktion hs(x)
        w (str): Auswahl der Funktion, "h" oder "hs"

    Rückgabe:
        keine
    """
    """
    w = "h"  -> Monte Carlo für h
    w = "hs" -> Monte Carlo für hs
    """
    # Feiner Plot der Kurve
    xp = np.linspace(a, b, 10000)

    # Zufallspunkte erzeugen
    xz, yz1, yz2, y1max, y2max = randomsmonte(a, b, N, h, hs)
    # Welche Funktion soll geplottet werden?
    if w == "h":
        ax.plot(xp, h(xp), color="red", label="$B(x)$")
        ax.plot(
            xz, yz1,
            'o',
            color="blue",
            markersize=3,
            label=f"Zufallspunkte (N={N})"
        )
    elif w == "hs":
        ax.plot(xp, hs(xp), color="red", label="$B(x)$")
        ax.plot(
            xz, yz2,
            'o',
            color="blue",
            markersize=3,
            label=f"Zufallspunkte (N={N})"
        )
    else:
        raise ValueError("w muss 'h' oder 'hs' sein")
    # Bearbeiten Koordinatensystem
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()
