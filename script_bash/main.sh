#!/bin/bash

# Leggi ogni riga del file devices.txt
while IFS='=' read -r hostname ip; do

        while true; do
            ping -c 1 -i 2 "$ip" &> /dev/null
            if [ $? -eq 0 ]; then
                echo "$hostname ($ip) is reachable."
            else
                echo "$hostname ($ip) is not reachable."
            fi
            sleep 1  # Aggiunge un intervallo tra i ping (opzionale)
        done $


done < "devices.txt"
wait