# ------------------------------------------------------------
# Validierungsfunktionen für Eingabeparameter
# ------------------------------------------------------------

# Überprüft, ob das Integrationsintervall korrekt definiert ist
# Es muss strikt a < b gelten, sonst ist kein sinnvolles Integral definiert
def check_interval(a, b):
    if b <= a:
        raise ValueError("Intervallfehler, es muss a < b gelten")


# Überprüft, ob ein Parameter strikt positiv ist
# Wird für Teilungszahlen n, Schrittweiten k oder Fehlertoleranzen err verwendet
def check_positive(n, name="n"):
    if n <= 0:
        raise ValueError(f"{name} muss > 0 sein")


# Überprüft, ob eine Zahl gerade ist
# Wird z. B. für ns benötigt, da die Simpsonregel eine gerade Teilungszahl verlangt
def check_even(n, name="n"):
    if n % 2 != 0:
        raise ValueError(f"{name} muss gerade sein")


# ------------------------------------------------------------
# Numerische Hilfsfunktionen
# ------------------------------------------------------------

import numpy as np  # Modul zur Arbeit mit Arrays und numerischen Operationen


# Funktion zum Abfangen problematischer Nullstellen
#
# Motivation:
# Einige Funktionen sind bei x = 0 nicht direkt definiert
# (z. B. sin(x)/x, x*ln(x), ln(x)/x), besitzen aber einen Grenzwert.
# Wird x = 0 numerisch direkt eingesetzt, entstehen Division durch 0,
# NaNs oder Exceptions.
#
# Lösung:
# Exakte Nullen werden durch ein sehr kleines eps (z. B. 1e-12) ersetzt.
def replace_zeros(x, eps=1e-12):
    """
    Ersetzt exakte Nullstellen durch ein kleines eps.

    Verhalten:
    - Skalar-Eingabe:
        0.0 -> eps
        sonst -> unverändert
    - Array-Eingabe:
        Alle Einträge, die exakt 0.0 sind, werden durch eps ersetzt
        (Vorzeicheninformation ist bei exakt 0 nicht vorhanden, daher +eps)
    """

    # x wird in ein numpy-Array umgewandelt
    # Vorteil: einheitliche Behandlung von Skalaren und Arrays
    x_arr = np.asarray(x, dtype=float)

    # Skalarfall: x ist ein einzelner Wert
    if x_arr.ndim == 0:
        if x_arr == 0.0:
            return float(eps)
        return float(x_arr)

    # Arrayfall: mehrere Auswertungsstellen
    out = x_arr.copy()  # Kopie, damit das Original unverändert bleibt

    # Maske für exakt auftretende Nullen
    mask0 = (out == 0.0)

    # Falls mindestens eine Null vorhanden ist, ersetze sie
    if np.any(mask0):
        # Vorzeichenbestimmung (bei 0 immer 0)
        s = np.sign(out[mask0])

        # Fallback: sign(0) = 0 -> ersetze durch +1
        # Ergebnis: 0.0 wird zu +eps
        s[s == 0] = 1.0

        # Ersetze Nullstellen durch eps
        out[mask0] = s * eps

    # Rückgabe des Arrays ohne exakte Nullen
    return out


# ------------------------------------------------------------
# Robuste Funktionsauswertung
# ------------------------------------------------------------

# Wertet eine Funktion f(x) numerisch stabil aus und stellt sicher,
# dass stets ein 1D-Array gleicher Länge wie x zurückgegeben wird
def _eval_y(f, x, eps=1e-12):
    # Zunächst exakte Nullen durch eps ersetzen
    x_safe = replace_zeros(x, eps)

    # Sicherstellen, dass x als numpy-Array vorliegt
    x_arr = np.asarray(x_safe, dtype=float)

    # Funktionsauswertung
    y = f(x_arr)

    # Fall 1: f liefert einen Python-Skalar (z. B. konstante Funktion)
    # -> auf die Länge von x aufweiten
    if np.isscalar(y):
        return np.full_like(x_arr, float(y), dtype=float)

    # In numpy-Array umwandeln
    y = np.asarray(y, dtype=float)

    # Fall 2: 0-d-Array (Skalar in Arrayform)
    if y.ndim == 0:
        return np.full_like(x_arr, float(y), dtype=float)

    # Fall 3: Array der Länge 1 bei mehreren x-Werten
    # -> ebenfalls als konstante Funktion interpretieren
    if y.size == 1 and x_arr.size > 1:
        return np.full_like(x_arr, float(y.ravel()[0]), dtype=float)

    # Fall 4: Shape stimmt nicht überein
    # Erlaubt ist nur ein 1D-Array gleicher Länge wie x
    if y.shape != x_arr.shape:
        if y.ndim == 1 and y.size == x_arr.size:
            return y
        raise ValueError("f(x) muss Skalar oder Array gleicher Länge wie x liefern")

    # Normalfall: y passt exakt zu x
    return y


# ------------------------------------------------------------
# Wrapper-Funktion für sichere Funktionsauswertung
# ------------------------------------------------------------

# Erzeugt eine neue Funktion, die vor der Auswertung exakte Nullen ersetzt
def safe_func(f, eps=1e-12):
    """
    Verpackt eine Funktion f(x), sodass x vor der Auswertung
    automatisch durch replace_zeros läuft.

    Nutzen:
    - Kann überall eingesetzt werden, wo f erwartet wird
    - Erhöht numerische Stabilität bei Funktionen mit Grenzwerten in 0
    """
    def _wrapped(x):
        return f(replace_zeros(x, eps))
    return _wrapped
