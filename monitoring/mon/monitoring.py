from ping3 import ping
import threading
import json, time, os
# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ottieni il path della cartella logs
log_dir = os.path.join(current_dir, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
# Ottieni il path della cartella utils
utils_dir = os.path.join(current_dir, '..', 'utils')
from utils.logger import setup_logger
# Costruisci il percorso del file hosts.json nella cartella 'mon'
hosts_path = os.path.join(current_dir, 'hosts.json')

stop_event = threading.Event()
monitoring_threads = {}  # Dizionario per tracciare i thread per ciascun host
file_monitor_thread = None  # Thread per il monitoraggio del file

logger = setup_logger("monitor_logger", os.path.join(log_dir, "monitor.log"))

class Check:
    def __init__(self, hosts, ip):
        self.hosts = hosts
        self.ip = ip
    
    def ping(self):
        result = ping(self.ip, timeout=2)
        if result is not None:
            pass
            print(f"{self.hosts} ({self.ip}): Raggiungibile ✅")
        else:
            logger.error(f"{self.hosts} ({self.ip}): Non raggiungibile ❌")

def monitor_host(host, ip, thread_stop_event):
    """
    Funzione per monitorare un singolo host.
    
    Args:
        host: Nome dell'host da monitorare
        ip: Indirizzo IP dell'host
        thread_stop_event: Evento individuale per fermare questo specifico thread
    """
    # print(f"[{threading.current_thread().name}] Avviato monitoraggio di {host} ({ip})")
    while not thread_stop_event.is_set() and not stop_event.is_set():
        try:
            # print(f"[{threading.current_thread().name}] Controllo ping per {host} ({ip})") 
            check = Check(host, ip)
            check.ping()
            # Controlliamo lo stato dell'evento ogni secondo per una risposta più rapida
            for _ in range(5):
                if thread_stop_event.is_set() or stop_event.is_set():
                    break
                time.sleep(1)
        except Exception as e:
            print(f"{host} ({ip}): Errore durante il ping - {e}")
            time.sleep(1)
    # print(f"[{threading.current_thread().name}] Fermato.")

def monitor_file_changes():
    # Monitora il file hosts.json per cambiamenti e ricarica gli host se necessario.
    # print("[Watcher] Avviato controllo file hosts.json")

    try:
        last_modified_time = os.path.getmtime(hosts_path)
        # print(f"[DEBUG] Ultima modifica file: {last_modified_time}")
    except FileNotFoundError:
        print(f"File {hosts_path} non trovato. Verrà creato quando si aggiungeranno host.")
        last_modified_time = 0

    while not stop_event.is_set():
        try:
            # print("[Watcher] Controllo modifiche...")
            if os.path.exists(hosts_path):
                current_modified_time = os.path.getmtime(hosts_path)
                # print(f"[DEBUG] Tempo di modifica corrente: {current_modified_time}")
                if current_modified_time != last_modified_time:
                    # print("File modificato, ricarico gli host...")
                    last_modified_time = current_modified_time
                    update_hosts()
            else:
                print(f"[DEBUG] File {hosts_path} non trovato durante il monitoraggio.")
        except Exception as e:
            print(f"[ERROR] Errore nel controllo modifiche: {e}")
        time.sleep(1)  # Controlla ogni secondo se il file è stato modificato

def load_hosts():
    # Carica gli host dal file JSON
    try:
        with open(hosts_path, 'r') as f:
            return json.load(f)['hosts']
    except FileNotFoundError:
        print(f"File {hosts_path} non trovato.")
        return {}
    except Exception as e:
        print(f"Errore durante il caricamento dei dispositivi: {e}")
        return {}

def update_hosts():
    """Ricarica gli host dal file e aggiorna la lista degli host da monitorare."""
    global monitoring_threads
    # print("[DEBUG] Ricaricando gli host...")
    new_hosts = load_hosts()
    # print(f"[DEBUG] Host trovati: {new_hosts}")  # Log degli host trovati
    
    if not new_hosts:
        # print("Nessun dispositivo trovato nel file hosts.json")
        # Fermiamo tutti i thread attivi se non ci sono host
        stop_all_monitoring_threads()
        return

    # 1. Identifica host rimossi e ferma i relativi thread
    hosts_to_stop = []
    for host in list(monitoring_threads.keys()):
        if host not in new_hosts:
            hosts_to_stop.append(host)
    
    # Ferma i thread per gli host rimossi
    for host in hosts_to_stop:
        # print(f"Host {host} rimosso, fermo il thread di monitoraggio")
        thread_info = monitoring_threads.pop(host)
        thread_info["stop_event"].set()  # Segnala al thread di fermarsi
        
        # Attendi che il thread termini (con timeout)
        thread = thread_info["thread"]
        if thread.is_alive():
            # print(f"Aspettando la terminazione di {thread.name}...")
            thread.join(timeout=2)  # Attendiamo al massimo 2 secondi
            if thread.is_alive():
                print(f"Avviso: {thread.name} non si è fermato in tempo")
    
    # 2. Avvia thread per i nuovi host
    for host, ip in new_hosts.items():
        # Se l'host è già monitorato e l'IP è lo stesso, non fare nulla
        if host in monitoring_threads and monitoring_threads[host]["ip"] == ip:
            # print(f"Host {host} ({ip}) già monitorato, continuo")
            continue
        
        # Se l'host è già monitorato ma l'IP è cambiato, ferma il vecchio thread
        if host in monitoring_threads:
            # print(f"IP dell'host {host} cambiato, aggiorno il thread")
            thread_info = monitoring_threads.pop(host)
            thread_info["stop_event"].set()
            thread = thread_info["thread"]
            if thread.is_alive():
                thread.join(timeout=2)
        
        # Crea un nuovo thread per l'host
        # print(f"[DEBUG] Avvio thread per {host} ({ip})")
        thread_stop_event = threading.Event()
        thread = threading.Thread(
            target=monitor_host,
            args=(host, ip, thread_stop_event),
            name=f"Monitor-{host}"
        )
        thread.daemon = True
        thread.start()
        
        # Salva le informazioni del thread nel dizionario
        monitoring_threads[host] = {
            "thread": thread,
            "stop_event": thread_stop_event,
            "ip": ip
        }
    
    # Debug: mostra i thread attivi
    # print("[DEBUG] Thread attivi dopo l'update:")
    # for t in threading.enumerate():
        # print(f" - {t.name}")

def stop_all_monitoring_threads():
    """Ferma tutti i thread di monitoraggio."""
    global monitoring_threads
    
    for host, thread_info in monitoring_threads.items():
        # print(f"Fermando il monitoraggio di {host}")
        thread_info["stop_event"].set()
        
    # Attendi che tutti i thread terminino (con timeout)
    for host, thread_info in list(monitoring_threads.items()):
        thread = thread_info["thread"]
        if thread.is_alive():
            thread.join(timeout=2)
        monitoring_threads.pop(host)

def start_monitoring(hosts=None):
    """Avvia il monitoraggio degli host specificati."""
    # print("[DEBUG] Thread attivi:")
    # for t in threading.enumerate():
        # print(" -", t.name)
    
    global file_monitor_thread
    
    if hosts is None:
        hosts = load_hosts()  # Carica gli host dal file
        if not hosts:
            # print("Nessun host da monitorare trovato.")
            return
    
    # Avvia la gestione degli host
    update_hosts()
    
    # Avvia il thread per monitorare le modifiche al file hosts.json se non è già in esecuzione
    if file_monitor_thread is None or not file_monitor_thread.is_alive():
        file_monitor_thread = threading.Thread(
            target=monitor_file_changes,
            name="FileMonitor"
        )
        file_monitor_thread.daemon = True
        file_monitor_thread.start()

def stop_monitoring(sig, frame):
    """Ferma tutti i thread di monitoraggio."""
    # print("\nInterruzione rilevata. Chiusura in corso...")
    stop_event.set()
    
    # Ferma tutti i thread di monitoraggio
    stop_all_monitoring_threads()
    
    if file_monitor_thread and file_monitor_thread.is_alive():
        file_monitor_thread.join(timeout=1)
    
    # print("Monitoraggio terminato.")