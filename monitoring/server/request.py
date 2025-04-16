import requests, json, os , sys, threading
import time
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ottieni il path della cartella logs
log_dir = os.path.join(current_dir, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
# Ottieni il path della cartella utils
utils_dir = os.path.join(current_dir, '..', 'utils')
from utils.logger import setup_logger
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

logger = setup_logger("requests_logger", os.path.join(log_dir, "requests.log"))

#Funzione per gestire il file
def manage_file(path, mode, data = None):
    if mode == 'w':
        with open(path, mode) as f:
            json.dump(data, f, indent=4)
            return None
    elif mode == 'r':
        with open(path, mode) as f:
            data = json.load(f)
            return data

def server_flask_not_responding(ip_addresses):
    data = manage_file(hosts_path, 'r')
    hosts = data.get('hosts', {})
    synced_hosts = data.get('synced_hosts', {})
    flask_not_responding = data.get('flask_not_responding', {})
    if synced_hosts:
        hostname = next((host for host, ip in hosts.items() if ip == ip_addresses), None) # Mi trovo il nome corrispondente al ip
        if hostname:
            ip = hosts.get(hostname)
            synced_hosts.pop(hostname, None) # Salva l'ip in base al hostname
            flask_not_responding[hostname] = ip # Salva Hostname e ip

            data['synced_hosts'] = synced_hosts
            data['flask_not_responding'] = flask_not_responding

            manage_file(hosts_path, 'w', data)

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
        logger.info(f"[REQUEST] Sending request to {SERVER_URL}")
        # print(f"[RESPONSE] Status: {response.status_code}, Body: {response.text}")
        # print("Nuovo file hosts.json:",response.json())

        if response.status_code == 200:
            # Dizionari Ricevuti
            data = response.json()['hosts']
            income_forgot = response.json().get('forgot', {})
            # print(f"Ricevuto dict forgot: {income_forgot}")

            # Dizionari locali
            local_hosts_data = manage_file(hosts_path, 'r') # Tutto il file hosts
            local_to_forgot = local_hosts_data.get('forgot', {})
            flask_not_responding = local_hosts_data.get('flask_not_responding', {})

            # Se ci sono host che prima non rispondevano, toglierli siccome hanno risposto
            if flask_not_responding:
                # Crea una lista degli host da rimuovere
                to_remove = []
                for host, ip in flask_not_responding.items():
                    # Se l'host è stato cancellato o la connessione è riuscita elimina da flask_not_responding
                    if host not in hosts or ip == ip_addresses:
                        to_remove.append(host)

                # Rimuovi gli host raccolti
                for host in to_remove:
                    flask_not_responding.pop(host, None)

                # Se ci sono stati cambiamenti, aggiorna il file
                if to_remove:
                    data['flask_not_responding'] = flask_not_responding
                    manage_file(hosts_path, 'w', data)

            combined_forgot = {**local_to_forgot, **income_forgot}
            # print(f"Uniti dict forgot: {income_forgot}")

            # Aggiorno 'forgot'
            local_hosts_data['forgot'] = combined_forgot
            manage_file(hosts_path, 'w', local_hosts_data)
            
            # Aggiorna hosts solo se ci sono nuovi host
            has_changes = False
            for hostname, ip in data.items():
                if hostname not in hosts and hostname not in this_device_ip and hostname not in combined_forgot: # Se l'host non è sè stesso o da eliminare o non è gia presente lo salva
                    hosts[hostname] = ip
                    has_changes = True

            # Rimuovi dal dizionario hosts quelli presenti in combined_forgot
            if combined_forgot:
                for hostname in combined_forgot.keys():
                    if hostname in hosts:
                        del hosts[hostname]
                        has_changes = True

            # Scrivi su file solo se ci sono stati cambiamenti
            if has_changes:
                manage_file(hosts_path, 'w', {'hosts': hosts, 'this_device_ip': this_device_ip})
                logger.info("File hosts.json aggiornato con nuovi host")
            # else:
            #     print("Nessun nuovo host da aggiungere")

    except requests.exceptions.Timeout:
        logger.error(f"Errore: il server {ip_addresses} non ha risposto in tempo utile.")
        server_flask_not_responding(ip_addresses)
    except requests.exceptions.ConnectionError:
        logger.error(f"Errore di connessione: il server {ip_addresses} non e' raggiungibile.")
        server_flask_not_responding(ip_addresses)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Errore HTTP: {http_err}")
        server_flask_not_responding(ip_addresses)
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore nella richiesta: {e}")  # Fallback generico per altri errori
        server_flask_not_responding(ip_addresses)

# funziona ma sovrascrive il file hosts.json
def update_hosts_from_api():
    """Funzione che aggiorna gli host dal server API"""
    try:
        data = manage_file(hosts_path, 'r')

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
            manage_file(hosts_path, 'w', data)

    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento degli host: {e}")

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
            logger.info("[API-Updater] Arresto in corso...")
            self.stop_event.set()
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.error("[API-Updater] Warning: Il thread non si è fermato correttamente")
            else:
                logger.info("[API-Updater] Thread fermato correttamente")
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
    api_updater = APIThread(interval=60)  # Aggiorna ogni 20 secondi
    api_updater.start()
    return api_updater  
