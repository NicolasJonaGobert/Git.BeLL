from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


@dataclass
class AppWidgets:
    # Buttons
    btn_choose: ttk.Button
    btn_eval: ttk.Button
    btn_reset: ttk.Button

    # Tabellen
    tree_input: ttk.Treeview
    tree_eval_func: ttk.Treeview
    tree_eval_spline: ttk.Treeview

    # Log
    txt_log: tk.Text

    # Plots (14 Stück)
    axes: list               # Liste mit 14 Axes
    canvases: list           # Liste mit 14 FigureCanvasTkAgg


def build_ui(root: tk.Tk) -> AppWidgets:
    """
    Baut die komplette Tkinter-Oberfläche auf, erstellt alle Widgets (Buttons, Tabellen, Log, Plotbereich) und gibt sie gesammelt zurück.

    Parameter:
        root (tk.Tk): Hauptfenster der Tkinter-Anwendung

    Rückgabe:
        AppWidgets: Container mit Referenzen auf alle erzeugten UI-Elemente (Buttons, Treeviews, Log-Textfeld, Axes und Canvas-Objekte)
    """
    root.title("BeLL – Auswertung")

    # -------- Topbar (Buttons) --------
    topbar = ttk.Frame(root, padding=(8, 6))
    topbar.grid(row=0, column=0, sticky="ew")
    root.grid_columnconfigure(0, weight=1)

    btn_choose = ttk.Button(topbar, text="Datei wählen…")
    btn_eval = ttk.Button(topbar, text="Auswerten")
    btn_reset = ttk.Button(topbar, text="Reset")

    btn_choose.grid(row=0, column=0, padx=(0, 6))
    btn_eval.grid(row=0, column=1, padx=(0, 6))
    btn_reset.grid(row=0, column=2)

    topbar.grid_columnconfigure(3, weight=1)

    # -------- Main Panes (links / rechts) --------
    main_panes = ttk.Panedwindow(root, orient="horizontal")
    main_panes.grid(row=1, column=0, sticky="nsew")
    root.grid_rowconfigure(1, weight=1)

    left = ttk.Frame(main_panes)
    right = ttk.Frame(main_panes)
    main_panes.add(left, weight=1)   # links kleiner
    main_panes.add(right, weight=3)  # rechts größer

    # -------- Linke Seite: Input (oben) + Log (unten) --------
    left_panes = ttk.Panedwindow(left, orient="vertical")
    left_panes.grid(row=0, column=0, sticky="nsew")
    left.grid_rowconfigure(0, weight=1)
    left.grid_columnconfigure(0, weight=1)

    input_frame = ttk.Labelframe(left_panes, text="Input", padding=(6, 6))
    log_frame = ttk.Labelframe(left_panes, text="Log", padding=(6, 6))
    left_panes.add(input_frame, weight=3)  # Input kleiner
    left_panes.add(log_frame, weight=1)    # Log klein

    # Input Treeview
    tree_input = ttk.Treeview(
        input_frame,
        columns=("key", "value", "type"),
        show="headings",
        height=10
    )
    tree_input.heading("key", text="Schlüssel")
    tree_input.heading("value", text="Wert")
    tree_input.heading("type", text="Typ")
    tree_input.column("key", width=140, anchor="w")
    tree_input.column("value", width=220, anchor="w")
    tree_input.column("type", width=80, anchor="w")

    sb_input_y = ttk.Scrollbar(input_frame, orient="vertical", command=tree_input.yview)
    tree_input.configure(yscrollcommand=sb_input_y.set)

    tree_input.grid(row=0, column=0, sticky="nsew")
    sb_input_y.grid(row=0, column=1, sticky="ns")
    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)

    # Log Text
    txt_log = tk.Text(log_frame, height=6, wrap="word")
    sb_log_y = ttk.Scrollbar(log_frame, orient="vertical", command=txt_log.yview)
    txt_log.configure(yscrollcommand=sb_log_y.set)
    txt_log.grid(row=0, column=0, sticky="nsew")
    sb_log_y.grid(row=0, column=1, sticky="ns")
    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    # -------- Rechte Seite: Auswertung (oben) + Plots (unten) --------
    right_panes = ttk.Panedwindow(right, orient="vertical")
    right_panes.grid(row=0, column=0, sticky="nsew")
    right.grid_rowconfigure(0, weight=1)
    right.grid_columnconfigure(0, weight=1)

    eval_frame = ttk.Frame(right_panes)
    plot_frame = ttk.Labelframe(right_panes, text="Plot", padding=(6, 6))
    right_panes.add(eval_frame, weight=2)
    right_panes.add(plot_frame, weight=3)  # Plots größer

    # -------- Auswertung: zwei Tabellen --------
    eval_panes = ttk.Panedwindow(eval_frame, orient="vertical")
    eval_panes.grid(row=0, column=0, sticky="nsew")
    eval_frame.grid_rowconfigure(0, weight=1)
    eval_frame.grid_columnconfigure(0, weight=1)

    eval_func = ttk.Labelframe(eval_panes, text="Auswertung – Funktionen", padding=(6, 6))
    eval_spline = ttk.Labelframe(eval_panes, text="Auswertung – Spline-Funktionen", padding=(6, 6))
    eval_panes.add(eval_func, weight=1)
    eval_panes.add(eval_spline, weight=1)

    def _make_eval_tree(parent: ttk.Frame) -> ttk.Treeview:
        tree = ttk.Treeview(
            parent,
            columns=("method", "result", "error", "time", "calls"),
            show="headings",
            height=6
        )
        tree.heading("method", text="Funktion(en)")
        tree.heading("result", text="Ergebnis")
        tree.heading("error", text="Fehler")
        tree.heading("time", text="Zeit")
        tree.heading("calls", text="Aufrufe")

        tree.column("method", width=200, anchor="w")
        tree.column("result", width=130, anchor="w")
        tree.column("error", width=130, anchor="w")
        tree.column("time", width=90, anchor="w")
        tree.column("calls", width=90, anchor="w")

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        return tree

    tree_eval_func = _make_eval_tree(eval_func)
    tree_eval_spline = _make_eval_tree(eval_spline)

    # -------- Plotbereich: scrollbares Grid (14 Plots, 2 Spalten) --------

    plot_canvas = tk.Canvas(plot_frame, highlightthickness=0)
    plot_scroll = ttk.Scrollbar(plot_frame, orient="vertical", command=plot_canvas.yview)
    plot_canvas.configure(yscrollcommand=plot_scroll.set)

    plot_canvas.grid(row=0, column=0, sticky="nsew")
    plot_scroll.grid(row=0, column=1, sticky="ns")
    plot_frame.grid_rowconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(0, weight=1)

    plot_inner = ttk.Frame(plot_canvas)
    plot_window = plot_canvas.create_window((0, 0), window=plot_inner, anchor="nw")

    def _on_plot_inner_configure(event):
        plot_canvas.configure(scrollregion=plot_canvas.bbox("all"))

    plot_inner.bind("<Configure>", _on_plot_inner_configure)

    def _on_plot_canvas_configure(event):
        plot_canvas.itemconfigure(plot_window, width=event.width)

    plot_canvas.bind("<Configure>", _on_plot_canvas_configure)

    # Mausrad-Scroll (Windows/Mac + Linux)
    def _on_mousewheel(event):
        plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_up(event):
        plot_canvas.yview_scroll(-3, "units")

    def _on_linux_down(event):
        plot_canvas.yview_scroll(3, "units")

    plot_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    plot_canvas.bind_all("<Button-4>", _on_linux_up)
    plot_canvas.bind_all("<Button-5>", _on_linux_down)

    plot_canvases = []
    plot_axes = []

    for idx in range(14):
        r = idx // 2
        c = idx % 2

        panel = ttk.Labelframe(plot_inner, text=f"Plot {idx + 1}", padding=(6, 6))
        panel.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        plot_inner.grid_columnconfigure(0, weight=1)
        plot_inner.grid_columnconfigure(1, weight=1)

        fig = Figure(figsize=(4.8, 3.0), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=panel)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        canvas.draw()

        plot_canvases.append(canvas)
        plot_axes.append(ax)

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
