import time#Modul zur Zeitmessung

def timed_call(func, *args, **kwargs):
    """
    Führt eine Funktion func mit gegebenen Argumenten aus und misst die benötigte Laufzeit.

    Parameter:
        func (callable): Funktion, deren Laufzeit gemessen werden soll
        *args: Positionsargumente für func
        **kwargs: Schlüsselwortargumente für func

    Rückgabe:
        tuple: (result, dt)
            result: Rückgabewert von func(*args, **kwargs)
            dt (float): Laufzeit der Funktionsausführung in Sekunden
    """
    start = time.perf_counter()#Starten des Timer
    result = func(*args, **kwargs)#Berechnung
    dt = time.perf_counter() - start #Zeit
    #Speichern (result sind alle Ergebnisse der funktion)
    return result, dt
