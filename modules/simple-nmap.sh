#!/bin/bash
# Dependencies: nmap
# Inputs: target, scan_type
# Help: scan_type - Options are 'Quick Scan' or 'Intense Scan'

# Read arguments
target=$1
scan_type=$2

# Perform nmap scan based on the provided scan type
case $scan_type in
    "Quick Scan") nmap -T4 -F $target ;;
    "Intense Scan") nmap -T4 -A $target ;;
    *) echo "Invalid scan type"; exit 1 ;;
esac
