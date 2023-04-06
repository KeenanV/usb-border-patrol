#!/bin/bash


date >> /home/usbbp/devices.log && echo -e "Start\n" >> /home/usbbp/devices.log

while true; do
	events=$(ls /dev/input)
	substring="event"
	if [[ $events = *"$substring"* ]]; then
		date >> /home/usbbp/devices.log && echo -e "Device found\n" >> /home/usbbp/devices.log
		sudo modprobe -r usbhid
		date >> /home/usbbp/devices.log && echo -e "Device disabled\n" >> /home/usbbp/devices.log
		/home/usbbp/Documents/capstone/usb-border-patrol/basic/output-test.sh id
		exit
	fi
done
