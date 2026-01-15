from __future__ import annotations  # Typ-Hinweise können als Strings ausgewertet werden (u. a. für Vorwärtsreferenzen)
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


@dataclass
class AppWidgets:
    # Container für alle wichtigen Widgets, damit die Logik später direkt darauf zugreifen kann
    btn_choose: ttk.Button        # Button: Datei auswählen
    btn_eval: ttk.Button          # Button: Auswertung starten
    btn_reset: ttk.Button         # Button: Eingaben/Ansicht zurücksetzen

    tree_input: ttk.Treeview      # Tabelle: geladene Input-Parameter
    tree_eval_func: ttk.Treeview  # Tabelle: Ergebnisse für Funktionen
    tree_eval_spline: ttk.Treeview# Tabelle: Ergebnisse für Splines

    txt_log: tk.Text              # Textfeld: Log/Statusmeldungen

    axes: list                    # Matplotlib-Achsenobjekte (zum Plotten/Updaten)
    canvases: list                # Matplotlib-Canvasobjekte (zum Neuzeichnen)


def build_ui(root: tk.Tk) -> AppWidgets:
    # Grundfenster konfigurieren
    root.title("BeLL – Auswertung")
    root.grid_columnconfigure(0, weight=1)  # Spalte 0 wächst mit dem Fenster
    root.grid_rowconfigure(1, weight=1)     # Zeile 1 (Hauptbereich) wächst mit

    # -------- Topbar --------
    topbar = ttk.Frame(root, padding=(8, 6))        # obere Leiste für Buttons
    topbar.grid(row=0, column=0, sticky="ew")       # "ew" = volle Breite

    btn_choose = ttk.Button(topbar, text="Datei wählen…")  # lädt Input-Datei
    btn_eval = ttk.Button(topbar, text="Auswerten")        # startet Berechnung
    btn_reset = ttk.Button(topbar, text="Reset")           # setzt UI zurück

    btn_choose.grid(row=0, column=0, padx=(0, 6))
    btn_eval.grid(row=0, column=1, padx=(0, 6))
    btn_reset.grid(row=0, column=2)
    topbar.grid_columnconfigure(3, weight=1)        # "Füllspalte", hält Buttons links

    # -------- ROOT: oben (Input+Auswertung) / unten (Plots) --------
    root_panes = ttk.Panedwindow(root, orient="vertical")  # teilbares Layout (Sash = Trennbalken)
    root_panes.grid(row=1, column=0, sticky="nsew")

    top_area = ttk.Frame(root_panes)                         # oberer Bereich (Tabellen/Log)
    plot_frame = ttk.Labelframe(root_panes, text="Plots", padding=(6, 6))  # unterer Bereich (Plots)

    # Wichtig: Plots NICHT dominant beim Start
    root_panes.add(top_area, weight=3)       # oben bekommt mehr Platz
    root_panes.add(plot_frame, weight=2)     # unten etwas weniger

    top_area.grid_rowconfigure(0, weight=1)    # Inhalt in top_area soll skalieren
    top_area.grid_columnconfigure(0, weight=1)

    # -------- oben: links/rechts --------
    main_panes = ttk.Panedwindow(top_area, orient="horizontal")  # links Input/Log, rechts Ergebnisse
    main_panes.grid(row=0, column=0, sticky="nsew")

    left = ttk.Frame(main_panes)     # linke Spalte
    right = ttk.Frame(main_panes)    # rechte Spalte
    main_panes.add(left, weight=1)   # links schmaler
    main_panes.add(right, weight=3)  # rechts breiter

    # -------- Links: Input oben, Log unten --------
    left.grid_rowconfigure(0, weight=1)
    left.grid_columnconfigure(0, weight=1)

    left_panes = ttk.Panedwindow(left, orient="vertical")  # Input und Log vertikal teilbar
    left_panes.grid(row=0, column=0, sticky="nsew")

    input_frame = ttk.Labelframe(left_panes, text="Input", padding=(6, 6))  # Input-Parameter
    log_frame = ttk.Labelframe(left_panes, text="Log", padding=(6, 6))      # Status/Fehler

    left_panes.add(input_frame, weight=2)  # Input soll größer sein
    left_panes.add(log_frame, weight=1)

    # Input Treeview
    tree_input = ttk.Treeview(
        input_frame,
        columns=("key", "value", "type"),  # feste Spalten, damit Einfügen/Lesen konsistent ist
        show="headings",
        height=10
    )
    tree_input.heading("key", text="Schlüssel")
    tree_input.heading("value", text="Wert")
    tree_input.heading("type", text="Typ")
    tree_input.column("key", width=140, anchor="w")
    tree_input.column("value", width=220, anchor="w")
    tree_input.column("type", width=80, anchor="w")

    sb_input_y = ttk.Scrollbar(input_frame, orient="vertical", command=tree_input.yview)  # Scrollbar für Input-Tabelle
    tree_input.configure(yscrollcommand=sb_input_y.set)

    tree_input.grid(row=0, column=0, sticky="nsew")  # Tabelle füllt den Frame
    sb_input_y.grid(row=0, column=1, sticky="ns")    # Scrollbar rechts daneben
    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)

    # Log Text
    txt_log = tk.Text(log_frame, height=8, wrap="word")  # Log als Textfeld (mehrzeilig)
    sb_log_y = ttk.Scrollbar(log_frame, orient="vertical", command=txt_log.yview)  # Scrollbar für Log
    txt_log.configure(yscrollcommand=sb_log_y.set)
    txt_log.grid(row=0, column=0, sticky="nsew")
    sb_log_y.grid(row=0, column=1, sticky="ns")
    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    # -------- Rechts: Auswertung --------
    right.grid_rowconfigure(0, weight=1)
    right.grid_columnconfigure(0, weight=1)

    right_panes = ttk.Panedwindow(right, orient="vertical")  # Ergebnisse: oben Funktionen, unten Splines
    right_panes.grid(row=0, column=0, sticky="nsew")

    eval_func = ttk.Labelframe(right_panes, text="Auswertung – Funktionen", padding=(6, 6))
    eval_spline = ttk.Labelframe(right_panes, text="Auswertung – Spline-Funktionen", padding=(6, 6))

    right_panes.add(eval_func, weight=1)
    right_panes.add(eval_spline, weight=1)

    def _make_eval_tree(parent: ttk.Frame) -> ttk.Treeview:
        # Hilfsfunktion, um zwei identische Ergebnis-Tabellen zu erzeugen
        tree = ttk.Treeview(
            parent,
            columns=("method", "n", "result", "abserror", "perror", "time", "calls"),
            show="headings",
            height=8
        )
        # Spaltenüberschriften entsprechen direkt den Auswertungskennzahlen
        tree.heading("method", text="Methode")
        tree.heading("n", text="n")
        tree.heading("result", text="Ergebnis")
        tree.heading("abserror", text="Absoluter Fehler")
        tree.heading("perror", text="Fehler in %")
        tree.heading("time", text="Zeit in ms")
        tree.heading("calls", text="Funktions Aufrufe")

        tree.column("method", width=180, anchor="w")
        tree.column("n", width=70, anchor="center")
        tree.column("result", width=130, anchor="w")
        tree.column("abserror", width=130, anchor="w")
        tree.column("perror", width=110, anchor="w")
        tree.column("time", width=90, anchor="w")
        tree.column("calls", width=120, anchor="w")

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)  # Scrollbar für Ergebnistabelle
        tree.configure(yscrollcommand=sb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        return tree

    tree_eval_func = _make_eval_tree(eval_func)      # Ergebnisse für Funktionen
    tree_eval_spline = _make_eval_tree(eval_spline)  # Ergebnisse für Splines

    # -------- Plots (unten, über volle Breite) --------
    plot_frame.grid_rowconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(0, weight=1)

    plot_canvas = tk.Canvas(plot_frame, highlightthickness=0)  # Canvas als scrollbarer Container
    plot_scroll = ttk.Scrollbar(plot_frame, orient="vertical", command=plot_canvas.yview)
    plot_canvas.configure(yscrollcommand=plot_scroll.set)

    plot_canvas.grid(row=0, column=0, sticky="nsew")
    plot_scroll.grid(row=0, column=1, sticky="ns")

    plot_inner = ttk.Frame(plot_canvas)  # hier drin liegen die einzelnen Plot-Panels
    plot_window = plot_canvas.create_window((0, 0), window=plot_inner, anchor="nw")  # Frame in Canvas "einbauen"

    def _on_plot_inner_configure(_event):
        # Scrollbereich anpassen, sobald sich die Größe des Inhalts ändert
        plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

    plot_inner.bind("<Configure>", _on_plot_inner_configure)

    def _on_plot_canvas_configure(event):
        # Innenframe soll immer die gleiche Breite wie das Canvas haben (kein Horizontal-Scroll nötig)
        plot_canvas.itemconfigure(plot_window, width=event.width)

    plot_canvas.bind("<Configure>", _on_plot_canvas_configure)

    # Scroll nur bei Hover über Plotbereich
    def _on_mousewheel(event):
        # Windows/macOS: MouseWheel liefert delta, daraus wird Scroll-Schritt berechnet
        plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_up(_event):
        # Linux nutzt oft Button-4/5 statt MouseWheel
        plot_canvas.yview_scroll(-3, "units")

    def _on_linux_down(_event):
        plot_canvas.yview_scroll(3, "units")

    def _bind_plot_scroll(_event=None):
        # Bind global, damit Scroll zuverlässig funktioniert solange Maus im Plotbereich ist
        plot_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        plot_canvas.bind_all("<Button-4>", _on_linux_up)
        plot_canvas.bind_all("<Button-5>", _on_linux_down)

    def _unbind_plot_scroll(_event=None):
        # Unbind wieder, damit Scrollrad außerhalb der Plots nicht "geklaut" wird
        plot_canvas.unbind_all("<MouseWheel>")
        plot_canvas.unbind_all("<Button-4>")
        plot_canvas.unbind_all("<Button-5>")

    plot_canvas.bind("<Enter>", _bind_plot_scroll)
    plot_canvas.bind("<Leave>", _unbind_plot_scroll)

    plot_inner.grid_columnconfigure(0, weight=1)  # 2 Spalten Layout für Plots
    plot_inner.grid_columnconfigure(1, weight=1)

    plot_canvases = []  # Liste der FigureCanvasTkAgg-Objekte
    plot_axes = []  # Liste der Achsen (ax), damit die Logik darauf zeichnen kann

    for idx in range(14):
        r = idx // 2  # Zeile im 2-Spalten-Raster
        c = idx % 2  # Spalte 0 oder 1

        panel = ttk.Labelframe(plot_inner, text=f"Plot {idx + 1}", padding=(4, 4))  # Rahmen pro Plot
        panel.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        # war figsize=(6.2, 3.2)
        fig = Figure(figsize=(6.0, 4.6), dpi=100)  # eigene Figure pro Plot-Slot
        ax = fig.add_subplot(1, 1, 1)  # genau eine Achse pro Figure
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=panel)  # Matplotlib-Figure in Tkinter einbetten
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        canvas.draw()  # initiales Rendern (leerer Plot, aber bereit)

        plot_canvases.append(canvas)  # speichern für spätere Updates
        plot_axes.append(ax)

    # -------- Startlayout so setzen, dass NICHTS versteckt ist --------
    def _set_initial_sashes():
        # Nach dem Rendern Größen abfragen und Sash-Positionen setzen
        try:
            root.update_idletasks()  # stellt sicher, dass winfo_height aktuelle Werte liefert
            total_h = root_panes.winfo_height()
            if total_h > 0:
                # Top sichtbar größer, Plots kleiner (du musst nicht erst ziehen)
                root_panes.sashpos(0, int(total_h * 0.62))

            left_h = left_panes.winfo_height()
            if left_h > 0:
                # Input über Log, Log nicht zu klein
                left_panes.sashpos(0, int(left_h * 0.55))
        except Exception:
            pass  # falls Plattform/Theme hier zickt, soll App trotzdem starten

    root.after(120, _set_initial_sashes)  # leicht verzögert, damit Layout fertig berechnet ist

    return AppWidgets(
        btn_choose=btn_choose,
        btn_eval=btn_eval,
        btn_reset=btn_reset,
        tree_input=tree_input,
        tree_eval_func=tree_eval_func,
        tree_eval_spline=tree_eval_spline,
        txt_log=txt_log,
        axes=plot_axes,
        canvases=plot_canvases
    )
