# Import der zentralen Startfunktion der App
# run_app enthält die komplette Logik zum Initialisieren und Starten der Benutzeroberfläche
from ui.app import run_app

# Dieser Block stellt sicher, dass der Code nur dann ausgeführt wird,
# wenn diese Datei direkt gestartet wird (z. B. mit python main.py)
# und NICHT, wenn sie nur von einer anderen Datei importiert wird.
if __name__ == "__main__":
    # Startet die Anwendung
    # Ab hier übernimmt run_app:
    # - Initialisierung der GUI
    # - Aufbau der Benutzeroberfläche
    # - Start der Event-Schleife
    run_app()
