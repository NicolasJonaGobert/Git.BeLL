# parser.py
"""
Parser für eine einfache Konfig-Textdatei im Format key=value mit Kommentaren (# ...)

Ziele
- liest Werte wie a=0, err=2*10**-5
- liest Listen wie x1=1,2,3 -> als Python-Listen von floats
- liest Funktionsausdrücke wie f=sin(x) und baut daraus eine weiterverwertbare Funktion f(x)
- validiert ein paar Basics (fehlende Keys, ns gerade, Listenlängen passend)

WICHTIG zur Sicherheit
- Funktionsstrings werden NICHT mit eval() ausgeführt
- stattdessen wird per ast geparst und nur eine kleine, sichere Teilmenge zugelassen
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Any
import ast
import math


# ----------------------------
# Datenstruktur für die Config
# ----------------------------

@dataclass(frozen=True)
class Config:
    # Intervall
    a: float
    b: float

    # Quadratur
    nt: int
    ns: int

    # Monte Carlo
    N: int

    # Fehlergrenze
    err: float

    # Splines: Liste von (x_liste, y_liste) Tupeln
    # Beispiel: [(x1_list, y1_list), (x2_list, y2_list)]
    splines: List[Tuple[List[float], List[float]]]

    # Funktionen
    f: Callable[[float], float]
    g: Callable[[float], float]


# -----------------------------------------------------
# 1) Allgemeines Einlesen key=value und Grund-Parsing
# -----------------------------------------------------

def load_config_from_txt(path: str) -> Config:
    """
    Liest die Datei und gibt ein Config-Objekt zurück.

    Erwartete Keys (entsprechend deiner Beispiel-Datei)
    - a, b
    - nt, ns
    - N
    - err
    - x1, y1, x2, y2, ... beliebig viele Spline-Paare
    - f, g
    """
    raw: Dict[str, str] = _read_key_value_file(path)

    # Pflichtfelder
    required = ["a", "b", "nt", "ns", "N", "err", "f", "g"]
    missing = [k for k in required if k not in raw]
    if missing:
        raise ValueError(f"Fehlende Schlüssel in Config: {missing}")

    # Zahlenfelder parsen
    a = _parse_number(raw["a"])
    b = _parse_number(raw["b"])

    nt = _parse_int(raw["nt"])
    ns = _parse_int(raw["ns"])
    N = _parse_int(raw["N"])

    err = _parse_number(raw["err"])

    # Plausibilitätschecks
    if b <= a:
        raise ValueError(f"Ungültiges Intervall: a={a} muss kleiner als b={b} sein")
    if nt <= 0:
        raise ValueError("nt muss > 0 sein")
    if ns <= 0 or (ns % 2 != 0):
        raise ValueError("ns muss > 0 und gerade sein (Simpsonregel)")
    if N <= 0:
        raise ValueError("N muss > 0 sein")
    if err <= 0:
        raise ValueError("err muss > 0 sein")

    # Splines sammeln: wir suchen alle Keys xk / yk mit gleicher Nummer k
    splines = _collect_splines(raw)

    # Funktionen f,g bauen
    f = _build_safe_function(raw["f"])
    g = _build_safe_function(raw["g"])

    return Config(
        a=a, b=b,
        nt=nt, ns=ns,
        N=N,
        err=err,
        splines=splines,
        f=f, g=g
    )


def _read_key_value_file(path: str) -> Dict[str, str]:
    """
    Liest eine Datei ein, ignoriert:
    - leere Zeilen
    - Kommentarzeilen, die mit # beginnen
    Akzeptiert:
    - key=value (links key, rechts value als string, whitespace wird entfernt)

    Rückgabe: dict key -> value_string
    """
    data: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()

            # leer oder Kommentar
            if not line or line.startswith("#"):
                continue

            # inline-Kommentare optional unterstützen:
            # "a=1  # kommentar" -> wir schneiden ab dem ersten # ab
            if "#" in line:
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue

            if "=" not in line:
                raise ValueError(f"Zeile {line_no}: Erwartet key=value, bekam: {line!r}")

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(f"Zeile {line_no}: Leerer Schlüssel")
            if not value:
                raise ValueError(f"Zeile {line_no}: Leerer Wert für Schlüssel {key!r}")

            # Doppelte keys sind meistens ein Fehler
            if key in data:
                raise ValueError(f"Zeile {line_no}: Schlüssel {key!r} mehrfach definiert")

            data[key] = value

    return data


# ----------------------------
# 2) Zahl-Parsing
# ----------------------------

def _parse_int(s: str) -> int:
    """
    Parst int (z.B. "10"). Für Sicherheit erlauben wir keine Ausdrücke wie "5+5" hier.
    """
    try:
        return int(s)
    except ValueError:
        raise ValueError(f"Erwartete ganze Zahl, bekam: {s!r}")


def _parse_number(s: str) -> float:
    """
    Parst float ODER einen einfachen Ausdruck wie 2*10**-5.

    Wir erlauben hier absichtlich eine sichere Ausdrucksauswertung (ast),
    aber ohne Variablen, nur Zahlen + Operatoren.
    """
    return float(_safe_eval_numeric_expr(s))


def _safe_eval_numeric_expr(expr: str) -> float:
    """
    Sichere Auswertung von numerischen Ausdrücken.
    Erlaubt: Zahlen, +, -, *, /, **, Klammern.
    Verbietet: Namen, Funktionsaufrufe, Attribute, etc.
    """
    tree = ast.parse(expr, mode="eval")

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.UAdd, ast.USub,
        ast.Load,
        # Für Python-Versionen, wo Zahlen als ast.Num vorkommen:
        ast.Num,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Nicht erlaubter Ausdruck in Zahl: {expr!r}")

        # Keine Namen (wie "pi") erlauben, nur pure Zahlen
        if isinstance(node, ast.Name):
            raise ValueError(f"Namen sind in err/a/b etc. nicht erlaubt: {expr!r}")

        # Keine Funktionsaufrufe
        if isinstance(node, ast.Call):
            raise ValueError(f"Funktionsaufrufe sind in Zahlen nicht erlaubt: {expr!r}")

    return eval(compile(tree, filename="<numeric_expr>", mode="eval"), {"__builtins__": {}}, {})


# ----------------------------
# 3) Listen-Parsing für Splines
# ----------------------------

def _parse_float_list(s: str) -> List[float]:
    """
    Parst "1,2,3,4.5" -> [1.0, 2.0, 3.0, 4.5]
    """
    parts = [p.strip() for p in s.split(",")]
    if any(p == "" for p in parts):
        raise ValueError(f"Ungültige Liste: {s!r}")
    try:
        return [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Liste enthält nicht-numerische Werte: {s!r}")


def _collect_splines(raw: Dict[str, str]) -> List[Tuple[List[float], List[float]]]:
    """
    Sammelt Spline-Paare x1/y1, x2/y2, ... aus dem raw dict.

    Regeln:
    - Wenn xk vorhanden ist, muss yk vorhanden sein (und umgekehrt)
    - Längen von xk und yk müssen übereinstimmen
    - k beginnt bei 1 (wie in deinem Beispiel), kann aber auch mehr sein
    """
    # Alle Keys, die wie "x<number>" aussehen, finden
    x_keys = []
    for k in raw.keys():
        if k.startswith("x") and k[1:].isdigit():
            x_keys.append(k)

    # Nach der Nummer sortieren: x1, x2, x10, ...
    def num_of(key: str) -> int:
        return int(key[1:])

    x_keys.sort(key=num_of)

    splines: List[Tuple[List[float], List[float]]] = []

    for xk in x_keys:
        k = xk[1:]      # z.B. "1"
        yk = "y" + k    # z.B. "y1"

        if yk not in raw:
            raise ValueError(f"Für {xk!r} fehlt das passende {yk!r}")

        xs = _parse_float_list(raw[xk])
        ys = _parse_float_list(raw[yk])

        if len(xs) != len(ys):
            raise ValueError(f"Spline {k}: x und y haben unterschiedliche Länge ({len(xs)} vs {len(ys)})")

        splines.append((xs, ys))

    # Optional: Wenn yk existiert aber xk nicht, Fehler
    for k in raw.keys():
        if k.startswith("y") and k[1:].isdigit():
            xk = "x" + k[1:]
            if xk not in raw:
                raise ValueError(f"Für {k!r} fehlt das passende {xk!r}")

    return splines


# ----------------------------
# 4) Sichere Funktions-Erzeugung aus "sin(x)" etc.
# ----------------------------

# erlaubte mathematische Funktionen (du kannst hier erweitern)
_ALLOWED_MATH_FUNCS: Dict[str, Any] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "log": math.log,
    "sqrt": math.sqrt,
    "abs": abs,          # abs ist builtin, aber okay
}

# erlaubte Konstanten
_ALLOWED_CONSTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}

_ALLOWED_NAMES = {"x"} | set(_ALLOWED_MATH_FUNCS.keys()) | set(_ALLOWED_CONSTS.keys())


def _build_safe_function(expr: str) -> Callable[[float], float]:
    """
    Baut aus einem Ausdruck wie "sin(x)" eine Python-Funktion f(x).

    - erlaubt nur eine kleine AST-Teilmenge
    - erlaubt nur den Namen x, sowie die erlaubten math-Funktionen und Konstanten
    - verbietet Attribute (math.sin), Imports, Listen, dicts, etc.
    """
    tree = ast.parse(expr, mode="eval")

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.UAdd, ast.USub,
        ast.Mod,
        ast.Num,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Nicht erlaubter Ausdruck in Funktion: {expr!r}")

        # keine Attribute wie "math.sin"
        if isinstance(node, ast.Attribute):
            raise ValueError(f"Attribute sind nicht erlaubt (nutze sin(x), nicht math.sin(x)): {expr!r}")

        # Namen prüfen
        if isinstance(node, ast.Name):
            if node.id not in _ALLOWED_NAMES:
                raise ValueError(f"Nicht erlaubter Name {node.id!r} in Funktion: {expr!r}")

        # Funktionsaufruf prüfen: Nur erlaubte Funktionsnamen
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError(f"Nur direkte Funktionsnamen erlaubt, z.B. sin(x): {expr!r}")
            if node.func.id not in _ALLOWED_MATH_FUNCS:
                raise ValueError(f"Nicht erlaubte Funktion {node.func.id!r} in: {expr!r}")

    code = compile(tree, filename="<function_expr>", mode="eval")

    def f(x: float) -> float:
        # locals: x und erlaubte Konstanten
        local_env = {"x": x, **_ALLOWED_CONSTS}
        # globals: nur erlaubte Funktionen, keine builtins
        global_env = {"__builtins__": {}, **_ALLOWED_MATH_FUNCS}
        return float(eval(code, global_env, local_env))

    return f


# ----------------------------
#
