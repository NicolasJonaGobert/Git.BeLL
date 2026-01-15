from __future__ import annotations  # ermöglicht moderne Typangaben (z. B. str | None) auch mit Vorwärtsreferenzen
from dataclasses import dataclass  # für einfache Datencontainer-Klassen (AppState)
from pathlib import Path  # für saubere Dateinamen-/Pfadbehandlung
import tkinter as tk
from tkinter import filedialog, messagebox  # Standard-Dialoge für Datei wählen und Fehlermeldungen

from metrics.timer import timed_call  # Hilfsfunktion: misst Laufzeit von Funktionsaufrufen

# Versuch, den Parser zu importieren (liest die Textdatei ein und erzeugt cfg-Dict)
# Falls das (noch) nicht klappt, soll das GUI-Grundgerüst trotzdem starten
try:
    from config.parser import lade_variablen
except Exception:
    lade_variablen = None  # dann werden später nur Hinweise geloggt


@dataclass
class AppState:
    # Speichert den aktuellen App-Zustand (damit Controller/GUI synchron bleiben)
    filepath: str | None = None  # aktuell gewählte Datei
    cfg: dict | None = None      # eingelesene Konfiguration (Parameter + Funktionen)


class Controller:
    def __init__(self, root: tk.Tk, widgets, state: AppState):
        """
        Initialisiert den Controller und verbindet UI-Elemente mit der Programmlogik.

        Zweck:
            - Speichert Referenzen auf Fenster (root), Widgets (widgets) und App-Zustand (state)
            - Verbindet Button-Aktionen mit den passenden Handler-Methoden
            - Schreibt eine Startmeldung ins Log

        Parameter:
            root (tk.Tk): Hauptfenster der Tkinter-Anwendung
            widgets (Any): Container/Objekt mit allen UI-Widgets (Buttons, Tabellen, Plots, Log)
            state (AppState): Zustand der Anwendung (aktuelle Datei, geladene Konfiguration)

        Rückgabe:
            None
        """
        # Referenzen speichern: root = Hauptfenster, w = Widgetsammlung, s = Zustand
        self.root = root
        self.w = widgets
        self.s = state

        # Buttons mit Handler-Funktionen verbinden (GUI -> Controller)
        self.w.btn_choose.configure(command=self.on_choose_file)
        self.w.btn_eval.configure(command=self.on_evaluate)
        self.w.btn_reset.configure(command=self.on_reset)

        # Startmeldung im Log
        self.log("Bereit. Wähle eine Eingabedatei.")

    def log(self, msg: str) -> None:
        """
               Schreibt eine Log-Nachricht in das Log-Textfeld und scrollt automatisch nach unten.

               Zweck:
                   - Ausgabe von Statusmeldungen und Fehlerhinweisen im GUI-Log

               Parameter:
                   msg (str): Text, der ins Log geschrieben werden soll

               Rückgabe:
                   None
               """
        # Nachricht ans Ende des Log-Felds schreiben
        self.w.txt_log.insert("end", msg + "\n")
        # Ansicht automatisch nach unten scrollen
        self.w.txt_log.see("end")

    # ------------------------------------------------------------
    # Datei wählen + Config laden
    # ------------------------------------------------------------
    def on_choose_file(self) -> None:
        """
               Öffnet einen Dateiauswahl-Dialog, lädt eine .txt-Konfiguration und füllt die Input-Tabelle.

               Zweck:
                   - Nutzer wählt eine Eingabedatei
                   - Parser (lade_variablen) liest Datei und erzeugt cfg-Dictionary
                   - cfg wird im AppState gespeichert und in der UI angezeigt
                   - Fehler werden geloggt und per Messagebox angezeigt

               Parameter:
                   keine

               Rückgabe:
                   None
               """
        # Öffnet Dateiauswahl-Dialog, Ergebnis ist Pfad als String
        path = filedialog.askopenfilename(
            title="Textdatei wählen",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        # Abbruch (Dialog geschlossen) -> nichts tun
        if not path:
            return

        # Pfad im Zustand speichern
        self.s.filepath = path
        # Nur Dateiname ins Log schreiben (übersichtlicher als kompletter Pfad)
        self.log(f"Datei gewählt: {Path(path).name}")

        # Wenn Parser nicht importiert werden konnte, nur Hinweis ausgeben
        if lade_variablen is None:
            self.log("Parser nicht importierbar. Prüfe Pfade/Imports.")
            return

        # Datei parsen und cfg-Dict erzeugen
        try:
            cfg = lade_variablen(path)
            self.s.cfg = cfg
            # Input-Tabelle aus cfg füllen
            self._fill_input_table(cfg)
            self.log("Config geladen.")
        except Exception as e:
            # bei Fehler: cfg verwerfen, Log + Popup anzeigen
            self.s.cfg = None
            self.log(f"Fehler beim Laden: {e}")
            messagebox.showerror("Fehler", f"Config konnte nicht geladen werden.\n\n{e}")

    def _fill_input_table(self, cfg: dict) -> None:
        """
               Füllt die Input-Treeview-Tabelle mit den Inhalten aus cfg.

               Zweck:
                   - Zeigt die geladenen Konfigurationswerte übersichtlich an
                   - Kürzt lange Listen und stellt Funktionswerte über gespeicherte *_expr Strings dar
                   - Stellt Splines kompakt als Anzahl + Stützstellenlängen dar

               Parameter:
                   cfg (dict): Konfigurations-Dictionary aus dem Parser

               Rückgabe:
                   None
               """
        # Tree leeren, damit keine alten Werte stehen bleiben
        for item in self.w.tree_input.get_children():
            self.w.tree_input.delete(item)

        # Diese Keys sind Funktionsausdrücke, die separat/indirekt angezeigt werden
        skip_keys = {"f_expr", "g_expr"}

        # Sortiert nach Key-Namen, damit die Anzeige stabil/vergleichbar bleibt
        for k in sorted(cfg.keys(), key=str):
            if k in skip_keys:
                continue

            v = cfg[k]
            t = type(v).__name__  # Datentyp als String (z. B. int, float, function)

            # Funktionen: lieber den ursprünglichen Ausdruck anzeigen (falls vorhanden)
            if callable(v):
                expr_key = f"{k}_expr"
                v_str = cfg.get(expr_key, "<funktion>")

            # Splines: kompakte Zusammenfassung (Anzahl und Stützstellen je Spline)
            elif k == "splines":
                try:
                    n_splines = len(v)  # Anzahl der Splines
                    lengths = [len(xs) for (xs, ys) in v]  # Anzahl Stützstellen pro Spline
                    v_str = f"{n_splines} Splines, Stützstellen: {lengths}"
                except Exception:
                    v_str = "<Spline-Daten>"

            # Lange Listen kürzen, damit die Tabelle lesbar bleibt
            elif isinstance(v, (list, tuple)) and len(v) > 8:
                v_str = f"[{', '.join(map(str, v[:8]))}, ...]"

            # Standard: alles andere einfach als String
            else:
                v_str = str(v)

            # Zeile in Input-Tabelle einfügen
            self.w.tree_input.insert("", "end", values=(k, v_str, t))

    # ------------------------------------------------------------
    # Auswerten
    # ------------------------------------------------------------
    def on_evaluate(self) -> None:
        """
               Validiert die geladene Konfiguration und startet danach Berechnung und Plots.

               Zweck:
                   - Prüft, ob cfg vorhanden ist
                   - Validiert alle notwendigen Parameter (Intervall, Positivität, Geradeheit für Simpson)
                   - Startet dann die Auswertung (_run_evaluation) und zeichnet Plots (_draw_plots)

               Parameter:
                   keine

               Rückgabe:
                   None
               """
        # Ohne cfg kann nichts berechnet werden
        if not self.s.cfg:
            self.log("Keine Config geladen.")
            return

        # Validierungsfunktionen (werfen ValueError bei ungültigen Parametern)
        from utils.validation import check_interval, check_positive, check_even

        def _validate_cfg_for_gui(cfg: dict) -> None:
            # Pflichtwerte aus cfg holen (KeyError, falls etwas fehlt)
            a = cfg["a"]
            b = cfg["b"]
            nr = cfg["nr"]
            nt = cfg["nt"]
            ns = cfg["ns"]
            N = cfg["N"]
            err = cfg["err"]
            kr = cfg["kr"]
            krs = cfg["krs"]
            kt = cfg["kt"]
            ks = cfg["ks"]
            km = cfg["km"]
            kmi=cfg["kmi"]
            wm = cfg["wm"]
            # Intervall muss gültig sein
            check_interval(a, b)

            # n-Werte müssen positiv sein
            check_positive(nr, "nr")
            check_positive(nt, "nt")
            check_positive(ns, "ns")
            check_even(ns, "ns")  # ns muss gerade sein (Simpson-Voraussetzung)

            # Monte Carlo Anzahl muss positiv sein
            check_positive(N, "N")

            # Parameter für Fehlersuche / Schrittweiten etc. müssen positiv sein
            check_positive(err, "err")
            check_positive(kr, "kr")
            check_positive(krs, "krs")
            check_positive(kt, "kt")
            check_positive(ks, "ks")
            check_positive(km, "km")
            check_positive(kmi, "kmi")
            check_positive(wm, "wm")

        # Validierung durchführen, Fehler abfangen und anzeigen
        try:
            _validate_cfg_for_gui(self.s.cfg)  # <- ohne self.
        except ValueError as e:
            self.log(f"Fehler in der Eingabe: {e}")
            messagebox.showerror("Eingabefehler", str(e))
            return

        # Startausgabe + UI kurz aktualisieren (damit Log sofort sichtbar ist)
        self.log("Starte Auswertung...")
        self.root.update_idletasks()

        # Berechnung + Plot-Erstellung
        self._run_evaluation()
        self._draw_plots()

        self.log("Auswertung abgeschlossen.")

    def _run_evaluation(self) -> None:
        """
                Führt die eigentliche Auswertung aus und füllt die Ergebnis-Tabellen.

                Zweck:
                    - Liest Parameter/Funktionen aus cfg
                    - Baut h=|f-g| und hs=|s1-s2|
                    - Führt alle numerischen Methoden aus (fixe N/n sowie fehlergesteuerte Suche)
                    - Misst Laufzeiten (timed_call) und Funktionsaufrufe (CountedFunction)
                    - Berechnet Fehler relativ zu Referenzintegralen (stammint)
                    - Trägt formatiert alle Ergebnisse in die GUI-Tabellen ein
                    - Speichert Monte-Carlo-Punkte für die spätere Plot-Ausgabe

                Parameter:
                    keine

                Rückgabe:
                    None
                """
        cfg = self.s.cfg

        # Werte und Funktionen definieren (aus cfg übernommen)
        a = cfg["a"]
        b = cfg["b"]
        f = cfg["f"]
        g = cfg["g"]
        nr = int(cfg["nr"])
        nt = int(cfg["nt"])
        ns = int(cfg["ns"])
        N = int(cfg["N"])
        err = cfg["err"]
        pl = cfg["splines"]
        kr= int(cfg["kr"])
        krs = int(cfg["krs"])
        kt = int(cfg["kt"])
        ks = int(cfg["ks"])
        km = int(cfg["km"])
        kma = int(cfg["kma"])
        kmi = int(cfg["kmi"])
        wm = int(cfg["wm"])
        # Funktionen bauen: h ist Betragsfunktion zwischen f und g, hs ist Betragsfunktion aus Splines
        from core.functions import betragsfunk,splinebetrag
        h = betragsfunk(f, g)
        hs = splinebetrag(pl)

        # Tabellen leeren (alte Ergebniszeilen entfernen)
        for t in (self.w.tree_eval_func, self.w.tree_eval_spline):
            for item in t.get_children():
                t.delete(item)

        # Methoden/Tools importieren (Berechnung, Fehler, Timing, Zähler)
        from core.riemann import riemann_untersumme,riemann_obersumme,mittel_riemann,errunter,errober,err_mittel_riemann
        from core.trapez import trapezregel,trapezerr
        from core.simpson import simpsonregel,simpsonerr
        from core.monte import geomonte,errmonte,mittel_monte,err_mittel_monte
        from core.analytisch import stammint
        from metrics.timer import timed_call
        from metrics.error import error
        from metrics.counter import CountedFunction
        from utils.validation import safe_func

        # "safe_func" ersetzt problematische x=0 Werte (numerisch stabiler bei Grenzwert-Funktionen)
        h_safe = safe_func(h, 1e-12)
        hs_safe = safe_func(hs, 1e-12)
        # CountedFunction zählt Funktionsaufrufe, damit Aufwand vergleichbar wird
        h_c = CountedFunction(h_safe, name="h")
        h_c.reset()
        hs_c = CountedFunction(hs_safe, name="hs")
        hs_c.reset()

        # ------------------------------------------------------------
        # Riemann-Summen (fixes nr)
        # ------------------------------------------------------------
        ruh, dt0 = timed_call(riemann_untersumme, nr, a, b, h_c, h_safe, kr)  # Untersumme h
        calls0 = h_c.calls
        h_c.reset()

        roh, dt1 = timed_call(riemann_obersumme, nr, a, b, h_c, h_safe, kr)  # Obersumme h
        calls1 = h_c.calls
        h_c.reset()

        rohs, dt2 = timed_call(riemann_obersumme, nr, a, b, hs_c,hs_safe , kr)  # Obersumme hs
        calls2 = hs_c.calls
        hs_c.reset()

        ruhs, dt3 = timed_call(riemann_untersumme, nr, a, b, hs_c,hs_safe , kr)  # Untersumme hs
        calls3 = hs_c.calls
        hs_c.reset()

        rmh, dt4 = timed_call(mittel_riemann, nr, a, b, h_c, hs_safe , h_safe, kr, 0)  # Mittelwert os/us für h
        calls4 = h_c.calls
        h_c.reset()

        rmhs, dt5 = timed_call(mittel_riemann, nr, a, b,  h_safe, hs_c,hs_safe, kr, 1)  # Mittelwert os/us für hs
        calls5 = hs_c.calls
        hs_c.reset()
        # ------------------------------------------------------------
        # Analytisch (Referenzwert, falls möglich)
        # ------------------------------------------------------------
        (Ih, errh), dt18 = timed_call(stammint, a, b, h_c, hs_safe , 0)
        calls18 = h_c.calls
        h_c.reset()

        (Ihs, errhs), dt19 = timed_call(stammint, a, b,  h_safe, hs_c, 1)
        calls19 = hs_c.calls
        hs_c.reset()
        # ------------------------------------------------------------
        # Fehlergesteuerte n-Suche (erhöht n, bis err erreicht wird)
        # ------------------------------------------------------------
        (ne0, fruh), dt6 = timed_call(errunter, err, h_c, hs_safe , a, b, h_safe,Ih, krs, kr, 0)
        calls6 = h_c.calls
        h_c.reset()

        (ne1, fruhs), dt7 = timed_call(errunter, err,  h_safe, hs_c, a, b,hs_safe ,Ihs, krs, kr, 1)
        calls7 = hs_c.calls
        hs_c.reset()

        (ne2, froh), dt8 = timed_call(errober, err, h_c, hs_safe , a, b, h_safe,Ih, krs, kr, 0)
        calls8 = h_c.calls
        h_c.reset()

        (ne3, frohs), dt9 = timed_call(errober, err,  h_safe, hs_c, a, b,hs,Ihs, krs, kr, 1)
        calls9 = hs_c.calls
        hs_c.reset()

        (ne4, fmh), dt10 = timed_call(err_mittel_riemann, err, a, b, h_c, hs_safe , h_safe,Ih, krs, kr, 0)
        calls10 = h_c.calls
        h_c.reset()

        (ne5, fmhs), dt11 = timed_call(err_mittel_riemann, err, a, b,  h_safe, hs_c,hs_safe ,Ihs, krs, kr, 1)
        calls11 = hs_c.calls
        hs_c.reset()

        (ne6, seh), dt12 = timed_call(simpsonerr, h_c, hs_safe , err, a, b,Ih, ks, 0)
        calls12 = h_c.calls
        h_c.reset()

        (ne7, sehs), dt13 = timed_call(simpsonerr,  h_safe, hs_c, err, a, b,Ihs, ks, 1)
        calls13 = hs_c.calls
        hs_c.reset()

        (ne8, teh), dt14 = timed_call(trapezerr, err, h_c, hs_safe , a, b,Ih, kt, 0)
        calls14 = h_c.calls
        h_c.reset()

        (ne9, tehs), dt15 = timed_call(trapezerr, err,  h_safe, hs_c, a, b,Ihs, kt, 1)
        calls15 = hs_c.calls
        hs_c.reset()

        (ne10, meh,Zeh), dt16 = timed_call(errmonte, err, a, b, h_c, hs_safe ,kma, h_safe,Ih, km, 0)
        calls16 = h_c.calls
        h_c.reset()

        (ne11, mehs,Zehs), dt17 = timed_call(errmonte, err, a, b,  h_safe, hs_c,kma,hs_safe,Ihs, km, 1)
        calls17 = hs_c.calls
        hs_c.reset()

        (ne12,mmeh),dta=timed_call(err_mittel_monte,err,a, b, h_c, hs_safe, kma, h_safe,wm,kmi,Ih, 0)
        callsa = h_c.calls
        h_c.reset()

        (ne13,mmehs),dtb=timed_call(err_mittel_monte,err,a, b, h_safe, hs_c, kma, hs_safe,wm,kmi,Ihs, 1)
        callsb = hs_c.calls
        hs_c.reset()

        # ------------------------------------------------------------
        # Fixe Simpson/Trapez/Monte Carlo (mit vorgegebenem ns/nt/N)
        # ------------------------------------------------------------
        sh, dt20 = timed_call(simpsonregel, h_c, hs_safe , ns, a, b, 0)
        calls20 = h_c.calls
        h_c.reset()

        shs, dt21 = timed_call(simpsonregel,  h_safe, hs_c, ns, a, b, 1)
        calls21 = hs_c.calls
        hs_c.reset()

        th, dt22 = timed_call(trapezregel, nt, h_c, hs_safe , a, b, 0)
        calls22 = h_c.calls
        h_c.reset()

        ths, dt23 = timed_call(trapezregel, nt,  h_safe, hs_c, a, b, 1)
        calls23 = hs_c.calls
        hs_c.reset()

        (mch,Zih,xzh,yzh),dt24 = timed_call(geomonte,N, a, b, h_c, hs_safe ,kma, h_safe, 0)
        calls24 = h_c.calls
        h_c.reset()

        (mchs,Zihs,xzhs,yzhs), dt25 = timed_call(geomonte, N, a, b, h_safe, hs_c,kma,hs_safe , 1)
        calls25 = hs_c.calls
        hs_c.reset()

        mmh,dt26=timed_call(mittel_monte,N, a, b, h_c, hs_safe, kma, h_safe,wm, 0)
        calls26 = h_c.calls
        h_c.reset()

        mmhs,dt27=timed_call(mittel_monte,N, a, b, h_safe, hs_c, kma, hs_safe,wm, 1)
        calls27 = hs_c.calls
        hs_c.reset()

        # Monte-Carlo-Punkte speichern, damit _draw_plots darauf zugreifen kann
        self._mc_h = {"Zih": Zih, "xzh": xzh, "yzh": yzh}
        self._mc_hs = {"Zihs": Zihs, "xzhs": xzhs, "yzhs": yzhs}

        # ------------------------------------------------------------
        # Fehler berechnen (Vergleich zu analytischem Referenzwert)
        # error(...) liefert: abs_h, abs_hs, pct_h, pct_hs
        # ------------------------------------------------------------
        e_ruh = error(ruh, ruhs,Ih,Ihs, a, b,)
        e_roh = error(roh, rohs,Ih,Ihs, a, b,)
        e_rmh = error(rmh, rmhs,Ih,Ihs, a, b,)
        e_th = error(th, ths,Ih,Ihs, a, b,)
        e_sh = error(sh, shs,Ih,Ihs, a, b,)
        e_monte = error(mch, mchs,Ih,Ihs, a, b,)
        e_mmonte = error(mmh,mmhs,Ih,Ihs, a, b,)

        # für die err-Zeile
        e_fruh = error(fruh, fruhs,Ih,Ihs, a, b,)
        e_froh = error(froh, frohs,Ih,Ihs, a, b,)
        e_fmh = error(fmh, fmhs,Ih,Ihs, a, b,)
        e_teh = error(teh, tehs,Ih,Ihs, a, b,)
        e_seh = error(seh, sehs,Ih,Ihs, a, b,)
        e_meh2 = error(meh, mehs,Ih,Ihs, a, b,)
        e_mmeh = error(mmeh, mmehs,Ih,Ihs, a, b,)


        # Formatierung für GUI-Anzeige (Zahlen/Zeiten/Prozente schön darstellen)
        from utils.formatting import _fmt_dt, _fmt_num,_fmt_abs,_fmt_pct

        # ------------------------------------------------------------
        # Ergebniszeilen in Tabellen eintragen (h)
        # ------------------------------------------------------------
        self.w.tree_eval_func.insert("", "end",
                                     values=("Riemann U", nr, _fmt_num(ruh), _fmt_abs(e_ruh[0]), _fmt_pct(e_ruh[2]),
                                             _fmt_dt(dt0), calls0)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=("Riemann O", nr, _fmt_num(roh), _fmt_abs(e_roh[0]), _fmt_pct(e_roh[2]),
                                             _fmt_dt(dt1), calls1)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=("Riemann Ø", nr, _fmt_num(rmh), _fmt_abs(e_rmh[0]), _fmt_pct(e_rmh[2]),
                                             _fmt_dt(dt4), calls4)
                                     )
        # Trapez / Simpson (fixe nt/ns)
        self.w.tree_eval_func.insert("", "end",
                                     values=("Trapez", nt, _fmt_num(th), _fmt_abs(e_th[0]), _fmt_pct(e_th[2]),
                                             _fmt_dt(dt22), calls22)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=("Simpson", ns, _fmt_num(sh), _fmt_abs(e_sh[0]), _fmt_pct(e_sh[2]),
                                             _fmt_dt(dt20), calls20)
                                     )

        # Monte Carlo (Anzeige: Treffer|N)
        self.w.tree_eval_func.insert("", "end",
                                     values=("Monte Carlo", f"{Zih}|{N}", _fmt_num(mch), _fmt_abs(e_monte[0]),
                                             _fmt_pct(e_monte[2]), _fmt_dt(dt24), calls24)
                                     )
        # Monte Carlo (Anzeige: N)
        self.w.tree_eval_func.insert("", "end",
                                     values=("Monte Carlo Ø", f"{N}", _fmt_num(mmh), _fmt_abs(e_mmonte[0]),
                                             _fmt_pct(e_mmonte[2]), _fmt_dt(dt26), calls26)
                                     )

        # Fehlergesteuerte n-Suche (h)
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Riemann U err={err}", ne0, _fmt_num(fruh), _fmt_abs(e_fruh[0]),
                                             _fmt_pct(e_fruh[2]), _fmt_dt(dt6), calls6)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Riemann O err={err}", ne2, _fmt_num(froh), _fmt_abs(e_froh[0]),
                                             _fmt_pct(e_froh[2]), _fmt_dt(dt8), calls8)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Riemann Ø err={err}", ne4, _fmt_num(fmh), _fmt_abs(e_fmh[0]),
                                             _fmt_pct(e_fmh[2]), _fmt_dt(dt10), calls10)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Trapez err={err}", ne8, _fmt_num(teh), _fmt_abs(e_teh[0]),
                                             _fmt_pct(e_teh[2]), _fmt_dt(dt14), calls14)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Simpson err={err}", ne6, _fmt_num(seh), _fmt_abs(e_seh[0]),
                                             _fmt_pct(e_seh[2]), _fmt_dt(dt12), calls12)
                                     )
        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Monte err={err}", f"{Zeh}|{ne10}", _fmt_num(meh), _fmt_abs(e_meh2[0]),
                                             _fmt_pct(e_meh2[2]), _fmt_dt(dt16), calls16)
                                     )

        self.w.tree_eval_func.insert("", "end",
                                     values=(f"Monte Ø err={err}", f"{ne12}", _fmt_num(mmeh), _fmt_abs(e_mmeh[0]),
                                             _fmt_pct(e_mmeh[2]), _fmt_dt(dta), callsa)
                                     )

        # Referenzwert (analytisch) als letzte Zeile
        self.w.tree_eval_func.insert("", "end",
                                     values=("Integralwert (Referenz) ", "-", _fmt_num(Ih), _fmt_abs(0.0), _fmt_pct(0.0),
                                             _fmt_dt(dt18), calls18)
                                     )


        # ------------------------------------------------------------
        # Ergebniszeilen in Tabellen eintragen (hs)
        # ------------------------------------------------------------
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Riemann U", nr, _fmt_num(ruhs), _fmt_abs(e_ruh[1]), _fmt_pct(e_ruh[3]),
                                               _fmt_dt(dt3), calls3)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Riemann O", nr, _fmt_num(rohs), _fmt_abs(e_roh[1]), _fmt_pct(e_roh[3]),
                                               _fmt_dt(dt2), calls2)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Riemann Ø", nr, _fmt_num(rmhs), _fmt_abs(e_rmh[1]), _fmt_pct(e_rmh[3]),
                                               _fmt_dt(dt5), calls5)
                                       )

        # Trapez / Simpson (fixe nt/ns)
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Trapez", nt, _fmt_num(ths), _fmt_abs(e_th[1]), _fmt_pct(e_th[3]),
                                               _fmt_dt(dt23), calls23)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Simpson", ns, _fmt_num(shs), _fmt_abs(e_sh[1]), _fmt_pct(e_sh[3]),
                                               _fmt_dt(dt21), calls21)
                                       )

        # Monte Carlo
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Monte Carlo ", f"{Zihs}|{N}", _fmt_num(mchs), _fmt_abs(e_monte[1]),
                                               _fmt_pct(e_monte[3]), _fmt_dt(dt25), calls25)
                                       )
        # Monte Carlo (Anzeige: N)
        self.w.tree_eval_spline.insert("", "end",
                                     values=("Monte Carlo Ø", f"{N}", _fmt_num(mmhs), _fmt_abs(e_mmonte[1]),
                                             _fmt_pct(e_mmonte[3]), _fmt_dt(dt27), calls27)
                                     )

        # Fehlergesteuerte n-Suche (hs)
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Riemann U err={err}", ne1, _fmt_num(fruhs), _fmt_abs(e_fruh[1]),
                                               _fmt_pct(e_fruh[3]), _fmt_dt(dt7), calls7)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Riemann O err={err}", ne3, _fmt_num(frohs), _fmt_abs(e_froh[1]),
                                               _fmt_pct(e_froh[3]), _fmt_dt(dt9), calls9)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Riemann Ø err={err}", ne5, _fmt_num(fmhs), _fmt_abs(e_fmh[1]),
                                               _fmt_pct(e_fmh[3]), _fmt_dt(dt11), calls11)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Trapez err={err}", ne9, _fmt_num(tehs), _fmt_abs(e_teh[1]),
                                               _fmt_pct(e_teh[3]), _fmt_dt(dt15), calls15)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Simpson err={err}", ne7, _fmt_num(sehs), _fmt_abs(e_seh[1]),
                                               _fmt_pct(e_seh[3]), _fmt_dt(dt13), calls13)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                       values=(f"Monte err={err}", f"{Zehs}|{ne11}", _fmt_num(mehs), _fmt_abs(e_meh2[1]),
                                               _fmt_pct(e_meh2[3]), _fmt_dt(dt17), calls17)
                                       )
        self.w.tree_eval_spline.insert("", "end",
                                     values=(f"Monte Ø err={err}", f"{ne13}", _fmt_num(mmehs), _fmt_abs(e_mmeh[1]),
                                             _fmt_pct(e_mmeh[3]), _fmt_dt(dtb), callsb)
                                     )
        self.w.tree_eval_spline.insert("", "end",
                                       values=("Integralwert (Referenz)", "-", _fmt_num(Ihs), _fmt_abs(0.0), _fmt_pct(0.0),
                                               _fmt_dt(dt19), calls19)
                                       )

    # ------------------------------------------------------------
    # Plots: 14 Stück füllen + jeweils draw() auf dem passenden Canvas
    # ------------------------------------------------------------
    def _draw_plots(self) -> None:
        """
        Zeichnet alle 14 Plots in die bereits im UI erzeugten Axes/Canvases.

        Zweck:
            - Erzeugt aus cfg die Funktionen f,g sowie Splines s1,s2 und Betragsfunktionen h,hs
            - Setzt alle Axes zurück (clear, labels, grid, Titel)
            - Füllt die 14 Plot-Panels mit den passenden Visualisierungen
            - Ruft für jeden Plot das passende canvas.draw() auf
            - Verwendet gespeicherte Monte-Carlo-Punktmengen aus _run_evaluation (self._mc_h, self._mc_hs)

        Parameter:
            keine

        Rückgabe:
            None
        """
        # Plot-Helfer importieren (zeichnen auf bestehende Axes)
        from core.functions import (betragsfunk,spline,splinebetrag)
        from plots.plotter import (
            plot_funktionen_fläche,
            plot_betrag,
            plot_riemannsumme,
            plot_trapezregel,
            plot_simpson,
            plot_monte
        )

        # Definieren der Variablen und Funktionen (aus cfg)
        cfg = self.s.cfg
        a = cfg["a"]
        b = cfg["b"]
        f = cfg["f"]
        g = cfg["g"]
        nr = cfg["nr"]
        nt = cfg["nt"]
        ns = cfg["ns"]
        N = cfg["N"]
        pl=cfg["splines"]
        kma = cfg["kma"]

        # h = |f-g|, s1/s2 = Splines, hs = |s1-s2|
        h=betragsfunk(f, g)
        s1=spline(pl, 0)
        s2=spline(pl, 1)
        hs=splinebetrag(pl)

        # alle 14 Plots zurücksetzen (clear + Standardachsen)
        for i, ax in enumerate(self.w.axes):
            ax.clear()
            ax.grid(True)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title(f"Plot {i+1}")

        # 1. Plot f und g mit Fläche
        self.w.axes[0].set_title("Funktionen $f$ und $g$, Fläche zwischen $f$ und $g$")
        plot_funktionen_fläche(self.w.axes[0], a, b, f, g)
        self.w.canvases[0].draw()

        # 2. Plot s1 und s2 mit Fläche
        self.w.axes[1].set_title("Spline-Funktionen, Fläche zwischen $s_1$ und $s_2$")
        plot_funktionen_fläche(self.w.axes[1], a, b, s1, s2)
        self.w.canvases[1].draw()

        # 3. Plot Betragsfunktion von f,g
        self.w.axes[2].set_title("Betragsfunktion $B(x)$=|$f(x)-g(x)$|")
        plot_betrag(self.w.axes[2], a, b, h)
        self.w.canvases[2].draw()

        # 4. Plot Betragsfunktion von s1,s2
        self.w.axes[3].set_title("Betragsfunktion $B_s(x)$=|$s_1(x)-s_2(x)$|")
        plot_betrag(self.w.axes[3], a, b, hs)
        self.w.canvases[3].draw()

        # 5. Plot Untersumme h
        self.w.axes[4].set_title("Riemann-Untersumme zu $B(x)$")
        plot_riemannsumme(self.w.axes[4], a, b, nr, h, "u")
        self.w.canvases[4].draw()

        # 6. Plot Untersumme hs
        self.w.axes[5].set_title("Riemann-Untersumme zu $B_s(x)$")
        plot_riemannsumme(self.w.axes[5], a, b, nr, hs, "u")
        self.w.canvases[5].draw()

        # 7. Plot Obersumme h
        self.w.axes[6].set_title("Riemann-Obersumme zu $B(x)$")
        plot_riemannsumme(self.w.axes[6], a, b, nr, h, "o")
        self.w.canvases[6].draw()

        # 8. Plot Obersumme hs
        self.w.axes[7].set_title("Riemann-Obersumme zu $B_s(x)$")
        plot_riemannsumme(self.w.axes[7], a, b, nr, hs, "o")
        self.w.canvases[7].draw()

        # 9. Plot Trapez h
        self.w.axes[8].set_title("Trapezregel zu $B(x)$")
        plot_trapezregel(self.w.axes[8], a, b, nt, h)
        self.w.canvases[8].draw()

        # 10. Plot Trapez hs
        self.w.axes[9].set_title("Trapezregel zu $B_s(x)$")
        plot_trapezregel(self.w.axes[9], a, b, nt, hs)
        self.w.canvases[9].draw()

        # 11. Plot Simpson h
        self.w.axes[10].set_title("Simpsonregel zu $B(x)$")
        plot_simpson(self.w.axes[10], a, b, ns, h)
        self.w.canvases[10].draw()

        # 12. Plot Simpson hs
        self.w.axes[11].set_title("Simpsonregel zu $B_s(x)$")
        plot_simpson(self.w.axes[11], a, b, ns, hs)
        self.w.canvases[11].draw()

        # Abrufen der Monte-Carlo-Punkte aus _run_evaluation()
        mc_h = self._mc_h
        mc_hs = self._mc_hs

        # 13. Plot Monte Carlo h (inkl. Zufallspunkte und Trefferzahl)
        self.w.axes[12].set_title("Monte Carlo zu $B(x)$")
        plot_monte(self.w.axes[12],a, b, N,h,kma,mc_h["xzh"],mc_h["yzh"],mc_h["Zih"])
        self.w.canvases[12].draw()

        # 14. Plot Monte Carlo hs
        self.w.axes[13].set_title("Monte Carlo zu $B_s(x)$")
        plot_monte(self.w.axes[13],a, b, N,hs,kma,mc_hs["xzhs"],mc_hs["yzhs"],mc_hs["Zihs"], "hs")
        self.w.canvases[13].draw()

    # ------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------
    def on_reset(self) -> None:
        """
        Setzt den GUI-Zustand vollständig zurück.

        Zweck:
            - Löscht den aktuellen Dateipfad und die geladene Konfiguration aus AppState
            - Leert alle Tabellen (Input, Funktionsauswertung, Spline-Auswertung)
            - Leert das Log-Feld und schreibt die Startmeldung erneut
            - Setzt alle 14 Plots zurück und zeichnet die leeren Achsen neu

        Parameter:
            keine

        Rückgabe:
            None
        """
        # Zustand zurücksetzen
        self.s.filepath = None
        self.s.cfg = None

        # Tabellen leeren (Input + beide Ergebnis-Tabellen)
        for tr in (self.w.tree_input, self.w.tree_eval_func, self.w.tree_eval_spline):
            for item in tr.get_children():
                tr.delete(item)

        # Log leeren und Starttext anzeigen
        self.w.txt_log.delete("1.0", "end")
        self.log("Reset. Wähle eine Eingabedatei.")

        # Plots leeren und neu zeichnen
        for i, ax in enumerate(self.w.axes, start=1):
            ax.clear()
            ax.set_title(f"Plot {i}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)
            self.w.canvases[i-1].draw()


