import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Constants
# ---------

FONT_PATH = '/home/pi/scripts/python/support/helvetica.ttf'

# Input pins:
L_pin = 27
R_pin = 23
C_pin = 4
U_pin = 17
D_pin = 22

A_pin = 5
B_pin = 6

# Raspberry Pi pin configuration:
RST = None
#RST = 24

# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Move left to right keeping track of the current x position for drawing shapes.
x = 4
rect_width = 10
rect_length = 125

# Load default font.
#font = ImageFont.load_default()
# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype(FONT_PATH, 12)


class OledBonnet(Adafruit_SSD1306.SSD1306_128_32):
    def __init__(self):
        Adafruit_SSD1306.SSD1306_128_32.__init__(self, rst=RST)
        self.left_pin = L_pin
        self.right_pin = R_pin
        self.center_pin = C_pin
        self.up_pin = U_pin
        self.down_pin = D_pin
        self.a_pin = A_pin
        self.b_pin = B_pin

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        # width and height are inherited from Adafruit original class.
        self.pil_image = Image.new('1', (self.width, self.height))
        self.pil_draw = ImageDraw.Draw(self.pil_image)

    def print_oled(self, line_list):
        '''
        Prints three lines on the OLED screen.

        line_list: list with **three items** representing each line
        of the OLED screen.

        **Assumes only three lines of the display will be used.**
        '''
        lines = 3
        # First define some constants to allow easy resizing of shapes.
        padding = - 1
        top = padding
        bottom = self.height-padding # not used.

        # Draw a black filled box to clear the image.
        self.pil_draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

        y = top-10
        for item in range(0,lines): # Iterates only over the first three elements of the list.
            y = y+10
            self.pil_draw.text((x,y), line_list[item], font=font, fill=255)

        # Display image:
        self.image(self.pil_image)
        self.display()
