#!/bin/bash

sudo mount /dev/sda1 /media/untrusted
sudo mount /dev/sdb1 /media/trusted

sudo rm -r /media/untrusted/*
sudo rm -r /media/trusted/*
sudo rm /home/usbbp/tmp/*
sudo rm -r /home/usbbp/usb-border-patrol/basic/malicious/*

sudo cp -r /home/usbbp/untrusted/* /media/untrusted

