#!/usr/bin/env -S python3 -u
import argparse
import magic
import os
import tarfile
import zipfile
from pathlib import Path
from zipfile import ZipFile
from progressbar import ProgressBar
import progressbar
import numpy as np


class Unpack:
    def __init__(self, usb_path):
        self.usb_path = usb_path
        self.log = []
        self.good = 0
        self.bad = 0

    def remove_file(self, path, filename, file_info, msg, zip):
        self.log.append(["In " + str(path)[len(self.usb_path) + 1:] + " found: " + str(file_info), msg])
        if zip and os.path.exists(path):
            zin = zipfile.ZipFile(path, 'r')
            zout = zipfile.ZipFile(str(path)[0:len(str(path)) - 4] + '_new.zip', 'w')
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if item.filename != filename:
                    zout.writestr(item, buffer)
            zout.close()
            zin.close()
            os.remove(path)
            os.rename(str(path)[0:len(str(path)) - 4] + '_new.zip', path)

    # unzip it and read the rest of the files
    def zip(self, path):
        with ZipFile(path, 'r') as zObject:
            unzipped = zObject.infolist()
            bad = False
            for z_file in unzipped:
                zObject.extract(z_file.filename, self.usb_path)  # extract all the files
                if os.path.isdir(self.usb_path + "/" + z_file.filename):  # if it's a directory
                    continue
                if magic.from_file(self.usb_path + "/" + z_file.filename,
                                   mime=True) == "application/zip":  # recursive zips
                    if z_file.file_size > 10000000:  # if the zip is greater than a certain size drop it (potential bomb)
                        bad = True
                        self.remove_file(path, z_file.filename, z_file, "Zipfile suspiciously large", True)
                    elif not self.check_bomb(self.usb_path + "/" + z_file.filename, 1, [z_file.filename]):
                        bad = True
                        self.remove_file(path, z_file.filename, z_file, "Potential zip bomb detected", True)
                    else:
                        self.good += 1
                elif tarfile.is_tarfile(self.usb_path + "/" + z_file.filename):
                    if not self.check_tbomb(self.usb_path + "/" + z_file.filename, 1, [z_file.filename]):
                        bad = True
                        self.remove_file(path, z_file.filename, z_file, "Zipfile suspiciously large", True)
                    else:
                        self.good += 1
        if os.path.exists(path): os.remove(path)
        if bad: self.bad += 1

    # unzip it and read the rest of the files
    def tar(self, path):
        t_object = tarfile.open(path)
        unzipped = t_object.getmembers()
        bad = False
        for t_file in unzipped:
            t_object.extract(t_file.name, self.usb_path)
            if os.path.isdir(self.usb_path + "/" + t_file.name):  # if it's a directory
                continue
            elif tarfile.is_tarfile(self.usb_path + "/" + t_file.name):
                if t_file.size > 1000000:  # if the tar is greater than a certain size drop it (potential bomb)
                    bad = True
                    self.remove_file(path, t_file.name, t_file, "Tarfile suspiciously large", False)
                elif not self.check_tbomb(self.usb_path + "/" + t_file.name, 1, [t_file.name]):  # recursive tars
                    bad = True
                    self.remove_file(path, t_file.name, t_file, "Potential tar bomb detected", False)
                else:
                    self.good += 1
            elif magic.from_file(self.usb_path + "/" + t_file.name, mime=True) == "application/zip":  # recursive zips
                if not self.check_bomb(self.usb_path + "/" + t_file.name, 1, [t_file.name]):
                    bad = True
                    self.remove_file(path, t_file.name, t_file, "Potential tar bomb detected", False)
                else:
                    self.good += 1
        if os.path.exists(path): os.remove(path)
        if bad: self.bad += 1

    # go through a zip file to check for zip bombs
    def check_bomb(self, path, count, zips):
        if count >= 4:  # at least 5 nested zips
            for z in np.unique(zips):
                os.remove(self.usb_path + "/" + z)
            return False
        with ZipFile(path, 'r') as zObject:  # going through list of files
            unzipped = zObject.infolist()
            for z_file in unzipped:
                zObject.extract(z_file.filename, self.usb_path)
                if os.path.isdir(self.usb_path + "/" + z_file.filename):  # if it's a directory
                    continue
                elif magic.from_file(self.usb_path + "/" + z_file.filename, mime=True) == "application/zip":
                    return self.check_bomb(self.usb_path + "/" + z_file.filename, count + 1, zips + [z_file.filename])
                elif tarfile.is_tarfile(self.usb_path + "/" + z_file.filename):
                    return self.check_tbomb(self.usb_path + "/" + z_file.filename, count + 1, zips + [z_file.filename])
        self.good += 1
        for z in zips:  os.remove(self.usb_path + "/" + z)
        return True

    # go through a tar file to check for tar bombs
    def check_tbomb(self, path, count, tars):
        if count >= 4:  # at least 5 nested tars
            for t in np.unique(tars):
                os.remove(self.usb_path + "/" + t)
            return False
        tObject = tarfile.open(path)
        unzipped = tObject.getmembers()
        for t_file in unzipped:
            tObject.extract(t_file.name, self.usb_path)
            if os.path.isdir(self.usb_path + "/" + t_file.name):  # if it's a directory
                continue
            elif tarfile.is_tarfile(self.usb_path + "/" + t_file.name):
                return self.check_tbomb(self.usb_path + "/" + t_file.name, count + 1, tars + [t_file.name])
            elif magic.from_file(self.usb_path + "/" + t_file.name, mime=True) == "application/zip":
                return self.check_bomb(self.usb_path + "/" + t_file.name, count + 1, tars + [t_file.name])
        self.good += 1
        for t in tars:  os.remove(self.usb_path + "/" + t)
        return True

    def run(self):
        if not os.listdir(self.usb_path):  # if list of files is empty
            print("\nUSB flash is already empty.")  # send a message and continue
        else:
            widgets = ['Checking for Zip Bombs: ', progressbar.Bar(u"█"), ' (', progressbar.ETA(), ') ', ]
            pbar = ProgressBar(widgets=widgets).start()
            usb = Path(self.usb_path)
            for filename in pbar(usb.glob("**/*")):
                filename = os.path.join(self.usb_path, filename)
                if os.path.isfile(filename):  # if it's a file
                    if zipfile.is_zipfile(filename):
                        self.zip(filename)  # unzip it
                    elif tarfile.is_tarfile(filename):
                        self.tar(filename)  # unzip it

        log_file = "usbbp.log"
        with open(self.usb_path + "/" + log_file, "w") as ff:
            ff.write("=====================ZIP BOMBS=====================\n")
            ff.write("The following files were detected as zip bombs.\n")
            ff.write("===================================================\n\n")
            for log in self.log:
                ff.write(str(log[0]) + ": " + log[1] + "\n\n")

        with open("/home/usbbp/tmp/gb-tmp.txt", 'w') as ff:
            ff.write(f"{self.good}\n{self.bad}\n")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='unpack files')
    parser.add_argument('usb', type=str, help="The path to the usb")
    args = parser.parse_args()
    usb = Unpack(args.usb)
    usb.run()
