import os, sys, subprocess
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)
monitoring_dir = os.path.dirname(server_dir)
sys.path.insert(0, monitoring_dir)
from config import this_machine_ip

def command_build(openssl_command):
    result = subprocess.run(
                openssl_command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
    return result

def certificati():
    # file_CA_richiesti = ["ca.crt", "ca.key"]
    file_server_richiesti = ["server.crt", "server.key"]

    # CA_mancanti = [file for file in file_CA_richiesti if not os.path.isfile(os.path.join(current_dir, file))]
    file_server_mancanti = [file for file in file_server_richiesti if not os.path.isfile(os.path.join(current_dir, file))]

    # if not CA_mancanti:
    #     print("Tutti i certificati della CA sono presenti.")
    if not file_server_mancanti:
        print("Sono gia presenti dei certificati per il server.")
        return True
    else:
        print(f"Creazione Certificati server mancanti:", file_server_mancanti)

        server_key = f"openssl genrsa -out {current_dir}/server.key 2048"
        result =command_build(server_key)

        if result.returncode == 0:
            print("Chiave privata del Server generata con successo.")

            server_sign_request = f'openssl req -new -key {current_dir}/server.key -out {current_dir}/server.csr -subj "/C=IT/ST=Veneto/L=Treviso/O=Pxnjo/CN={this_machine_ip}"'
            result =command_build(server_sign_request)

            if result.returncode == 0:
                print("Richiesta firma del Server generata con successo.")
                print(f"L'ip di questa macchina è {this_machine_ip}")

                conf_ext_file = f""" 
                    authorityKeyIdentifier=keyid,issuer
                    basicConstraints=CA:FALSE
                    keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
                    subjectAltName = @alt_names

                    [alt_names]
                    IP.1 = {this_machine_ip}
                    IP.2 = 127.0.0.1
                """
                print(f"Il file extension è {conf_ext_file}")
                ext_file_path = f"{current_dir}/server.ext"
                with open(ext_file_path, 'w') as f:
                    f.write(conf_ext_file)
                # Dopo che il file è stato scritto, puoi eseguire il comando openssl
                crea_ext_file = f"openssl x509 -req -in {current_dir}/server.csr -CA {current_dir}/ca.crt -CAkey {current_dir}/ca.key -CAcreateserial -out {current_dir}/server.crt -days 825 -sha256 -extfile {ext_file_path}"
                result =command_build(crea_ext_file)
                if result.returncode == 0:
                    print("Certificato del Server firmato con successo.")
                    return True
                else:
                    print(f"Errore nella firma della chiave del server: {result.stderr}")
                    return False            
            else:
                print(f"Errore nella richiesta firma della chiave del server: {result.stderr}")
                return False
        else:
            print(f"Errore nella creazione della chiave del server: {result.stderr}")
            return False
            
    # else:
    #     print(f"Certificati della CA mancanti:", CA_mancanti)
    #     crea_ca_key = f"openssl genrsa -out {current_dir}/ca.key 4096"
    #     result =command_build(crea_ca_key)
    #     if result.returncode == 0:
    #         print("Chiave privata della CA generata con successo.")
    #         crea_ca_crt = f'openssl req -x509 -new -nodes -key {current_dir}/ca.key -sha256 -days 3650 -out {current_dir}/ca.crt -subj "/C=IT/ST=Veneto/L=Treviso/O=Pxnjo/CN=Pxnjo Monitoring CA"'
    #         result =command_build(crea_ca_crt)
    #         # Verifica se ci sono errori nell'esecuzione
    #         if result.returncode == 0:
    #             print("Certificato della CA generata con successo.")
    #             certificati()
    #         else:
    #             print(f"Errore nella creazione del Certificato: {result.stderr}")
    #     else:
    #         print(f"Errore nella creazione della chiave della CA: {result.stderr}")
