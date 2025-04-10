from flask import Flask, request, jsonify
import json, os, sys

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
print(parent_dir)
sys.path.insert(0, parent_dir)
from config import create_totp
#Entra nella directory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory mon al path
sys.path.insert(0, mon_dir)
hosts_path = os.path.join(mon_dir, 'hosts.json')
# Aggiungi la directory ssl al path
ssl_folder = os.path.join(os.path.dirname(__file__), 'ssl')
certfile = os.path.join(ssl_folder, 'server.crt')
keyfile = os.path.join(ssl_folder, 'server.key')



app = Flask(__name__)

#Server API waiting for json request
@app.route('/api/hosts', methods=['POST'])
def get_hosts():
    try:
        # Verifica se il contenuto è JSON
        if not request.is_json:
            return jsonify({'error': 'La richiesta non è in formato JSON'}), 400

        # Estrai il corpo JSON
        data = request.get_json()
        code = create_totp()
         # Verifica che il corpo JSON contenga il codice
        if 'auth' not in data:
            return jsonify({'error': 'Codice non trovato nel body della richiesta'}), 400

        elif data['auth'] != code:
            return jsonify({' error': 'Codice non valido', 'codice_atteso': code}), 403
        else:
            # Ottieni l'indirizzo IP del client dalla richiesta
            # Se il server è dietro un proxy, usa 'X-Forwarded-For' per ottenere l'IP originale
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
            app.logger.info(f"[{request.method}] {request.url} from {client_ip}")

            # Leggi il file JSON
            with open(hosts_path, 'r') as f:
                data = json.load(f)

            hosts = data.get('hosts', {})
            this_device_ip = data.get('this_device_ip', {})
            forgot = data.get('forgot', {})

            # Aggiungi i componenti di this_device_ip a hosts
            hosts.update(this_device_ip)
            send = {'hosts': hosts, 'forgot': forgot}

            return jsonify(send), 200

    except Exception as e:
        app.logger.error(f"Errore nel gestire la richiesta: {str(e)}")
        return jsonify({'error': str(e)}), 500

def run_server():
    app.run(
        host='0.0.0.0', 
        port=5000, 
        ssl_context=(certfile, keyfile)
    )

if __name__ == '__main__':
    run_server()