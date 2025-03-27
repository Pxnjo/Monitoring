from ping3 import ping
import threading
import signal
import json, time

class Check:
    def __init__(self, hosts, ip):
        self.hosts = hosts
        self.ip = ip
    
    def ping(self):
        result = ping(self.ip, timeout=2)
        print(f"{self.hosts} ({self.ip}): {'Raggiungibile ✅' if result is not None else 'Non raggiungibile ❌'}")

def monitor_host(host, ip):
    while not stop_event.is_set():
        try:
            check = Check(host, ip)
            check.ping()
            time.sleep(5)
        except Exception as e:
            print(f"{host} ({ip}): Errore durante il ping - {e}")
            time.sleep(5)

def load_hosts():
    with open('hosts.json', 'r') as f:
        return json.load(f)['hosts']
    
def start_monitoring():
    signal.signal(signal.SIGINT, stop_monitoring)
    hosts = load_hosts()
    threads = []

    for host, ip in hosts.items():
        thread = threading.Thread(
            target = monitor_host,
            args = (host, ip),
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    for thread in threads:
        thread.join()
    print("Monitoraggio terminato.")

stop_event = threading.Event()
def stop_monitoring(sig, frame):
    print("\nInterruzione rilevata. Chiusura in corso...")
    stop_event.set()

if __name__ == "__main__":
    start_monitoring()