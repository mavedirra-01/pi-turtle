#!/bin/bash

# Define file paths for temporary storage and configuration
IP_INFO_TEMP="/tmp/ip_info.txt"
NETWORK_CONFIG="/etc/network/interfaces"  # Example path, adjust as needed

# Function to display network information
show_network_info() {
    ip addr show > "$IP_INFO_TEMP"
    dialog --title "Network Information" --textbox "$IP_INFO_TEMP" 20 80
}

# Function to configure network settings (example function)
configure_network() {
    # Example: Set static IP address
    dialog --title "Configure Network" --form "\nEnter the static IP configuration" 15 50 0 \
    "IP Address:" 1 1 "" 1 15 15 0 \
    "Subnet Mask:" 2 1 "" 2 15 15 0 \
    "Gateway:" 3 1 "" 3 15 15 0 \
    2> "$IP_INFO_TEMP"

    if [ $? -eq 0 ]; then
        read -r ip_addr subnet gateway < "$IP_INFO_TEMP"
        # Here, you'd add logic to apply these settings to $NETWORK_CONFIG
        echo "IP Address: $ip_addr"
        echo "Subnet Mask: $subnet"
        echo "Gateway: $gateway"
        # Apply changes here
    fi
}

# Main menu integration
while true; do
    exec 3>&1
    SELECTION=$(dialog --clear --menu "Network Module" 15 50 2 \
    1 "Show Network Information" \
    2 "Configure Network" \
    2>&1 1>&3)
    exit_status=$?
    exec 3>&-

    case $exit_status in
        1 | 255) break ;;
    esac

    case $SELECTION in
        1) show_network_info ;;
        2) configure_network ;;
        *) dialog --title "Error" --msgbox "Invalid option. Please try again." 5 40 ;;
    esac
done

# Clean up
[ -f "$IP_INFO_TEMP" ] && rm "$IP_INFO_TEMP"
