#!/bin/sh

width=78
height=$(tput lines)
v_center=$((height / 2 - 8))

fonts_dir=/home/usbbp/figlet-fonts

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

clear

for ii in $(seq 0 $v_center); do
    echo
done

if [ $# -eq 1 ]; then
    if [ "$1" = "id" ]; then
        echo "${YELLOW}"
        figlet "INPUT DEV." -d $fonts_dir -f "ANSI Shadow" -t -c
        echo "${GREEN}"
        figlet "BLOCKED" -d $fonts_dir -f "ANSI Shadow" -t -c

		for ii in $(seq 0 $((v_center - 4))); do
			echo
		done
    fi
else
    ff="/home/usbbp/tmp/gb-tmp.txt"
    good1=$(sed -n '1p' "$ff")
    bad1=$(sed -n '2p' "$ff")
    good2=$(sed -n '3p' "$ff")
    bad2=$(sed -n '4p' "$ff")

    good=$(($good1 + $good2))
    bad=$(($bad1 + $bad2))

    echo "${GREEN}"
    figlet "GOOD: ${good}" -d $fonts_dir -f "ANSI Shadow" -t -c

    echo "${RED}"
    figlet "BAD: ${bad}" -d $fonts_dir -f "ANSI Shadow" -t -c

    echo "${YELLOW}"
    figlet "SUS: 0" -d $fonts_dir -f "ANSI Shadow" -t -c
	
	for ii in $(seq 0 $((v_center - 7))); do
		echo
	done
fi

echo "${NC}"

