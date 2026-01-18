#!/usr/bin/bash
export PATH="$PATH:$HOME/.local/bin"
LOG_FILE_NAME=$HOME/logs/simulation_$(date +"%F_%H-%M-%S").log
biester_client gruppe03 $HOME/login_daten.txt >$LOG_FILE_NAME 2>&1