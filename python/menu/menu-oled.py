#!/usr/bin/python3

#import sys
#sys.path.append("/home/pi/scripts/python/support")

from support import adafruit_oled as ada
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO
import time
import subprocess
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Setting up OLED display object
disp = ada.OledBonnet()

# Adafruit OLED Bonnet hardware settings
GPIO.setmode(GPIO.BCM)

GPIO.setup(disp.a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.up_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.down_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(disp.center_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize library.
disp.begin()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Clear display.
disp.clear()
disp.display()

# Constants
# ---------
FONT_PATH = '/home/pi/scripts/python/support/helvetica.ttf'

# First define some constants to allow easy resizing of shapes.
padding = -1
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 4
rect_width = 10
rect_length = 125


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
#draw.rectangle((0,0,width,height), outline=0, fill=0)

# Load default font.
#font = ImageFont.load_default()
# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype(FONT_PATH, 12)

class Screen(object):
    '''
    Holds position and content for a screen/OLED page that will be printed.
    '''

    def __init__(self, position, group):
        '''
        position = integer inidicating position of highlighted element in screen.
        group = list of items in a group.
        '''
        self.position = position
        self.group = group
        self.count = len(self.group)

    def rect_position(self):
        '''
        Returns a tuple with coordinates of highlight rectangle.
        **Assumes only three lines of the display will be used.**
        '''
        coord = (None,None)
        if self.position == 0:
            coord = (0, 0, rect_length, rect_width)
        if self.position == 1:
            coord = (0,rect_width, rect_length, rect_width+10)
        if self.position == 2:
            coord = (0,rect_width+10, rect_length, rect_width+20)
        return coord

    def generate_data(self):
        '''
        Generates a list of lists with item coordinates and data in the form of:

        [[(x,y), "text"], [(x,y), "text"], ...]

        **Assumes only three lines of the display will be used**.
        '''

        y = top-10
        list = []

        for item in self.group:
            y = y+10
            list.append([(x,y), item])

        return list


def print_oled(screen_object):
    '''
    screen_object: Screen object (custom class) holding all data that will be printed
    on the OLED screen.

    Prints OLED screen based on the screen object passed as argument.
    '''

    # Clear display.
    # disp.clear()
    # disp.display()
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)


    data = screen_object.generate_data()
    rect_coord = screen_object.rect_position()

    # Generating hollow rectangle outline:
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    draw.rectangle(rect_coord, outline=1, fill=0)
    # Generating screen items:
    for i in range(0,screen_object.count):
        draw.text(data[i][0], data[i][1] ,  font=font, fill=255)

    # Display image:
    disp.image(image)
    disp.display()

# Operation functions:

def shutdown():
    disp.print_oled(['Shutting down...', 'Wait for LEDs to', 'stop blinking.'])
    subprocess.call(['sudo', 'shutdown', 'now'])
    return

def backup_photos():
    subprocess.call(['python3', '/home/pi/scripts/python/photos/backup_photos-oled.py'])
    # Preventing options menu from being shown as soon as the backup
    # process finishes:
    GPIO.wait_for_edge(disp.a_pin, GPIO.FALLING)
    return

def quit_menu():
    # Exists menu and script.
    # Draw a black filled box to clear the image:
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    # Display image:
    disp.image(image)
    disp.display()
    sys.exit(0)

def rpi_stats():
    subprocess.call(['python3', '/home/pi/scripts/python/system/stats-oled.py'])
    return

# -- Main Script --
if __name__ == "__main__":

    print('Printing OLED screen ...')

    # Lines to be used in OLED display:
    lines = 3
    # Items and respective functions to be executed:
    items = ['Backup Photos', 'Statistics', 'Quit menu', 'Shutdown RPi']
    operations = [backup_photos, rpi_stats, quit_menu, shutdown]


    # Slicing items list on several lists with as many items as lines per screen:
    group_list = [items[i:i+lines] for i in range(0,len(items),lines)]

    # Generating screen data for each item in list:
    object_list = []
    for group in group_list:
        # each group is a list of items to be shown in a screen.
        for ix,item in enumerate(group):
            item_scrn = Screen(ix, group)
            object_list.append(item_scrn)


    show_screen=True
    index = 0
    print_oled(object_list[index])
    try:
        while True:

            if show_screen == True:

                if not GPIO.input(disp.down_pin): # down arrow pressed
                    index = index + 1

                if not GPIO.input(disp.up_pin):
                    index = index - 1

                if not GPIO.input(disp.b_pin):
                    print('{} option selected.'.format(items[index]))
                    operations[index]() #Note the '()' at the end.
                    # Uncomment to run the script just once.
                    #break

                if not GPIO.input(disp.center_pin): # joystick center pressed
                    # Toggles screen showing flag.
                    show_screen = not show_screen

                try:
                    print_oled(object_list[index])
                except IndexError:
                    index = 0

                time.sleep(0.05)

            else:
                # Draw a black filled box to clear the image:
                draw.rectangle((0,0,width,height), outline=0, fill=0)
                # Display image:
                disp.image(image)
                disp.display()

                if not GPIO.input(disp.center_pin):
                    show_screen = not show_screen
                time.sleep(0.05)

    except KeyboardInterrupt:
        GPIO.cleanup()

GPIO.cleanup()
