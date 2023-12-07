#!/bin/bash
# Dependencies: feroxbuster, gedit
# Inputs: url, extentions
# Help: extentions - Options are 'txt, php, py, etc'
url=$1
extentions=$2

feroxbuster --url $url -x $extentions -w /opt/pi-turtle/wordlists/words.txt