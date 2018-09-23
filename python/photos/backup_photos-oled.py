#!/usr/bin/python3

import os
import sys
import subprocess
import re

from datetime import datetime
from time import sleep
from support import adafruit_oled as ada
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO

def read_configuration():
    '''
    Reads the script configuration file.
    '''
    
    try:

        with open(CONFIG_FILE, 'rU') as file: #IMPORTANT: rU Opens the file with Universal Newline Support, so \n and/or \r is recognized as a new line.
            
            confList = file.readlines()
            for line in confList:
                line = line.strip('\n')

                try:
                    name , value = line.split('=')
                    if name.strip() == 'mount folder': #.strip eliminates leading and ending spaces only.
                        mount_path = value.strip()
                    elif name.strip() == 'excluded folders':
                        excld_folders = value.strip().split(',') #transforms the string of words into a list.
                
                except ValueError:
                    print ('Incorrect line format in configuration file.\nExiting.')
                    disp.print_oled(['Error:','Incorrect format','in config file.'])
                    sys.exit(1)

    except FileNotFoundError:

        print ('Error: File not found!.')
        disp.print_oled(['Error:','File not found.',''])
        sys.exit(1)

    return (mount_path, excld_folders)

def read_drive(driveType):
    '''
    Returns a folder selected through the OLED bonnet. Uses global variables
    for drive mounting point/folder and excluded folders.

    '''

    global mountFolder
    global excluded_folders

    choice = None

    for folder in os.listdir(mountFolder):
        if folder not in excluded_folders:

            disp.print_oled([driveType+' drive',folder+' ? [Y]', '              [N]'])

            while True:
                if not GPIO.input(disp.b_pin):
                    choice = folder
                    excluded_folders.append(folder) #exclude selected folder from future choices.
                    break
                if not GPIO.input(disp.a_pin):
                    break
                sleep(0.05)

            if choice != None: #breaks out of the "for" loop if the choice is made.
                break

    return choice


def create_folder(path):
    '''
    Checks if the destination folder is present in the destination drive.
    If it's not, it attempts to create it.
    '''

    print ('attempting to create destination folder: ',path)
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            print ('Folder created.')
        except:
            print ('Folder could not be created. Stopping.')
            disp.print_oled(['Error:', 'Folder could not', 'be created.'])
            return
    else:
        print ('Folder already in path. Using that one instead.')


def calc_percent(matched_string):
    '''
    matched_string = bytes string.

    Receives a byte string (binary string) in the form b'x/y' and returns a calculated
    percentage in integer form.
    '''

    # decoding bytes string into text string and getting each component
    # from x / y
    str_list = matched_string.decode('utf-8').split('/')
    percent = 100-(int(str_list[0])/int(str_list[1]))*100
    return int(percent)

if __name__ == '__main__':

    '''
    This script copies the contents of a mounted SD card to a mounted drive 
    selected through Adafruit's Bonnet OLED device. If the destination folder 
    doesn't exist, it is automatically created with the SD Card's name.

    .conf file contains the list of excluded folders (comma separated) and
    the system mounting folder. 

    The script can be run from the CLI with two arguments:
    
    Origin drive label
    Destination drive label

    If any of these arguments is omitted, the OLED bonnet is used for
    interaction with the user.
    '''

    # Constants
    # ---------
    CONFIG_FILE = '/home/pi/scripts/python/photos/backup_photos.conf'

    # Setting up OLED display object
    disp = ada.OledBonnet()

    # Adafruit OLED Bonnet hardware settings
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(disp.a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(disp.b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(disp.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(disp.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(disp.up_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(disp.down_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(disp.center_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    # Reads configuration file and assigns variables.
    mountFolder, excluded_folders = read_configuration()
    
    # Checks if origin drive is passed as an argument.
    # If not, gets it from the OLED interface.
    try:
        originDrive = sys.argv[1]
        destDrive = sys.argv[2]

        if not os.path.exists(os.path.join(mountFolder, originDrive)):
            print ('Error: Origin drive not mounted.\nExiting.')
            disp.print_oled(['Error:','Origin drive', 'not mounted.'])
            sys.exit(1)
        elif not os.path.exists(os.path.join(mountFolder, destDrive)):
            print ('Error: Destination drive not mounted.\nExiting.')
            disp.print_oled(['Error:','Dest. drive', 'not mounted.'])
            sys.exit(1)

    except IndexError:
        originDrive = read_drive('Origin')
        destDrive = read_drive('Destination')

    if originDrive == None or destDrive == None:
        print ('Origin or destination drive not selected.\nExiting.')
        disp.print_oled(['Error: Origin','or dest. drive', 'not selected.'])
        sys.exit(1)

    else:
        # Verifying if both origin and destination folders are mounted points.
        # os.path.exists() can also be used.
        if os.path.ismount(os.path.join(mountFolder,destDrive)) and os.path.ismount(os.path.join(mountFolder,originDrive)):

            #destFolder = mountFolder+destDrive+'/'+originDrive
            destFolder = os.path.join(mountFolder,destDrive,originDrive)
            create_folder(destFolder)
            disp.print_oled(['Initiating','backup...',''])

            print (datetime.now().strftime('%Y-%m-%d %H:%M')+' Backup process initiated...')

            cmd = ['rsync', '-a', '--no-inc-recursive', '--progress', '--delete', '--info=name0', mountFolder+originDrive+'/', destFolder]

            # Compiled with 'b' because p.stdout returns a bytes string.
            rgx = re.compile(b'.*to\-chk=(.+)\)')

            # Popen used to interact with stdout (command line) as commands are run.
            p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            for line in p.stdout:
                matched_obj = rgx.match(line)
                try:
                    p_num = calc_percent(matched_obj.group(1))
                    print('Percentage completed: {} %'.format(p_num))
                    disp.print_oled(['Backing up files','to '+destDrive , str(p_num)+' % completed'])

                except AttributeError:
                    # Raised when the line doesn't match the RegEx
                    pass

            print (datetime.now().strftime('%Y-%m-%d %H:%M')+' Backup process finished.')

            disp.print_oled(['Backup to', destDrive, 'finished!'])

        else:
            print ("Error with mounted drives. Possible issues:\na) Origin drive "+mountFolder+originDrive+" is not mounted.\
                \nb) Destination drive "+mountFolder+destDrive+" is not mounted.\
                \nc) SD Card has a different name.")

            disp.print_oled(['Error:', 'Issue with', 'mounted drives.'])
