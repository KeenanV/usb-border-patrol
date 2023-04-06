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

    def main(self):
        # checks if the malicious directory exists and creates it if not
        malicious_dir_path = Path.cwd() / "malicious"
        malicious_dir_path.mkdir(parents=True, exist_ok=True)

        # runs all files in the usb directory against the antivirus
        malicious_path_str = str(malicious_dir_path)
        temp_file = open("temp_file.txt", "w")
        for filename in self.malicious_usb_path.glob("**/*"):
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

        # creates a log of the malicious files
        log_file = "av_log.log"
        with open(log_file, "w") as ff:
            if malicious_files:
                self.bad += len(malicious_files)
                ff.write("=====================MALICIOUS=====================\n")
                ff.write("The following files were infected by known malware.\n")
                ff.write("===================================================\n")
                for filename in malicious_files:
                    ff.write(str(filename) + "\n")

        # moves non-malicious files to clean usb
        for filename in self.malicious_usb_path.glob("**/*"):
            file_str = str(filename)
            if filename.is_file():
                shutil.move(file_str, str(self.clean_usb_path))
                self.good += 1

        with open("/home/usbbp/tmp/gb-tmp.txt", 'a') as ff:
            ff.write(f"{self.good}\n{self.bad}")

        # moves log file to clean usb
        if malicious_files:
            log_file_name = Path(log_file)
            log_file_path = Path.cwd() / log_file_name
            shutil.move(str(log_file_path), str(self.clean_usb_path / log_file_name))


if __name__ == "__main__":
    # get USB path from command line
    parser = argparse.ArgumentParser(description="Scans the files in the given directory for malware")
    parser.add_argument("malicious_usb_path", type=str, help="The path of the USB to be scanned")
    parser.add_argument("clean_usb_path", type=str, help="The path of the clean USB")
    args = parser.parse_args()

    av = AV(Path(args.malicious_usb_path), Path(args.clean_usb_path))
    av.main()
