#!/usr/bin/env -S python3 -u
import os
import time


def plugin():
    """
    Checks every 0.5 seconds for two storage devices to be plugged in
    :return:
    """
    while True:
        # check for newly mounted devices
        stream = os.popen('lsblk')
        output: list[str] = stream.readlines()

        # maintain a count of partitions
        sda_count = 0
        sdb_count = 0

        # check for 1st and 2nd mounted devices
        for line in output:
            if 'sda' in line:
                sda_count += 1
            elif 'sdb' in line:
                sdb_count += 1

        if sda_count > 0 and sdb_count > 0:
            paths = []
            # sda1 --> "dirty USB" (with malicious files)
            # sdb1 --> "clean USB" (with zero files) that we copy files from sda1 from
            # for i in (sda_count - 1):
            #     paths.append('/dev/sda{}'.format(i + 1))
            # for i in (sdb_count - 1):
            #     paths.append('/dev/sdb{}'.format(i + 1))

            exec("/home/usb-border-patrol/usb-border-patrol/basic/unpack.py", "/dev/sda1")
            exec("/home/usb-border-patrol/usb-border-patrol/basic/av_script.py", '/dev/sda1')

            # prevent future temporarily, will need to change or final script needs to restart script
            unplug()

        time.sleep(0.5)


def unplug():
    """
    Checks for when all devices are unplugged
    :return:
    """
    while True:
        stream = os.popen('lsblk')
        output: str = stream.read()

        if 'sda' not in output and 'sdb' not in output:
            break

        time.sleep(0.5)
