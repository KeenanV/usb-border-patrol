#!/usr/bin/env -S python3 -u
import os
import time
import datetime

# logging
log_file = "trigger_log.txt"
f = open(log_file, "w")

def log(msg : str):
    text = '{} >> {}'.format(datetime.datetime.now(), msg)
    f.write(text)
    print(text)

def check_usbs():
    '''
    Checks for any USB connections, returns False when two USBs are found, otherwise returns True.
    '''
    stream = os.popen('lsblk')
    output : str = stream.read()
    if 'sda' in output and 'sdb' in output:
        log("FOUND 2 USB storage devices!")
        return False 
    elif 'sda' in output and 'sdb' not in output:
        log('found first USB storage device, waiting on second')
        return True
    elif 'sda' not in output and 'sdb' in output:
        log('this is a weird error...this was entirely unexpected')
        return True
    else:        
        log("didn't find two USB storage devices")
        return True

def reset():
    if os.path.exists('/dev/sda*'):
        os.system('sudo rm -rf /dev/sda*')
    if os.path.exists('/dev/sdb*'):
        os.system('sudo rm -rf /dev/sdb*')

def main():
    reset()

    while check_usbs():
        time.sleep(0.5)

    # loop exited, two USBs have been detected
    log("loop exited, continuing with trigger script...")
    
    # check if mount-points already exist
    if os.path.exists("/media/untrusted"):
        log("/media/untrusted already exists, deleting folder")
        os.system('sudo umount /media/untrusted')
        os.system('sudo rm -rf /media/untrusted')
    if os.path.exists("/media/trusted"):
        log("/media/trusted already exists, deleting folder")
        os.system('sudo umount /media/trusted')
        os.system('sudo rm -rf /media/trusted')

    # create directories for mount points
    os.system('sudo mkdir /media/untrusted')
    os.system('sudo mkdir /media/trusted')

    # Change mount-points of USB to appropriate paths
    # UNTRUSTED USB: "/media/untrusted"
    # TRUSTED USB:   "/media/trusted"
    log("attempting to mount USB storage devices to pre-defined folders")
    os.system('sudo mount /dev/sda1 /media/untrusted')
    os.system('sudo mount /dev/sdb1 /media/trusted')

    # execute scripts
    log("USB storage devices have been mounted, now executing other USB Border Patrol Scripts")
    os.system('/home/usb-border-patrol/usb-border-patrol/basic/unpack.py /media/untrusted /media/trusted')
    os.system('/home/usb-border-patrol/usb-border-patrol/basic/av_script.py /media/untrusted /media/trusted')

if __name__ == "__main__":
    main()
