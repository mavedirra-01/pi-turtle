#!/bin/bash
# Dependencies: nikto
# Inputs: url
# Silent: true
# Logfile: /opt/pi-turtle/logs/test.log
# Follow_log: true

url=$1
nikto -h $url
