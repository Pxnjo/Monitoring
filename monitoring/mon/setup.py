import re, json, os, sys
# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
hosts_path = os.path.join(current_dir, 'hosts.json')

# Risali di una directory
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import this_machine_hostname, this_machine_ip, hostname, ip

def get_json():
    global data
    global monitoring_hostnames
    try:
        if os.path.exists(hosts_path) and os.path.getsize(hosts_path) > 0:
            with open(hosts_path, 'r') as f:
                data = json.load(f)

                # Se il JSON è valido ma manca la struttura corretta
                if not isinstance(data, dict) or 'hosts' not in data or 'this_device_ip' not in data:
                    raise ValueError  # Simula un errore per attivare l'except
        else:
            raise FileNotFoundError  # Se il file è vuoto, trattalo come inesistente

    # Se il file non esiste o è corrotto, inizializzalo    
    except (json.JSONDecodeError, FileNotFoundError, ValueError):
        data = {"this_device_ip":{},"hosts": {}}
        with open(hosts_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    monitoring_hostnames = list(data['hosts'].keys())

def update_json(hostname = None, ip = None, this_machine_hostname = None, this_machine_ip = None):
    if hostname and ip:
        data['hosts'][hostname] = ip
    elif this_machine_hostname and this_machine_ip:
        data['this_device_ip'] = {this_machine_hostname: this_machine_ip}

    with open(hosts_path, 'w') as f:
        json.dump(data, f, indent=4)

#________________________________________________________________________________________________________________________#

def setup():
    global hostname, ip
    global this_machine_hostname, this_machine_ip
    get_json()
    if this_machine_hostname in data['this_device_ip'].keys():
        pass
    else:
        verify_ip(this_machine_ip)
        update_json(None, None, this_machine_hostname, this_machine_ip)
    if hostname in monitoring_hostnames:
        pass
    else:
        verify_ip(ip)
        update_json(hostname, ip, None, None)


def verify_ip(ip = None):
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"

    if re.match(pattern, ip):
        ottetti = ip.split(".")
        if all(0 <= int(octeto) <= 255 for octeto in ottetti ):
            print("Ip address valid.")
            return True
        else:
            print("Ip address not valid, out of range.")
            return
    else:
        print("Ip address not valid.")
        return