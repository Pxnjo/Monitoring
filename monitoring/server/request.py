import requests, json, os , sys

# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
#Entra nella directory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory parent al path
sys.path.insert(0, mon_dir)

hosts_path = os.path.join(mon_dir, 'hosts.json')

#funziona ma sovrascrive il file hosts.json

with open(hosts_path, 'r') as f:
    hosts = json.load(f)['hosts']

def update_hosts():
    ip_addresses = list(hosts.values())
    SERVER_URL = f'http://{ip_addresses[0]}:5000' # Prendo il server di destinazone dal primo IP dopo aver inizializzato lo script

    response = requests.get(f'{SERVER_URL}/api/hosts')
    print(response.json())
    if response.status_code == 200:
        data = response.json()['hosts']
        hosts.update(data)
        with open(hosts_path, 'w') as f:
            json.dump({'hosts': hosts}, f, indent=4)
    
update_hosts()