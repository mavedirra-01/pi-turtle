#!/bin/bash

# Configuration file path
CONFIG_FILE="/etc/pi-turtle/nmap_config.conf"
LOG_DIR="/var/log/pi-turtle/nmap"
DATE=$(date +"%Y-%m-%d_%H-%M")

# Ensure configuration and log directories exist
mkdir -p "$(dirname "$CONFIG_FILE")"
mkdir -p "$LOG_DIR"

# Function to read configuration
read_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        touch "$CONFIG_FILE"
    fi
}

# Function to write configuration
write_config() {
    echo "nmap_target='$nmap_target'" > "$CONFIG_FILE"
    echo "nmap_profile='$nmap_profile'" >> "$CONFIG_FILE"
    echo "nmap_log='$LOG_DIR'" >> "$CONFIG_FILE"
}

# Function to start scanning
start_scan() {
    read_config
    if [ -z "$nmap_target" ] || [ -z "$nmap_profile" ]; then
        echo "nmap module missing configuration"
        exit
    fi

    # Define profiles
    case $nmap_profile in
        1) PROFILE="-T4 -A -v";;
        # Add other profiles here
    esac

    echo "Executing: nmap $PROFILE $nmap_target > $nmap_log/nmap_$DATE.log"
    nmap $PROFILE $nmap_target > "$nmap_log/nmap_$DATE.log" 2>&1 &
}

# Function to configure target
configure_target() {
    read_config
    echo "Enter target network (e.g., 192.168.1.0/24):"
    read -r nmap_target
    write_config
}

# Function to configure profile
configure_profile() {
    read_config
    echo "Select Scan Profile:"
    echo "1) Intense scan"
    # Add other profiles here
    read -r nmap_profile
    write_config
}

# Main Menu Integration
while true; do
    echo "1) Configure Target"
    echo "2) Configure Profile"
    echo "3) Start Scan"
    echo "4) Exit"
    read -r choice

    case $choice in
        1) configure_target ;;
        2) configure_profile ;;
        3) start_scan ;;
        4) break ;;
        *) echo "Invalid option";;
    esac
done
