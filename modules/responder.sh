#!/bin/bash
# Dependencies: responder
# Silent: true
# Logfile: /opt/pi-turtle/logs/responder.log

echo "Responder script started"
responder -I wlan0 -wd | tee -a /opt/pi-turtle/logs/responder.log
