# main.py
import subprocess
import os
import sys
import signal
import time

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))

# Aggiungi le directory al path
mon_dir = os.path.join(current_dir, 'mon')
sys.path.insert(0, mon_dir)

server_dir = os.path.join(current_dir, 'server')

import mon.setup as setup
import mon.monitoring as monitoring
import server.request as request
import server.ssl.certs as certs

def stop_monitoring(sig, frame):
    print("\nInterruzione rilevata. Chiusura in corso...")
    monitoring.stop_event.set()  # Impostiamo l'evento per fermare il monitoraggio

def start_server():
    # Avvia il server in un processo separato
    server_path = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
    subprocess.Popen([sys.executable, server_path])

def main():
    # Registra il gestore di segnali
    signal.signal(signal.SIGINT, stop_monitoring)

    if certs.certificati():
        # Avvia il server
        start_server()
        time.sleep(5)
    else:
        print("Impossibile avviare l'API server, certificati mancanti o corrotti")
        # Invia il segnale SIGINT al processo corrente
        os.kill(os.getpid(), signal.SIGINT)
    
    # Chiamata alla funzione di setup
    setup.setup()  
    # Avvia il monitoraggio
    monitoring.start_monitoring()
    
    # Avvia il thread per le richieste API periodiche
    api_updater = request.main()  # Ottieni l'oggetto thread API

    try:
        # Mantieni il processo principale in esecuzione
        while not monitoring.stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        monitoring.stop_monitoring()
        api_updater.stop()  # Ferma anche il thread API

if __name__ == "__main__":
    main() 