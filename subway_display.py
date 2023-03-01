import time
import threading
import RPi.GPIO as GPIO
from subway_times import get_subway_times_dict, get_subway_times_strings

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# consts & globals
N_ITEMS = 4
station = '125'

str_tmpl = r'({}) {}'
str_tmpl_all = r'{}: ({}) {}'

count = 0
DISPLAY_HEADSIGN = ''
subway_dict = {}

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
# Load default font.
font = ImageFont.load_default()

# 
reset_signal = threading.Event()

def change_headsign(channel):
    global subway_dict
    global count
    global DISPLAY_HEADSIGN
    DISPLAY_HEADSIGN = list(subway_dict.keys())[count % len(subway_dict)]

    reset_signal.set()
    count += 1

def smart_sleep(seconds: int):
    reset_signal.wait(timeout=seconds)


def print_helper(res_strs: list, n_lines: int, delay_sec: int, duration: int):
    global draw
    global image
    global disp

    seconds = 0
    pages = - (len(res_strs) // -n_lines)
    while seconds < duration:
        for pageno in range(0, pages):
            cur_top = top
            draw.rectangle((0,0,width,height), outline=0, fill=0)

            for lineno in range(0, n_lines):
                line = ''
                if lineno + pageno * n_lines < len(res_strs):
                    line = res_strs[lineno + pageno * n_lines]

                draw.text((x, cur_top), line, font=font, fill=255)
                cur_top += 8

            # Display image.
            disp.image(image)
            disp.display()
            smart_sleep(delay_sec)
            if reset_signal.is_set():
                reset_signal.clear()
                seconds = duration
            seconds += delay_sec


def main_loop():
    print('== Refreshing! ==')
    global DISPLAY_HEADSIGN
    global subway_dict
    subway_dict = get_subway_times_dict(station, N_ITEMS)
    if DISPLAY_HEADSIGN not in subway_dict.keys():
        DISPLAY_HEADSIGN = 'ALL'

    res_strs = []
    if DISPLAY_HEADSIGN == 'ALL':
        res_strs = get_subway_times_strings(subway_dict['ALL'], str_tmpl_all, True)
    else:
        res_strs = get_subway_times_strings(subway_dict[DISPLAY_HEADSIGN], str_tmpl)
        while len(res_strs) >= N_ITEMS:
            res_strs.pop()
        res_strs.insert(0, DISPLAY_HEADSIGN)

    print_helper(res_strs, 4, 2, 30)


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(17, GPIO.RISING, callback=change_headsign)

while True:
    main_loop()

