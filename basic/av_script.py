import os
import argparse
from pathlib import Path

def main():
    #get USB path from command line
    parser = argparse.ArgumentParser(description="Scans the files in the given directory for malware")
    parser.add_argument("usb_path", type=str, help="The path of the USB to be scanned")
    args = parser.parse_args()
    usb_path = Path(args.usb_path)

    #checks if the malicious directory exists and creates it if not
    malicious_dir_path = Path.cwd() / "malicious"
    malicious_dir_path.mkdir(parents=True, exist_ok=True)

    #runs all files in the usb directory against the antivirus
    malicious_path_str = str(malicious_dir_path)
    temp_file = open("temp_file.txt", "w")
    for filename in usb_path.glob("**/*"):
        if filename.is_file():
            temp_file.write(str(filename) + "\n")
    temp_file.close()
    cmd = "clamscan --file-list=temp_file.txt --move=" +  malicious_path_str
    os.system(cmd)
    temp_file_path = Path("temp_file.txt")
    temp_file_path.unlink()

    #checks if the non_malicious directory exists and creates it if not
    non_malicious_dir_path = Path.cwd() / "non_malicious"
    non_malicious_dir_path.mkdir(parents=True, exist_ok=True)

    #moves non malicious file to non malicious directory
    for filename in usb_path.glob("**/*"):
        file_str = str(filename)
        if filename.is_file():
            filename.rename(non_malicious_dir_path / filename.name)
    
    #gets a list of all the malicious files separated
    malicious_files = []
    for filename in malicious_dir_path.glob("**/*"):
        if filename.is_file():
                malicious_files.append(filename)
    
    #creates a log of the malicious files
    log_file = "av_log.txt"
    f = open(log_file, "w")
    if malicious_files:
         f.write("=====================MALICIOUS=====================\n")
         f.write("The following files were infected by known malware.\n")
         f.write("===================================================\n")
         for filename in malicious_files:
              f.write(str(filename) + "\n")
    f.close()

if __name__ == "__main__":
     main()