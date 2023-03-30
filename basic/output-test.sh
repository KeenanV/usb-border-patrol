#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "${GREEN}"
figlet "GOOD: 13" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 

echo "${RED}"
figlet "BAD: 22" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 

echo "${YELLOW}"
figlet "SUS: 5" -d /home/keenan/Documents/capstone/figlet-fonts -f "ANSI Shadow" -t -c 
echo "${NC}"

