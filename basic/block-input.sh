#!/bin/bash


date > $HOME/devices.log && echo -e "Start\n" >> $HOME/devices.log

while true; do
	events=$(ls /dev/input)
	substring="event"
	if [[ $events = *"$substring"* ]]; then
		date >> $HOME/devices.log && echo -e "Device found\n" >> $HOME/devices.log
		# sudo modprobe -r usbhid
		date >> $HOME/devices.log && echo -e "Device disabled\n" >> $HOME/devices.log
		$HOME/Documents/capstone/usb-border-patrol/basic/output-test.sh
		exit
	fi
done
