from __future__ import annotations  # erlaubt moderne Typ-Hinweise ohne Laufzeitprobleme
import tkinter as tk
from tkinter import ttk
from ui.views import build_ui              # baut die komplette Benutzeroberfläche
from ui.controller import Controller, AppState  # steuert Logik und Zustand der App

def run_app():
    """
    Startet die Tkinter-Anwendung, baut die Benutzeroberfläche auf und initialisiert den Controller.

    Parameter:
        keine

    Rückgabe:
        keine
    """
    # Hauptfenster der Tkinter-Anwendung erzeugen
    root = tk.Tk()

    # -------- Grundstyle (TTK) --------
    style = ttk.Style(root)

    # Versucht nacheinander bevorzugte Themes zu setzen
    # bricht ab, sobald ein verfügbares Theme gefunden wurde
    for preferred in ("clam", "vista", "default"):
        try:
            style.theme_use(preferred)
            break
        except Exception:
            pass  # falls Theme nicht existiert, einfach weitermachen

    # -------- UI aufbauen --------
    # build_ui erstellt alle Widgets und gibt sie gebündelt zurück
    widgets = build_ui(root)

    # -------- Controller starten --------
    # AppState hält den aktuellen Zustand der Anwendung
    state = AppState()

    # Controller verbindet UI (widgets), Zustand (state) und Fenster (root)
    Controller(root, widgets, state)

    # Mindestgröße des Fensters festlegen
    root.minsize(1100, 650)

    # Start der Event-Schleife (ab hier reagiert die App auf Benutzereingaben)
    root.mainloop()
