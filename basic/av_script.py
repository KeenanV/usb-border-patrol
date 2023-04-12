#!/usr/bin/env -S python3 -u
import os
import argparse
import shutil
from pathlib import Path


class AV:
    def __init__(self, malicious_usb_path, clean_usb_path):
        self.malicious_usb_path = malicious_usb_path
        self.clean_usb_path = clean_usb_path
        self.good = 0
        self.bad = 0
        self.suspicious = 0

    def main(self):
        # checks if the malicious directory exists and creates it if not
        malicious_dir_path = Path.cwd() / "malicious"
        malicious_dir_path.mkdir(parents=True, exist_ok=True)

        # moves all files from malicious usb into temporary directory to prevent clamav error
        temp_dir_path = Path.cwd() / "temp_dir"
        temp_dir_path.mkdir(parents=True, exist_ok=True)
        all_files = os.listdir(str(self.malicious_usb_path))
        for filename in all_files:
            old_file_path = str(self.malicious_usb_path / Path(filename))
            new_file_path = str(temp_dir_path / Path(filename))
            shutil.move(old_file_path, new_file_path)

        # runs all files in the usb directory against the antivirus
        malicious_path_str = str(malicious_dir_path)
        temp_file = open("temp_file.txt", "w")
        for filename in temp_dir_path.glob("**/*"):
            if filename.is_file():
                temp_file.write(str(filename) + "\n")
        temp_file.close()
        cmd = "clamscan --file-list=temp_file.txt --move=" + malicious_path_str
        os.system(cmd)
        temp_file_path = Path("temp_file.txt")
        temp_file_path.unlink()

        # gets a list of all the malicious files separated
        malicious_files = []
        for filename in malicious_dir_path.glob("**/*"):
            if filename.is_file():
                malicious_files.append(filename)
                    
        # checks if the suspicious directory exists and creates it if not
        suspicious_dir_path = Path.cwd() / "suspicious"
        suspicious_dir_path.mkdir(parents=True, exist_ok=True)
        
        #move suspicious and non malicious files to usb
        suspicious_extensions = [".exe", ".html", ".sfx", ".bat", ".sh", ".vbs", ".dll", ".lnk", ".ps1", ".jar"]
        remaining_files = temp_dir_path.glob("**/*")
        suspicious_files = []
        for filename in remaining_files:
            is_suspicious = False
            for extension in suspicious_extensions:
                if extension in str(filename)[(0 - len(extension)):]:
                    is_suspicious = True
            if is_suspicious:
                self.suspicious += 1
                shutil.move(filename, suspicious_dir_path)
            else:
                self.good += 1
                suspicious_files.append(str(filename))
                shutil.move(filename, self.clean_usb_path)
        if suspicious_files:
            shutil.move(suspicious_dir_path, self.clean_usb_path)

        shutil.rmtree(str(temp_dir_path))
        
        # creates a log of the malicious files
        log_file = "/home/usbbp/tmp/usbbp.log"
        with open(log_file, "a") as ff:
            if malicious_files:
                self.bad += len(malicious_files)
                ff.write("=====================MALICIOUS=====================\n")
                ff.write("The following files were infected by known malware.\n")
                ff.write("===================================================\n")
                for filename in malicious_files:
                    ff.write(str(filename) + "\n")
            if suspicious_files:
                ff.write("======================SUSPICIOUS======================\n")
                ff.write("The following file types are known to contain malware.\n")
                ff.write("Only open them if you trust the source.\n")
                ff.write("======================================================\n")
                for filename in suspicious_files:
                    ff.write(str(filename) + "\n")

        with open("/home/usbbp/tmp/gb-tmp.txt", 'a') as ff:
            ff.write(f"{self.good}\n{self.bad}\n{self.suspicious}")

        # moves log file to clean usb
        log_file_absolute_path = Path(log_file)
        log_file_name = Path("usbbp.log")
        shutil.move(log_file_absolute_path, self.clean_usb_path / log_file_name)


if __name__ == "__main__":
    # get USB path from command line
    parser = argparse.ArgumentParser(description="Scans the files in the given directory for malware")
    parser.add_argument("malicious_usb_path", type=str, help="The path of the USB to be scanned")
    parser.add_argument("clean_usb_path", type=str, help="The path of the clean USB")
    args = parser.parse_args()

    av = AV(Path(args.malicious_usb_path), Path(args.clean_usb_path))
    av.main()
