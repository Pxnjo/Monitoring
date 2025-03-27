from flask import Flask, request, jsonify
import json, os, sys

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
#Entra nella directory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory parent al path
sys.path.insert(0, mon_dir)

hosts_path = os.path.join(mon_dir, 'hosts.json')


app = Flask(__name__)

#Server API waiting for json request
@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    try:
        with open(hosts_path, 'r') as f:
            hosts = json.load(f)
        return jsonify(hosts), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    run_server()