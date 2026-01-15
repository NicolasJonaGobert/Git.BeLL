# ui/controller.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# bei dir: from config.parser import lade_variablen
# ich importiere hier nur symbolisch:
try:
    from config.parser import lade_variablen
except Exception:
    lade_variablen = None  # damit das GUI-Grundgerüst trotzdem läuft


@dataclass
class AppState:
    filepath: str | None = None
    cfg: dict | None = None


class Controller:
    def __init__(self, root: tk.Tk, widgets, state: AppState):
        """
        Initialisiert den Controller, speichert Referenzen auf Root, Widgets und AppState,
        verbindet Button-Callbacks und schreibt eine Startmeldung ins Log.

        Parameter:
            root (tk.Tk): Hauptfenster der Tkinter-Anwendung
            widgets: Widget-Container (z.B. AppWidgets), enthält Buttons, Tabellen, Log und Plot-Objekte
            state (AppState): Zustand der Anwendung (Dateipfad und geladene Config)

        Rückgabe:
            keine
        """
        self.root = root
        self.w = widgets
        self.s = state

        # Buttons verbinden
        self.w.btn_choose.configure(command=self.on_choose_file)
        self.w.btn_eval.configure(command=self.on_evaluate)
        self.w.btn_reset.configure(command=self.on_reset)

        self.log("Bereit. Wähle eine Eingabedatei.")

    def log(self, msg: str) -> None:
        """
        Schreibt eine Nachricht in das Log-Textfeld und scrollt automatisch ans Ende.

        Parameter:
            msg (str): Log-Nachricht, die ausgegeben werden soll

        Rückgabe:
            keine
        """
        self.w.txt_log.insert("end", msg + "\n")
        self.w.txt_log.see("end")

    def on_choose_file(self) -> None:
        """
        Öffnet einen Dateidialog, speichert den ausgewählten Pfad im AppState,
        lädt die Konfiguration über lade_variablen und füllt anschließend die Input-Tabelle.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        path = filedialog.askopenfilename(
            title="Textdatei wählen",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return

        self.s.filepath = path
        self.log(f"Datei gewählt: {Path(path).name}")

        if lade_variablen is None:
            self.log("Parser nicht importierbar. Prüfe Pfade/Imports.")
            return

        try:
            cfg = lade_variablen(path)
            self.s.cfg = cfg
            self._fill_input_table(cfg)
            self.log("Config geladen.")
        except Exception as e:
            self.s.cfg = None
            self.log(f"Fehler beim Laden: {e}")
            messagebox.showerror("Fehler", f"Config konnte nicht geladen werden.\n\n{e}")

    def _fill_input_table(self, cfg: dict) -> None:
        """
        Leert die Input-Treeview und füllt sie mit den Key-Value-Paaren aus cfg.
        Große Listen und Funktionsobjekte werden dabei kurz/kompakt dargestellt.

        Parameter:
            cfg (dict): Geladene Konfigurationsdaten, die angezeigt werden sollen

        Rückgabe:
            keine
        """
        # Tree leeren
        for item in self.w.tree_input.get_children():
            self.w.tree_input.delete(item)

        # Einträge sortiert anzeigen (Strings kurz halten)
        for k in sorted(cfg.keys(), key=str):
            v = cfg[k]
            t = type(v).__name__

            # Funktionsobjekte / große Listen kurz darstellen
            if callable(v):
                v_str = "<funktion>"
            elif isinstance(v, (list, tuple)) and len(v) > 8:
                v_str = f"[{', '.join(map(str, v[:8]))}, ...]"
            else:
                v_str = str(v)

            self.w.tree_input.insert("", "end", values=(k, v_str, t))

    def on_evaluate(self) -> None:
        """
        Startet die Auswertung, sofern eine Config geladen ist.
        Aktuell werden Dummy-Ergebnisse und Dummy-Plots erzeugt, um das UI-Update zu demonstrieren.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        if not self.s.cfg:
            self.log("Keine Config geladen.")
            return

        self.log("Starte Auswertung...")

        # Hier kommt später dein echter Run-Dispatcher rein:
        # - h, hs bauen
        # - Methoden aus core/ ausführen
        # - timer/counter/error benutzen
        #
        # Ich trage nur Dummy-Werte ein, damit du UI-Update siehst.

        self._fill_eval_dummy()
        self._draw_dummy_plots()

        self.log("Auswertung abgeschlossen.")

    def _fill_eval_dummy(self) -> None:
        """
        Leert die Auswertungs-Tabellen (Funktionen/Splines) und füllt sie mit Dummy-Zeilen.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        # Tabellen leeren
        for item in self.w.tree_eval_func.get_children():
            self.w.tree_eval_func.delete(item)
        for item in self.w.tree_eval_spline.get_children():
            self.w.tree_eval_spline.delete(item)

        # Dummy-Zeilen
        self.w.tree_eval_func.insert("", "end", values=("Trapez", "1.234", "0.012", "0.003 s", "1001"))
        self.w.tree_eval_func.insert("", "end", values=("Simpson", "1.235", "0.004", "0.004 s", "1001"))
        self.w.tree_eval_func.insert("", "end", values=("Monte", "1.220", "0.050", "0.020 s", "N"))

        self.w.tree_eval_spline.insert("", "end", values=("Trapez", "0.900", "0.010", "0.002 s", "1001"))
        self.w.tree_eval_spline.insert("", "end", values=("Simpson", "0.910", "0.005", "0.003 s", "1001"))

    def _draw_dummy_plots(self) -> None:
        """
        Setzt alle Plot-Axes zurück und zeichnet anschließend einige Beispielkurven in die ersten Plots.
        Danach wird das Canvas aktualisiert.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        import numpy as np

        for ax in self.w.axes:
            ax.clear()
            ax.grid(True)
            ax.set_xlabel("x")
            ax.set_ylabel("y")

        x = np.linspace(0, 1, 200)
        self.w.axes[0].set_title("Plot 1")
        self.w.axes[0].plot(x, x**2)

        self.w.axes[1].set_title("Plot 2")
        self.w.axes[1].plot(x, np.sin(2*np.pi*x))

        self.w.axes[2].set_title("Plot 3")
        self.w.axes[2].plot(x, np.abs(np.sin(2*np.pi*x) - x**2))

        self.w.axes[3].set_title("Plot 4")
        self.w.axes[3].plot(x, x)

        self.w.canvas.draw()

    def on_reset(self) -> None:
        """
        Setzt den AppState zurück, leert Tabellen und Log, und setzt alle Plots auf den Ausgangszustand zurück.

        Parameter:
            keine

        Rückgabe:
            keine
        """
        self.s.filepath = None
        self.s.cfg = None

        # Tabellen leeren
        for tr in (self.w.tree_input, self.w.tree_eval_func, self.w.tree_eval_spline):
            for item in tr.get_children():
                tr.delete(item)

        # Log leeren und neu starten
        self.w.txt_log.delete("1.0", "end")
        self.log("Reset. Wähle eine Eingabedatei.")

        # Plots leeren
        for i, ax in enumerate(self.w.axes, start=1):
            ax.clear()
            ax.set_title(f"Plot {i}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)
        self.w.canvas.draw()
