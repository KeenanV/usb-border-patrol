#!/usr/bin/env -S python3 -u
import os
import time
import datetime


class Trigger:
    def __init__(self):
        # logging
        self.log_file = "trigger_log.log"
        self.ff = open(self.log_file, "w")

    def log(self, msg: str):
        text = '{} >> {}'.format(datetime.datetime.now(), msg)
        self.ff.write(text)
        print(text)

    def check_usbs(self):
        """
        Checks for any USB connections, returns False when two USBs are found, otherwise returns True.
        """
        stream = os.popen('lsblk')
        output: str = stream.read()
        if 'sda' in output and 'sdb' in output:
            self.log("FOUND 2 USB storage devices!")
            return False
        elif 'sda' in output and 'sdb' not in output:
            self.log('found first USB storage device, waiting on second')
            return True
        elif 'sda' not in output and 'sdb' in output:
            self.log('this is a weird error...this was entirely unexpected')
            return True
        else:
            self.log("didn't find two USB storage devices")
            return True

    def reset(self):
        self.log("resetting system state...may encounter errors (can ignore)")
        os.system('sudo umount /media/untrusted')
        os.system('sudo umount /media/trusted')
        if os.path.exists('/dev/sda*'):
            os.system('sudo rm -rf /dev/sda*')
        if os.path.exists('/dev/sdb*'):
            os.system('sudo rm -rf /dev/sdb*')
        self.log("finished resetting system state")

    def main(self):
        self.reset()

        while self.check_usbs():
            time.sleep(0.5)

        # loop exited, two USBs have been detected
        self.log("loop exited, continuing with trigger script...")

        # check if mount-points already exist
        if os.path.exists("/media/untrusted"):
            self.log("/media/untrusted already exists, deleting folder")
            os.system('sudo umount /media/untrusted')
            os.system('sudo rm -rf /media/untrusted')
        if os.path.exists("/media/trusted"):
            self.log("/media/trusted already exists, deleting folder")
            os.system('sudo umount /media/trusted')
            os.system('sudo rm -rf /media/trusted')

        # create directories for mount points
        os.system('sudo mkdir /media/untrusted')
        os.system('sudo mkdir /media/trusted')

        # Change mount-points of USB to appropriate paths
        # UNTRUSTED USB: "/media/untrusted"
        # TRUSTED USB:   "/media/trusted"
        self.log("attempting to mount USB storage devices to pre-defined folders")
        os.system('sudo mount /dev/sda1 /media/untrusted')
        os.system('sudo mount /dev/sdb1 /media/trusted')

        # execute scripts
        self.log("USB storage devices have been mounted, now executing other USB Border Patrol Scripts")
        os.system('sudo ./unpack.py /media/untrusted')
        self.log("Running Anti-Virus (AV)...")
        os.system('sudo ./av_script.py /media/untrusted /media/trusted')

        # eject/unmount USBs
        self.log("scripts have finished execution...now ejecting USBs")
        os.system('sudo umount /media/untrusted')
        os.system('sudo umount /media/trusted')
        os.system('./output-test.sh')


if __name__ == "__main__":
    trigger = Trigger()
    trigger.main()
