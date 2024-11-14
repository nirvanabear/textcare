#!/bin/bash

CLIENT_IP=$(curl ifconfig.me)
# Requires extra empty string for MacOS
sed -i '' "s/client_IP = .*/client_IP = '${CLIENT_IP}\/32'/g" boot_script.py

## TODO ## 
    #◊ needs to create blank string if current IP is my regular IP
	#◊ also needs to delete new rules once the VPN session is no longer needed