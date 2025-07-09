from __future__ import (absolute_import, division, print_function)
import configparser
import imagehash
import shutil
import os
from datetime import datetime, timedelta
from PIL import Image
import pickle
import time
from rich import print as rprint


# John's amazing lock screen capture tool
rprint("[bold italic red]John\'s Amazing Windows Lock Screen Capture Tool 2025")

rprint("Loading modules...")

# SECTION ONE: check whether there is an existing configuration, and if not create one
config = configparser.ConfigParser()


# Just a small function to write the file
def write_file():
    config.write(open('LSC.ini', 'w'))


if not os.path.exists('LSC.ini'):
    config['Lock Screen Capture'] = dict(
        input='C:/Users/JohnHoddinott/AppData/Local/Packages/Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy'
              '/LocalState/Assets', destination='D:/John/Pictures/Backgrounds/Lock images/', max_delay=28)
    write_file()
else:
    # Read File
    config.read('LSC.ini')
    # Get the list of sections
    # print(config.sections())
    # Print value at test2
    print('Input file location: ' + config.get('Lock Screen Capture', 'input'))


input_dir = config.get('Lock Screen Capture', 'input')
# print("Hidden Windows folder detected at: " + input_dir)
destination = config.get('Lock Screen Capture', 'destination')
# END SECTION ONE

# Identify timeframe for valid images
now = datetime.today()
max_delay = timedelta(days=config.getint('Lock Screen Capture', 'max_delay'))  # timedelta(days=28)
print("processing images downloaded within the last " + str(max_delay) + " hours")
# reload hashes from file
pickle_file = destination + 'hashes.pkl'
file2 = open(pickle_file, 'rb')
hashes = pickle.load(file2)
file2.close()


# Identify the next available sequential file name
def get_nonexistent_path(fname_path):
    """
    Get the path to a filename which does not exist by incrementing path.
    """
    if not os.path.exists(fname_path):
        return fname_path
    filename, file_extension = os.path.splitext(fname_path)
    i = 1
    new_fname = "{} {}{}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        i += 1
        new_fname = "{} {}{}".format(filename, i, file_extension)
    return new_fname


# Main body of the code
source = os.listdir(input_dir)
input_count = len([name for name in source])
proc_count = 0
lscape = 0
print("There are a total of " + str(input_count) + " files to process")
for files in source:
    path = os.path.join(input_dir, files)
    if not os.path.isdir(path):
        file_mod_time = datetime.fromtimestamp(os.stat(path).st_mtime)
        if now - file_mod_time <= max_delay:
            with Image.open(path) as im:
                width, height = im.size
                if width > height:  # We only want to capture landscape backgrounds
                    my_hash = imagehash.average_hash(im)
                    if my_hash not in hashes:
                        print(str(my_hash) + ' is a unique hash')
                        fname = get_nonexistent_path(destination + "Image.jpeg")
                        new_name = os.path.join(destination, fname)
                        shutil.copy(path, new_name)
                        print("Image being saved as " + new_name)
                        hashes.append(my_hash)
                        proc_count += 1
                        # else:
                        # print('Image is a duplicate')
                else:
                    lscape += 1
print(str(lscape) + " of the images were in Portrait format so discarded")
if proc_count != 0:
    print("There were " + str(proc_count) + " new images saved to disk")
print("The remaining " + str(input_count - lscape - proc_count) + " images were duplicates of ones already saved")
# Save the updated hashes list to the persistent store
if proc_count > 0:
    afile = open(pickle_file, 'wb')
    pickle.dump(hashes, afile)
    afile.close()
    print("Hash file successfully saved to disk")
else:
    print("Hash file does not not need updating")
time.sleep(5)
