# kleine Anzeigehilfen
def _fmt_dt(dt):  # Anzeigen der Zeit
    """
    Formatiert eine Laufzeit in Sekunden zur Anzeige in Millisekunden.

    Parameter:
        dt (float): Laufzeit in Sekunden

    Rückgabe:
        str: Formatierte Laufzeit in Millisekunden mit drei Nachkommastellen
    """
    return f"{1000*dt:.3f}"


def _fmt_num(x):  # Anzeigen des Ergebnis
    """
    Formatiert einen numerischen Ergebniswert kompakt für die Anzeige.

    Parameter:
        x (float): Ergebniswert

    Rückgabe:
        str: Formatierter Zahlenwert mit bis zu 9 signifikanten Stellen
    """
    return f"{x:.9g}"


def _fmt_abs(x):  # Anzeigen des Abs.Fehlers
    """
    Formatiert einen absoluten Fehlerwert in wissenschaftlicher Notation.

    Parameter:
        x (float): Absoluter Fehler

    Rückgabe:
        str: Absoluter Fehler in Exponentialdarstellung mit 9 signifikanten Stellen
    """
    return f"{x:.9e}"


def _fmt_pct(x):  # Anzeigen Prozentualer Fehler
    """
    Formatiert einen prozentualen Fehlerwert für die Anzeige.

    Parameter:
        x (float): Prozentualer Fehler

    Rückgabe:
        str: Prozentualer Fehler mit sechs Nachkommastellen
    """
    return f"{x:.6f}"
