import requests, json, os , sys, threading, logging
import time

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ottieni il path della cartella logs
log_dir = os.path.join(current_dir, '..', 'logs')
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
#Entra nella directory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory parent al path
sys.path.insert(0, mon_dir)
from config import create_totp
hosts_path = os.path.join(mon_dir, 'hosts.json')
# Aggiungi la directory ssl al path
ssl_folder = os.path.join(os.path.dirname(__file__), 'ssl')
ca_cert_path = os.path.join(ssl_folder, 'ca.crt')

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "requests.log")),
        logging.StreamHandler()  # Mostra anche su console
    ]
)

def api_request(ip_addresses, hosts, this_device_ip):
    try:
        # print(f"Controllo IP: {ip_addresses}")
        SERVER_URL = f'https://{ip_addresses}:5000' # Faccio la richiesta per ogni ip del file hosts
        body = {
            'auth': create_totp()
        }
        response = requests.post(
            f'{SERVER_URL}/api/hosts',
            json=body,
            headers={'Content-Type': 'application/json'},
            verify = ca_cert_path
        )
        # print(f"[REQUEST] Sending request to {SERVER_URL}")
        # print(f"[RESPONSE] Status: {response.status_code}, Body: {response.text}")
        # print("Nuovo file hosts.json:",response.json())

        if response.status_code == 200:
            data = response.json()['hosts']
            forgot = response.json().get('forgot', {})

            # Aggiorna hosts solo se ci sono nuovi host
            has_changes = False
            for hostname, ip in data.items():
                if hostname not in hosts and hostname not in this_device_ip: # Se l'host non è sè stesso o non è gia presente lo salva
                    hosts[hostname] = ip
                    has_changes = True

            # Rimuovi gli host presenti in forgot
            if forgot:
                for hostname in forgot.keys():
                    if hostname in hosts:
                        del hosts[hostname]
                        has_changes = True

            # Scrivi su file solo se ci sono stati cambiamenti
            if has_changes:
                with open(hosts_path, 'w') as f:
                    json.dump({'hosts': hosts, 'this_device_ip': this_device_ip}, f, indent=4)
                logging.error("File hosts.json aggiornato con nuovi host")
            # else:
            #     print("Nessun nuovo host da aggiungere")

    except requests.exceptions.Timeout:
        logging.error("Errore: il server non ha risposto in tempo utile.")
    
    except requests.exceptions.ConnectionError:
        logging.error("Errore di connessione: il server non è raggiungibile.")
    
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Errore HTTP: {http_err}")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nella richiesta: {e}")  # Fallback generico per altri errori

# funziona ma sovrascrive il file hosts.json
def update_hosts_from_api():
    """Funzione che aggiorna gli host dal server API"""
    try:
        with open(hosts_path, 'r') as f:
            data = json.load(f)

        hosts = data.get('hosts', {})
        this_device_ip = data.get('this_device_ip', {})
        unknown_hosts = data.get('unknown_hosts', [])
        # print(f"Vecchio file hosts.json: {hosts}")

        for ip_addresses in hosts.copy().values():
            api_request(ip_addresses, hosts, this_device_ip)

        # print(f"Ricevuta richiesta da {unknown_hosts}, sperando succeda qualcosa")
        if unknown_hosts:
            for ip_addresses in unknown_hosts:
                api_request(ip_addresses, hosts, this_device_ip)

            # Dopo averli usati, svuota la lista nel file
            data['unknown_hosts'] = []
            with open(hosts_path, 'w') as f:
                json.dump(data, f, indent=4)

    except Exception as e:
        logging.error(f"Errore durante l'aggiornamento degli host: {e}")

class APIThread:
    def __init__(self, interval=60):
        """
        Inizializza un thread per l'aggiornamento periodico degli host.
        Args:
            interval: Intervallo in secondi tra le richieste API (default: 60 secondi)
        """
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        """" Avvia il thread per l'aggiornamento api """
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(
                target=self._run_periodic_update,
                name="API-Updater",
                daemon=True
            )
            self.thread.start()
            # print(f"[API-Updater] Thread avviato, aggiornamento ogni {self.interval} secondi")
            return True
        return False

    def stop(self):
        """ Ferma il thread aggiornamento """

        if self.thread and self.thread.is_alive():
            print("[API-Updater] Arresto in corso...")
            self.stop_event.set()
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                print("[API-Updater] Warning: Il thread non si è fermato correttamente")
            else:
                print("[API-Updater] Thread fermato correttamente")
                self.thread = None

    def _run_periodic_update(self):
        """Funzione principale del thread che esegue gli aggiornamenti periodici."""
        while not self.stop_event.is_set():

            # print("[API-Updater] Esecuzione aggiornamento hosts da API")
            update_hosts_from_api()

            # Attendi per l'intervallo specificato, controllando periodicamente se fermarsi
            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

# Esempio di utilizzo:
def main():
    api_updater = APIThread(interval=20)  # Aggiorna ogni 60 secondi
    api_updater.start()
    return api_updater  
