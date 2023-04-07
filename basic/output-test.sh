#!/bin/sh

width=78
height=44
v_center=$((height / 2 - 8))

fonts_dir=/home/keenan/Documents/capstone/figlet-fonts

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

tmux new-session -d -x $width -y $height

commands='clear'

for ii in $(seq 0 $v_center); do
    commands="$commands; echo"
done

if [ $# -eq 1 ]; then
    if [ "$1" = "id" ]; then
        commands="$commands; echo \"${YELLOW}\""
        commands="$commands; figlet \"INPUT DEV.\" -d $fonts_dir -f \"ANSI Shadow\" -t -c"
        commands="$commands; echo \"${GREEN}\""
        commands="$commands; figlet \"BLOCKED\" -d $fonts_dir -f \"ANSI Shadow\" -t -c"
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
    figlet "GOOD: ${good}" -d //usbbp/figlet-fonts -f "ANSI Shadow" -t -c

    echo "${RED}"
    figlet "BAD: ${bad}" -d /home/usbbp/figlet-fonts -f "ANSI Shadow" -t -c

    echo "${YELLOW}"
    figlet "SUS: 0" -d /home/usbbp/figlet-fonts -f "ANSI Shadow" -t -c
fi

echo "${NC}"

for ii in $(seq 0 $((v_center - 8))); do
    commands="$commands; echo"
done

tmux send-keys "$commands" C-m
tmux attach

