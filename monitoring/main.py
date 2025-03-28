import subprocess, os, sys, time

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
mon_dir = os.path.join(current_dir, 'mon')
# Aggiungi monitoring al path
sys.path.insert(0, mon_dir)

import mon.setup as setup
import mon.monitoring as monitoring
import server.request as request



def start_server():
    # Avvia il server in un processo separato
    server_path = os.path.join(os.path.dirname(__file__), 'server', 'server.py')
    subprocess.Popen(["python", server_path])

if __name__ == "__main__":
    start_server()
    time.sleep(10)
    response = setup.setup()
    print(response)
    if response == "y":
        request.update_hosts()
    monitoring.start_monitoring()
