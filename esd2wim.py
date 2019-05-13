import os
import subprocess
import ctypes
import colorama
import time
import argparse


VERSION = "0.1"
WIM_SIGNATURE = b'MSWIM\x00\x00\x00'


parser = argparse.ArgumentParser(prog="esd2wim",
                                 description="Convert Windows ESD images to Windows WIM images. Version v{}".format(VERSION),
                                 epilog="Created by Thomas Jones - 01/05/2019")
parser.add_argument("esd_file", help="path to an ESD file")
parser.add_argument("--compression", help="configure compression (default: max)", choices=["none", "fast", "max"], default="max")
parser.add_argument("--verbose", help="show extra information", action="store_true")
args = parser.parse_args()

def qprint(*args, **kwargs):
    colorama.init()
    args = list(args)
    qcodes = {0: colorama.Fore.BLACK, 1: colorama.Fore.RED, 2: colorama.Fore.GREEN, 3: colorama.Fore.YELLOW, 4: colorama.Fore.BLUE, 5: colorama.Fore.CYAN, 6: colorama.Fore.MAGENTA, 7: colorama.Fore.WHITE}
    for index, arg in enumerate(args):
        for code, colour in qcodes.items():
            if "^{}".format(code) in arg:
                args[index] = args[index].replace("^{}".format(code), colour) + colorama.Style.RESET_ALL
    print(*args, **kwargs)
    
def dism(*args):
    dism_path = os.path.join(os.environ["windir"], "System32", "Dism.exe")
    return subprocess.check_output([dism_path, *args], cwd=os.getcwd(), shell=True).decode()

def new_file_extension(filename, extension):
    return str(".".join(filename.split(".")[:-1]) + ".{}".format(extension))

def print_image_info(images, filename):
    for index, image in images.items():
        qprint("  ^5{}^7: ^5{}^7 (^5{}^7)".format(index, image["Name"], image["Architecture"]))

def export_to_wim(image, filename, compression="max"):
    wim_filename = new_file_extension(filename, "wim")
    return dism("/Export-Image",
                "/SourceImageFile:{}".format(filename),
                "/SourceIndex:{}".format(image["Index"]),
                "/DestinationImageFile:{}".format(wim_filename),
                "/Compress:{}".format(compression),
    )
         
def esd_images(esd_file):
    global parser
    images = {}
    index = 0
    while True:
        index += 1
        try:
            lines = dism("/Get-WimInfo", "/WimFile:{}".format(esd_file), "/Index:{}".format(index)).split("\r\n")
            del lines[:6]; del lines[-5:] # clean up dism output
            data = {}
            for line in lines:
                split_line = line.split(" : ")
                data[split_line[0]] = split_line[1]
            images[index] = data
        except subprocess.CalledProcessError as e:
            if e.returncode == 87: # index does not exist
                break # out of images
            if e.returncode == 11: # image file not valid
                parser.error("{} is not a valid image file.".format(esd_file))
            raise e
    return images



# only run if running as Admin - DISM requires admin-level privileges
if not ctypes.windll.shell32.IsUserAnAdmin():
    parser.error("this script must be run with administrative rights.")

# only run if the specified ESD file actually exists.
if not os.path.isfile(args.esd_file):
    parser.error("{} cannot be found.".format(args.esd_file))

# only run if the specified ESD file is a valid MSWIM file.
with open(args.esd_file, "rb") as esd_file:
    if esd_file.read(8) != WIM_SIGNATURE:
        parser.error("{} is not a valid ESD/WIM file.".format(args.esd_file))

# don't run if an existing WIM file exists.
if os.path.isfile(new_file_extension(args.esd_file, "wim")):
    parser.error("{} already has a corresponding WIM file.".format(args.esd_file))



time_started = time.time()

images = esd_images(args.esd_file)

qprint("Found ^5{}^7 image indexes.".format(len(images)))

if args.verbose:
    print_image_info(images, args.esd_file)

qprint("^3Please wait patiently. The conversion process can take some time...^7")
for index, image in images.items():
    qprint("  Converting image index ^5{}^7 to WIM...".format(index), end=" ")
    try:
        output = export_to_wim(image, args.esd_file, compression=args.compression)
        qprint("^2Done.^7")
    except subprocess.CalledProcessError as e:
        qprint("^1DISM Error ^3{}^7:\n\n{}".format(e.returncode, e.output.decode()))
    except KeyboardInterrupt:
        parser.error("user cancelled operation.")
        

time_finished = time.time()

qprint("All conversions completed. Took ^5{}^7 seconds.".format(int(time_finished-time_started)))
