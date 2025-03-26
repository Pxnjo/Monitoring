#!/bin/bash

# Leggi ogni riga del file devices.txt
while IFS='=' read -r hostname ip; do
    
    # Fai il ping e salva il risultato
    ping -W 2 "$ip" &>/dev/null
    
    # Controlla il risultato del ping
    if [ $? -eq 0 ]; then
        echo "$hostname ($ip) is reachable."
    else
        echo "$hostname ($ip) is not reachable."
    fi
done < "devices.txt"