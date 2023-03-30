#!/usr/bin/env -S python3 -u
import argparse
import magic
import os
import tarfile
import zipfile
from pathlib import Path
from zipfile import ZipFile


class Unpack:
    def __init__(self, usb_path):
        self.usb_path = usb_path
        self.log = []
        self.good = 0
        self.bad = 0

    def remove_file(self, path, filename, file_info, msg, zip_file):
        self.log.append([file_info, msg])
        self.bad += 1
        os.remove(self.usb_path + "/" + filename)  # delete the extracted file
        if zip_file:
            zin = zipfile.ZipFile(path, 'r')
            zout = zipfile.ZipFile(str(path)[0:len(str(path)) - 4] + '_new.zip', 'w')
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                if item.filename != filename:
                    zout.writestr(item, buffer)
            zout.close()
            zin.close()
            os.remove(path)
        else:
            os.remove(path)

    # unzip it and read the rest of the files
    def zip(self, path):
        with ZipFile(path, 'r') as zObject:
            unzipped = zObject.infolist()
            zObject.extractall(path=self.usb_path)  # extract all the files

            for z_file in unzipped:
                if os.path.isdir(self.usb_path + "/" + z_file.filename):  # if it's a directory
                    continue
                if magic.from_file(self.usb_path + "/" + z_file.filename,
                                   mime=True) == "application/zip":  # recursive zips
                    if z_file.file_size > 10000000:  # if the zip is greater than a certain size drop it (potential bomb)
                        self.remove_file(path, z_file.filename, z_file, "Zipfile suspiciously large", True)
                    elif not self.check_bomb(self.usb_path + "/" + z_file.filename, 1, []):
                        self.remove_file(path, z_file.filename, z_file, "Potential zip bomb detected", True)
                    else:
                        self.good += 1

    # unzip it and read the rest of the files
    def tar(self, path):
        t_object = tarfile.open(path)
        unzipped = t_object.getmembers()
        t_object.extractall(path=self.usb_path)  # extract all the files

        for t_file in unzipped:
            if os.path.isdir(self.usb_path + "/" + t_file.name):  # if it's a directory
                continue
            elif tarfile.is_tarfile(self.usb_path + "/" + t_file.name):
                if t_file.size > 1000000:  # if the tar is greater than a certain size drop it (potential bomb)
                    self.remove_file(path, t_file.name, t_file, "Tarfile suspiciously large", False)
                elif not self.check_tbomb(self.usb_path + "/" + t_file.name, 1, []):  # recursive tars
                    self.remove_file(path, t_file.name, t_file, "Potential tar bomb detected", False)
                else:
                    print("Ran the else")
                    self.good += 1

    # go through a zip file to check for zip bombs
    def check_bomb(self, path, count, zips):
        if count >= 4:  # at least 5 nested zips
            for z in zips:
                os.remove(self.usb_path + "/" + z)
            return False
        with ZipFile(path, 'r') as zObject:  # going through list of files
            unzipped = zObject.infolist()
            zObject.extractall(path=self.usb_path)
            for z_file in unzipped:
                if os.path.isdir(self.usb_path + "/" + z_file.filename):  # if it's a directory
                    continue
                elif magic.from_file(self.usb_path + "/" + z_file.filename, mime=True) == "application/zip":
                    return self.check_bomb(self.usb_path + "/" + z_file.filename, count + 1, zips + [z_file.filename])
        self.good += 1
        print("Returned true")
        return True

    # go through a tar file to check for tar bombs
    def check_tbomb(self, path, count, tars):
        if count >= 4:  # at least 5 nested tars
            for t in tars:
                os.remove(self.usb_path + "/" + t)
            return False
        t_object = tarfile.open(path)
        unzipped = t_object.getmembers()
        t_object.extractall(path=self.usb_path)
        for t_file in unzipped:
            if os.path.isdir(self.usb_path + "/" + t_file.name):  # if it's a directory
                continue
            elif tarfile.is_tarfile(self.usb_path + "/" + t_file.name):
                return self.check_tbomb(self.usb_path + "/" + t_file.name, count + 1, tars + [t_file.name])
        return True

    def run(self):
        if not os.listdir(self.usb_path):  # if list of files is empty
            print("\nUSB flash is already empty.")  # send a message and continue
        else:
            usb_drive = Path(self.usb_path)
            for filename in usb_drive.glob("**/*"):
                if os.path.isfile(filename):  # if it's a file
                    if zipfile.is_zipfile(filename):
                        self.zip(filename)  # unzip it
                    elif tarfile.is_tarfile(filename):
                        self.tar(filename)  # unzip it

        log_file = "unpack.log"
        with open(self.usb_path + "/" + log_file, "w") as ff:
            for log in self.log:
                ff.write(str(log[0]) + ": " + log[1] + "\n\n")

        with open("gb-tmp.txt", 'w') as ff:
            ff.write(f"{self.good}\n{self.bad}\n")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='unpack files')
    parser.add_argument('usb', type=str, help="The path to the usb")
    args = parser.parse_args()
    usb = Unpack(args.usb)
    usb.run()
