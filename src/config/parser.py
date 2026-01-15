"""
Ziel:
- User wählt eine .txt Datei aus
- Datei enthält Zeilen wie: a=0, err=2*10**-5, x1=1,2,3, f=sin(x)
- Wir lesen alles ein und geben ein Dictionary zurück, in dem
- Zahlen als int/float vorliegen
- err auch als Ausdruck funktioniert (2*10**-5)
- x1,y1,x2,y2,... als Listen von floats gespeichert werden
- f und g als echte Python-Funktionen f(x) gespeichert werden
"""

from __future__ import annotations
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import math
import ast
import numpy as np


# ============================================================
# 1) Datei auswählen (Tkinter)
# ============================================================

def datei_auswaehlen() -> str | None:
    """
    Öffnet einen Dateidialog, damit der User eine .txt Datei auswählen kann.

    Parameter:
        keine

    Rückgabe:
        str | None: Pfad zur ausgewählten Datei, oder None falls keine Datei gewählt wurde
    """
    # Wir öffnen nur den Dateidialog, kein extra Fenster anzeigen
    root = tk.Tk()
    root.withdraw()
    root.update()

    pfad = filedialog.askopenfilename(
        title="Textdatei wählen",
        filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )

    root.destroy()
    return pfad or None


# ============================================================
# 2) Hilfsfunktionen für Listen und Zahlen
# ============================================================

def _parse_float_list(value: str) -> list[float]:
    """
       Wandelt eine Komma getrennte Zahlenfolge aus einem String in eine Liste von floats um.

       Parameter:
           value (str): String mit Komma getrennten Zahlen, z.B. "1,2,3,4.5"

       Rückgabe:
           list[float]: Liste der Zahlen als floats
       """
    # Beispiel: "1,2,3,4.5" -> [1.0, 2.0, 3.0, 4.5]
    teile = [v.strip() for v in value.split(",")]
    # leere Teile rauswerfen (falls jemand "1,2,,3" schreibt)
    teile = [t for t in teile if t != ""]
    return [float(t) for t in teile]


def _safe_eval_number(expr: str) -> float:
    """
        Wertet einen rein numerischen Ausdruck sicher aus und gibt den Wert als float zurück.

        Parameter:
            expr (str): Numerischer Ausdruck als String, z.B. "2*10**-5"

        Rückgabe:
            float: Ausgewerteter Zahlenwert
        """
    # Wir erlauben NUR Zahlen + Operatoren (+ - * / ** Klammern)
    # Keine Namen, keine Funktionen, kein "math", nichts.
    tree = ast.parse(expr, mode="eval")

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,   # Zahl
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.UAdd, ast.USub,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Unerlaubter Ausdruck bei Zahl: {expr!r}")

        # Sicherheit: keine Namen wie "pi", "x" etc.
        if isinstance(node, ast.Name):
            raise ValueError(f"Namen sind in Zahl-Ausdrücken nicht erlaubt: {expr!r}")

        # Sicherheit: keine Funktionsaufrufe
        if isinstance(node, ast.Call):
            raise ValueError(f"Funktionsaufrufe sind in Zahl-Ausdrücken nicht erlaubt: {expr!r}")

    # eval mit komplett abgeschalteten builtins
    return float(eval(compile(tree, "<number>", "eval"), {"__builtins__": {}}, {}))


# ============================================================
# 3) Funktion aus String bauen, z.B. "sin(x)" oder "x**2"
#    Jetzt vektorisierbar: x darf float ODER np.ndarray sein
# ============================================================

# WICHTIG
# - für Plotten brauchst du numpy-Funktionen, nicht math-Funktionen
# - np.sin, np.exp etc. funktionieren mit Arrays

_ALLOWED_FUNCS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,      # np.abs ist arrayfähig
}

# Konstanten dürfen ebenfalls benutzt werden, z.B. sin(pi*x)
_ALLOWED_CONSTS = {"pi": np.pi, "e": np.e}

# Erlaubte AST-Knoten, die wir in Funktionsausdrücken zulassen
_ALLOWED_FUNC_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.UAdd, ast.USub,
)

def _compile_safe_function(expr: str):
    """
    Erstellt aus einem Funktionsausdruck als String eine sichere, auswertbare Funktion f(x).

    Parameter:
        expr (str): Funktionsausdruck, z.B. "sin(x)" oder "x**2"

    Rückgabe:
        callable: Funktion f(x), die für x (float oder np.ndarray) den Ausdruck auswertet
    """
    # Baut aus expr eine Funktion f(x).
    # x darf float oder numpy array sein.
    tree = ast.parse(expr, mode="eval")

    for node in ast.walk(tree):
        # 1) Nur erlaubte Syntax-Elemente
        if not isinstance(node, _ALLOWED_FUNC_NODES):
            raise ValueError(f"Unerlaubtes Syntaxelement {type(node).__name__} in {expr!r}")

        # 2) Keine Attribute wie np.sin oder math.sin erlauben
        # Der User schreibt einfach sin(x), nicht np.sin(x)
        if isinstance(node, ast.Attribute):
            raise ValueError("Bitte schreibe sin(x) statt np.sin(x). Attribute sind nicht erlaubt.")

        # 3) Namen prüfen: erlaubt sind x, pi, e, und Funktionsnamen
        if isinstance(node, ast.Name):
            if node.id == "x":
                continue
            if node.id in _ALLOWED_CONSTS:
                continue
            if node.id in _ALLOWED_FUNCS:
                continue
            raise ValueError(f"Unerlaubter Name {node.id!r} in {expr!r}")

        # 4) Funktionsaufrufe prüfen: nur erlaubte Funktionen
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError(f"Nur direkte Funktionsaufrufe erlaubt, z.B. sin(x). Problem in {expr!r}")
            if node.func.id not in _ALLOWED_FUNCS:
                raise ValueError(f"Unerlaubte Funktion {node.func.id!r} in {expr!r}")

    code = compile(tree, "<function>", "eval")

    def f(x):
        # locals: x und Konstanten
        local_env = {"x": x, **_ALLOWED_CONSTS}
        # globals: nur die erlaubten Funktionen, keine builtins
        global_env = {"__builtins__": {}, **_ALLOWED_FUNCS}

        # WICHTIG: kein float(...) hier, sonst gehen arrays kaputt
        return eval(code, global_env, local_env)

    return f



# ============================================================
# 4) Hauptparser: liest die Datei und baut das Werte-Dict
# ============================================================

def lade_variablen(dateiname: str) -> dict:
    """
        Liest eine Textdatei mit key=value Zeilen ein und gibt ein Dictionary mit geparsten Werten zurück.

        Parameter:
            dateiname (str): Pfad zur Textdatei, die eingelesen werden soll

        Rückgabe:
            dict: Dictionary mit Variablenwerten (Zahlen, Listen, Funktionen) plus "splines" als Struktur
        """
    # Datei lesen
    zeilen = Path(dateiname).read_text(encoding="utf-8").splitlines()

    werte: dict = {}

    for line_no, zeile in enumerate(zeilen, start=1):
        s = zeile.strip()

        # a) leere Zeilen oder Kommentarzeilen überspringen
        if not s or s.startswith("#"):
            continue

        # b) optional: inline Kommentar abschneiden
        # Beispiel: a=0  # startwert
        if "#" in s:
            s = s.split("#", 1)[0].strip()
            if not s:
                continue

        # c) nur key=value Zeilen akzeptieren
        if "=" not in s:
            continue

        key, value = s.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Zeile {line_no}: leerer Schlüssel")
        if not value:
            raise ValueError(f"Zeile {line_no}: leerer Wert bei {key!r}")

        # --------------------------------------------
        # Spezialfälle 1: Splines x1,y1,x2,y2,...
        # --------------------------------------------
        # Wenn key so aussieht: x1, x2, x3 oder y1, y2, ...
        # dann ist es eine Liste
        if (key.startswith("x") or key.startswith("y")) and key[1:].isdigit():
            werte[key] = _parse_float_list(value)
            continue

        # --------------------------------------------
        # Spezialfälle 2: Funktionen f und g
        # --------------------------------------------
        if key in {"f", "g"}:
            werte[key + "_expr"] = value  # Originaltext speichern, z.B. "sin(x)"
            werte[key] = _compile_safe_function(value)  # Funktion bauen
            continue

        # --------------------------------------------
        # Standard: int / float / Ausdruck wie 2*10**-5
        # --------------------------------------------
        # int: "10"
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            werte[key] = int(value)
            continue

        # float direkt: "0.5" oder "-3.2"
        try:
            werte[key] = float(value)
            continue
        except ValueError:
            pass

        # numerischer Ausdruck: "2*10**-5"
        # Achtung: wenn das auch nicht klappt, speichern wir es als String
        try:
            werte[key] = _safe_eval_number(value)
            continue
        except Exception:
            werte[key] = value

    # ============================================================
    # 5) Optional: Splines als Struktur zusammenbauen
    # ============================================================
    # Statt nur x1,y1,x2,y2... im dict zu haben, bauen wir zusätzlich:
    # werte["splines"] = [ (x_list, y_list), (x_list2, y_list2), ... ]
    werte["splines"] = _baue_spline_liste(werte)

    return werte


def _baue_spline_liste(werte: dict) -> list[tuple[list[float], list[float]]]:
    """
        Erstellt aus den Einträgen x1/y1, x2/y2, ... eine Liste von Spline-Stützpunkten.

        Parameter:
            werte (dict): Dictionary, das xk/yk Paare als Listen enthalten kann (z.B. "x1", "y1")

        Rückgabe:
            list[tuple[list[float], list[float]]]: Liste von Tupeln (x_liste, y_liste) für alle gefundenen Indizes
        """
    # Sucht passende Paare (x1,y1), (x2,y2), ...
    splines: list[tuple[list[float], list[float]]] = []

    # Alle x-Keys finden
    x_keys = [k for k in werte.keys() if k.startswith("x") and k[1:].isdigit()]
    x_keys.sort(key=lambda k: int(k[1:]))

    for xk in x_keys:
        idx = xk[1:]      # z.B. "1"
        yk = "y" + idx    # z.B. "y1"
        if yk not in werte:
            raise ValueError(f"Für {xk} fehlt {yk}")

        xs = werte[xk]
        ys = werte[yk]

        if len(xs) != len(ys):
            raise ValueError(f"Spline {idx}: x und y haben unterschiedliche Länge ({len(xs)} vs {len(ys)})")

        splines.append((xs, ys))

    # Falls jemand y2 hat aber x2 nicht -> Fehler
    y_keys = [k for k in werte.keys() if k.startswith("y") and k[1:].isdigit()]
    for yk in y_keys:
        idx = yk[1:]
        xk = "x" + idx
        if xk not in werte:
            raise ValueError(f"Für {yk} fehlt {xk}")

    return splines


# ============================================================
# 6) Demo: nur zum Testen
# ============================================================

if __name__ == "__main__":
    pfad = datei_auswaehlen()
    if not pfad:
        print("Keine Datei gewählt")
        raise SystemExit
    cfg = lade_variablen(pfad)
