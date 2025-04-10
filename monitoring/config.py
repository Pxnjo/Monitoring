this_machine_hostname = "win2" # hostname della macchina corrente
this_machine_ip = "10.20.10.10" # ip della macchina corrente
hostname = "deb" # hostname della prima macchina da monitorare 
ip = "20.20.20.20" # ip della prima macchina da monitorare

###################################################################
#__________________________WARNING________________________________#
###################################################################
# NON MODIFICARE QUESTA VARIABILE A MENO CHE NON SIA NECESSARIO
import pyotp
# Genera una chiave segreta base32
# secret = pyotp.random_base32()
# print("Chiave segreta:", secret)

TOTP_KEY = "V52Z3ZGEAGAHWNFY6KT2B44KBVANWMMV"
def create_totp():
    # Crea un oggetto TOTP con la chiave
    totp = pyotp.TOTP(TOTP_KEY, interval=30)
    # Genera un codice TOTP valido ora
    code = totp.now()
    return code

