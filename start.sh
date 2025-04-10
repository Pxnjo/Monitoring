#!/bin/bash
tmux new-session -d -s monitor 'python3 /monitoring/main.py'

tail -f /dev/null # Serve a non far pegnere subito il docker
