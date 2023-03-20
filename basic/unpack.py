#!/usr/bin/env -S python3 -u
import argparse, os, magic
import zipfile, tarfile
from pathlib import Path
import subprocess
from zipfile import ZipFile

class unpack():
    log = []

    def __init__(self, usb_path):
       self.usb_path = usb_path.usb

    def remove_file(self, path, filename, msg, zip):
        self.log.append([filename, msg])
        os.remove(self.usb_path + "/" + filename) # delete the extracted file
        if zip:
            cmd=['zip', '-d', path] + [filename] # delete the file in the zip
            subprocess.check_call(cmd)
        else: 
            os.remove(path)

    # unzip it and read the rest of the files
    def zip(self, path):
        with ZipFile(path, 'r') as zObject:
            unzipped = zObject.infolist()
            zObject.extractall(path=self.usb_path) # extract all the files

            for zfile in unzipped:
                if magic.from_file(self.usb_path + "/" + zfile.filename, mime=True) == "application/zip": # recursive zips
                    if not self.check_bomb(self.usb_path + "/" + zfile.filename, 1, []):
                        self.log.append([zfile, "Potential zip bomb detected"])
                        os.remove(self.usb_path + "/" + zfile.filename) # delete the extracted file
                        cmd=['zip', '-d', path] + [zfile.filename] # delete the file in the zip
                        subprocess.check_call(cmd) 
                elif zfile.file_size > 10000000: # if the zip is greater than a certain size drop it (potential bomb)
                    self.log.append([zfile, "Zipfile suspiciously large"])
                    os.remove(self.usb_path + "/" + zfile.filename) # delete the extracted file
                    cmd=['zip', '-d', path] + [zfile.filename] # delete the file in the zip
                    subprocess.check_call(cmd)
    
    # unzip it and read the rest of the files
    def tar(self, path):
        tObject = tarfile.open(path)
        unzipped = tObject.getmembers()
        tObject.extractall(path=self.usb_path) # extract all the files
        
        for tfile in unzipped:
            if os.path.isdir(self.usb_path + "/" + tfile.name): # if it's a directory
                continue # self.dir(tfile.name)
            elif tarfile.is_tarfile(self.usb_path + "/" + tfile.name):
                if tfile.size > 1000000: # if the tar is greater than a certain size drop it (potential bomb)\
                    self.remove_file(path, tfile.name, "Tarfile suspiciously large", False)
                elif not self.check_tbomb(self.usb_path + "/" + tfile.name, 1, []): # recursive tars
                    self.remove_file(path, tfile.name, "Potential tar bomb detected", False)

    # go through a zip file to check for zip bombs
    def check_bomb(self, path, count, zips):
        if count >= 4: # at least 5 nested zips
            for z in zips:
                os.remove(self.usb_path + "/" + z)
            return False
        with ZipFile(path, 'r') as zObject: # going through list of files
            unzipped = zObject.infolist()
            zObject.extractall(path=self.usb_path)
            for zfile in unzipped:
                if os.path.isdir(self.usb_path + "/" + zfile.filename): # if it's a directory
                    continue
                elif magic.from_file(self.usb_path + "/" + zfile.filename, mime=True) == "application/zip":
                    return self.check_bomb(self.usb_path + "/" + zfile.filename, count + 1, zips + [zfile.filename])
        return True

    # go through a tar file to check for tar bombs
    def check_tbomb(self, path, count, tars):
        if count >= 4: # at least 5 nested tars
            for t in tars:
                os.remove(self.usb_path + "/" + t)
            return False
        tObject = tarfile.open(path)
        unzipped = tObject.getmembers()
        tObject.extractall(path=self.usb_path)
        for tfile in unzipped:
            if os.path.isdir(self.usb_path + "/" + tfile.name): # if it's a directory
                continue
            elif tarfile.is_tarfile(self.usb_path + "/" + tfile.name):
                return self.check_tbomb(self.usb_path + "/" + tfile.name, count + 1, tars + [tfile.name])
        return True

    def run(self):
        if not os.listdir(self.usb_path): # if list of files is empty
            print("\nUSB flash is already empty.") # send a message and continue
        else:
            usb = Path(self.usb_path)
            for filename in usb.glob("**/*"):
                if os.path.isfile(filename): # if it's a file
                    if zipfile.is_zipfile(filename): # magic.from_file(filename, mime=True) == "application/zip":
                        self.zip(filename) # unzip it
                    elif tarfile.is_tarfile(filename):
                        self.tar(filename) # unzip it
                # elif not a directory: is irregular file
                    
        log_file = "unpack.log"
        f = open(self.usb_path + "/" + log_file, "w")
        for log in self.log:
           f.write(str(log[0]) + ": " + log[1] + "\n")
        f.close()
        return
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='unpack files')
    parser.add_argument('usb', type=str, help="The path to the usb")
    args = parser.parse_args()
    usb = unpack(args)
    usb.run()
