#!/usr/bin/env -S python3 -u
import argparse
import os, magic
import tarfile
import subprocess
from zipfile import ZipFile

class unpack():
    log = []

    def __init__(self, usb_path):
       self.usb_path = usb_path.usb

    # in case of a regular file 
    def file(self, file):
        path = self.usb_path + "/" + file
        if os.path.isfile(path): # if it's a file
            if magic.from_file(path, mime=True) == "application/zip":
                self.zip(path) # unzip it
            elif tarfile.is_tarfile(path):
                self.tar(path) # unzip it

    # in case of a directory
    def dir(self, dir):
        path = self.usb_path + "/" + dir
        if os.listdir(path):
            dir_files = os.listdir(path) # read the files in the directory
            for dfile in dir_files:
                if os.path.isdir(path + "/" + dfile): # if it is a directory - open that!
                    self.dir(dir + "/" + dfile)
                else: 
                    self.file(dir + "/" + dfile)

    # unzip it and read the rest of the files
    def zip(self, path):
        with ZipFile(path, 'r') as zObject:
            unzipped = zObject.infolist()
            zObject.extractall(path=self.usb_path) # extract all the files

            for zfile in unzipped:
                if magic.from_file(self.usb_path + "/" + zfile.filename, mime=True) == "application/zip": # recursive zips
                    if self.check_bomb(self.usb_path + "/" + zfile.filename, 1, []) == False:
                        self.log.append([zfile, "Potential zip bomb detected"])
                        os.remove(self.usb_path + "/" + zfile.filename) # delete the extracted file
                        cmd=['zip', '-d', path] + [zfile.filename] # delete the file in the zip
                        subprocess.check_call(cmd)  
                if zfile.file_size > 1000000: # if the zip is greater than a certain size drop it (potential bomb)
                    self.log.append([zfile, "Zipfile suspiciously large"])
                    os.remove(self.usb_path + "/" + zfile.filename) # delete the extracted file
                    cmd=['zip', '-d', path] + [zfile.filename] # delete the file in the zip
                    subprocess.check_call(cmd)
                else:
                    self.file(zfile.filename)
    
    # unzip it and read the rest of the files
    def tar(self, path):
        tObject = tarfile.open(path)
        unzipped = tObject.getmembers()
        tObject.extractall(path=self.usb_path) # extract all the files
        
        for tfile in unzipped:
            if tfile.size > 1000000: # if the tar is greater than a certain size drop it (potential bomb)
                self.log.append([tfile, "Tarfile suspiciously large"])
                os.remove(self.usb_path + "/" + tfile.name) # delete the extracted file
                os.remove(path) # delete the original tar 
            if tarfile.is_tarfile(self.usb_path + "/" + tfile.name): # recursive tars
                if self.check_tbomb(self.usb_path + "/" + tfile.name, 1, []) == False:
                    self.log.append([tfile, "Potential tar bomb detected"])
                    os.remove(self.usb_path + "/" + tfile.name) # delete the extracted file
                    os.remove(path) # delete the original tar 
            else:
                self.file(tfile.name)

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
                if magic.from_file(self.usb_path + "/" + zfile.filename, mime=True) == "application/zip":
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
            if tarfile.is_tarfile(self.usb_path + "/" + tfile.name):
                return self.check_tbomb(self.usb_path + "/" + tfile.name, count + 1, tars + [tfile.name])
        return True

    def run(self):

        if not os.listdir(self.usb_path): # if list of files is empty
            print("\nUSB flash is already empty.") # send a message and continue

        else:
            files = os.listdir(self.usb_path) # list of names of files in the usb flash
            for file in files: # loop through the file list
                path = self.usb_path + "/" + file
                if os.path.isfile(path): # if it's a file
                    self.file(file)
                    continue
                elif os.path.isdir(path): # if it's a directory
                    self.dir(file)
                else: # it's something else
                    self.log.append(file, "Irregular file.")

        print("\nDone extracting files")
        log_file = "unpack_log.txt"
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
