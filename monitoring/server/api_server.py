from flask import Flask, request, jsonify
import json, os, sys
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
print(parent_dir)
sys.path.insert(0, parent_dir)
from config import create_totp
# Ottieni il path della cartella logs
log_dir = os.path.join(current_dir, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
# Ottieni il path della cartella utils
utils_dir = os.path.join(current_dir, '..', 'utils')
from utils.logger import setup_logger
#Entra nella directory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory mon al path
sys.path.insert(0, mon_dir)
hosts_path = os.path.join(mon_dir, 'hosts.json')
# Aggiungi la directory ssl al path
ssl_folder = os.path.join(os.path.dirname(__file__), 'ssl')
certfile = os.path.join(ssl_folder, 'server.crt')
keyfile = os.path.join(ssl_folder, 'server.key')

logger = setup_logger("server_logger", os.path.join(log_dir, "api_server.log"))
index_to_forgot = 0

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

app = Flask(__name__)
#Server API waiting for json request
@app.route('/api/hosts', methods=['POST'])
def get_hosts():
    global index_to_forgot
    try:
        # Verifica se il contenuto è JSON
        if not request.is_json:
            logger.error({'error': 'La richiesta non è in formato JSON'})
            return jsonify({'error': 'La richiesta non è in formato JSON'}), 400

        # Estrai il corpo JSON
        requests_data = request.get_json()
        code = create_totp()
         # Verifica che il corpo JSON contenga il codice
        if 'auth' not in requests_data:
            logger.error({'error': 'Codice non trovato nel body della richiesta'})
            return jsonify({'error': 'Codice non trovato nel body della richiesta'}), 400

        elif requests_data['auth'] != code:
            logger.error({' error': 'Codice non valido'})
            return jsonify({' error': 'Codice non valido'}), 403
        else:
            # Leggi il file JSON
            data = manage_file(hosts_path, 'r')

            hosts = data.get('hosts', {})
            this_device_ip = data.get('this_device_ip', {})
            forgot = data.get('forgot', {})
            copy_of_forgot = data.get('copy_of_forgot', {})
            unknown_hosts = data.get('unknown_hosts', [])
            synced_hosts = data.get('synced_hosts', {})
            flask_not_responding = data.get('flask_not_responding', {})

            # Ottieni l'indirizzo IP del client dalla richiesta
            # Se il server è dietro un proxy, usa 'X-Forwarded-For' per ottenere l'IP originale
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
            logger.info(f"[server] Ricevuta richiesta: [{request.method}] from {client_ip}")

            # Se l'ip non è riconosciuto viene salvato temporaneamente
            if client_ip not in hosts.values() and client_ip not in unknown_hosts:
                unknown_hosts.append(client_ip)
                data['unknown_hosts'] = unknown_hosts

                # Salva l'host sconosciuto
                manage_file(hosts_path, 'w', data)
                logger.info(f" [server] Ricevuta richiesta da {data['unknown_hosts']}")
            else:
                # Se l'ip viene riconosciuto
                if forgot:
                    # Confronta i 2 dizionari e restituisce True se è cambiato
                    changed_forgot = copy_of_forgot != forgot

                    # Crea synced_hosts solo se i server rispondono
                    if changed_forgot or not synced_hosts:
                        data['copy_of_forgot'] = forgot
                        synced_hosts = {hostname: False for hostname in hosts if hostname not in flask_not_responding}
                        data['synced_hosts'] = synced_hosts
                        manage_file(hosts_path, 'w', data)

                    # Prendi l'hostname del IP da cui hai ricevuto la richiesta
                    hostname = next((host for host, ip in hosts.items() if ip == client_ip), None)
                    if hostname:
                        # Setta True sul host a cui ha mandato il json aggiornato
                        synced_hosts[hostname] = True
                        data['synced_hosts'] = synced_hosts
                        manage_file(hosts_path, 'w', data)

                    # Se tutti i valori sono True svuota la lista
                    if all(synced_hosts.values()):
                        data['synced_hosts'] = {}
                        data['forgot'] = {}
                        data['copy_of_forgot'] = {}
                        manage_file(hosts_path, 'w', data)

            # Aggiungi i componenti di this_device_ip a hosts
            hosts.update(this_device_ip)
            # Invia gli hosts e quelli da dimenticare
            send = {'hosts': hosts, 'forgot': forgot}

            return jsonify(send), 200

    except Exception as e:
        logger.error(f" [server] Errore nel gestire la richiesta: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_server():
    app.run(
        host='0.0.0.0', 
        port=5000, 
        ssl_context=(certfile, keyfile)
    )

if __name__ == '__main__':
    run_server()