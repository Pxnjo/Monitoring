import re, json, os
# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
hosts_path = os.path.join(current_dir, 'hosts.json')

def get_json():
    global data
    global hostnames
    hostnames = ""
    try:
        if os.path.exists(hosts_path) and os.path.getsize(hosts_path) > 0:
            with open(hosts_path, 'r') as f: 
                data = json.load(f)

                # Se il JSON è valido ma manca la struttura corretta
                if not isinstance(data, dict) or 'hosts' not in data:
                    raise ValueError  # Simula un errore per attivare l'except
        else:
            raise FileNotFoundError  # Se il file è vuoto, trattalo come inesistente

    # Se il file non esiste o è corrotto, inizializzalo    
    except (json.JSONDecodeError, FileNotFoundError, ValueError):
        data = {"hosts": {}}

        with open(hosts_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    hostnames = list(data['hosts'].keys())


def update_json(hostname, ip):
    data['hosts'][hostname] = ip

    with open(hosts_path, 'w') as f:
        json.dump(data, f, indent=4)
    
def verify_ip(ip = None):
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if ip is None:
        ip = input("Enter a valid ip address: ")

    if re.match(pattern, ip):
        ottetti = ip.split(".")
        if all(0 <= int(octeto) <= 255 for octeto in ottetti ):
            print("Ip address valid.")
            update_json(hostname, ip)
            return
        else:
            print("Ip address not valid, out of range.")
            return verify_ip()
    else:
        print("Ip address not valid.")
        return verify_ip()

#________________________________________________________________________________________________________________________#

def setup():
    get_json()
    response = input("Is this a new machine? (y/n/q)").lower()

    while response not in ["y", "n", "q"]:
        response = input("Wrong input. (y/n/q)")

    if response == "y":
        return set_new_entry("y")
    if response == "n":
        if hostnames == "":
            print("No hosts found, set one.")
            return set_new_entry("y")
        return "n"
    if response == "q":
        exit()

def set_new_entry(response): #gestisce principalmente if fatto di non trovare host nel caso si risponda "n"
    if response == "y":
        global hostname
        hostname = input("Enter the hostname: ")
        while hostname in hostnames:
            hostname = input("Sorry hostname already exists: ")
        ip = input("Enter the IP address: ")
        verify_ip(ip)
    return "y"


