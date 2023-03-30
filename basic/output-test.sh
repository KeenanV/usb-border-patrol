#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [ $# -eq 1 ]; then
    if [ "$1" = "id" ]; then
		echo "${YELLOW}"
		figlet "INPUT DEV." -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c
		echo "${GREEN}"
		figlet "BLOCKED" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c
    fi
else
	ff="${HOME}/tmp/gb-tmp.txt"
	good1=$(sed -n '1p' "$ff")
	bad1=$(sed -n '2p' "$ff")
	good2=$(sed -n '3p' "$ff")
	bad2=$(sed -n '4p' "$ff")

	good=$(($good1 + $good2))
	bad=$(($bad1 + $bad2))

	echo "${GREEN}"
	figlet "GOOD: ${good}" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 

	echo "${RED}"
	figlet "BAD: ${bad}" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 

	echo "${YELLOW}"
	figlet "SUS: 0" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 
fi

echo "${NC}"

