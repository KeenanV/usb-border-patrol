#!/bin/bash

sudo rm /home/usbbp/tmp/*
sudo rm -r /home/usbbp/usb-border-patrol/basic/malicious/*

usage=$(cat << EOF
Usage: ./reset.sh <1-4>
    1: main demo
    2: zip bomb demo
    3: clamav demo
    4: input device demo
EOF
)

if [ $# -ne 1 ]; then
	echo "$usage"
	exit 1
fi

if [ -d "/media/untrusted" ] && [ -d "/media/trusted" ]; then
	sudo mount /dev/sda1 /media/untrusted
	sudo mount /dev/sdb1 /media/trusted
	sudo rm -r /media/untrusted/*
	sudo rm -r /media/trusted/*

	if [ "$1" = "1" ]; then
		# demo
		sudo cp -r /home/usbbp/untrusted/bombs/* /media/untrusted
		sudo cp -r /home/usbbp/untrusted/clam/* /media/untrusted
	elif [ "$1" = "2" ]; then
		# zips
		sudo cp -r /home/usbbp/untrusted/zips/* /media/untrusted
	elif [ "$1" = "3" ]; then
		# clam
		sudo cp -r /home/usbbp/untrusted/clam/* /media/untrusted
	elif [ "$1" != "4" ]; then
		echo "$usage"
		exit 1
	fi

	sudo umount /media/untrusted
	sudo umount /media/trusted
else
	if [ "$1" = "1" ] || [ "$1" = "2" ] || [ "$1" = "3" ]; then
		echo "No storage devices connected for reset."
		exit 1
	elif [ "$1" != "4" ]; then
		echo "$usage"
		exit 1
	fi
fi

exit 0

