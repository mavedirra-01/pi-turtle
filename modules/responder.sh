#!/bin/bash
# Dependencies: responder
# Silent: true
# Logfile: /opt/pi-turtle/logs/responder.log

echo "Responder script started"
sudo responder -I wlan0 -wd
