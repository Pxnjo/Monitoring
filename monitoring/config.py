this_machine_hostname = "monitor1" # hostname della macchina corrente
this_machine_ip = "10.20.86.13" # ip della macchina corrente
hostname = "monitor2" # hostname della prima macchina da monitorare 
ip = "10.20.86.14" # ip della prima macchina da monitorare

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