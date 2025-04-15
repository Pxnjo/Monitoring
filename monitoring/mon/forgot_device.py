import json, os

# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Costruisci il percorso del file hosts.json nella cartella 'mon'
hosts_path = os.path.join(current_dir, 'hosts.json')

def forgot_device():
    with open(hosts_path, 'r') as f:
        data = json.load(f)
    
    hosts = data.get('hosts', {})
    forgot = data.get('forgot', {})

    if not hosts:
        print("Nessun dispositivo presente in 'hosts'.")
        return

    print(f"Current devices: {hosts.keys()}")
    hostname  = input("Enter the hostname of the device you want to remove: ")

    while hostname  not in hosts:
        print("Hostname not found.")
        hostname  = input("Enter the hostname of the device you want to remove: ")

    # Sposta l'host da "hosts" a "forgot"
    ip = hosts.pop(hostname)
    forgot[hostname] = ip

    # Aggiorna i campi nel dizionario originale
    data['hosts'] = hosts
    data['forgot'] = forgot

    # Salviamo tutto il dizionario originale con la nuova chiave
    with open(hosts_path, 'w') as f:
        json.dump(data, f, indent=4)

forgot_device()