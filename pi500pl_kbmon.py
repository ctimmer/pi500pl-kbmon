# -*-coding:utf-8 -*-
################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2026 Curt Timmerman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################
#
# Written by Curt Timmerman & Google
# Key mapping:
#   C - CPU load
#   I - Disk IO
#   M - Memory usage
#   N - NVME temperature
#   T - CPU temperature
#

import time
import psutil
from RPiKeyboardConfig import RPiKeyboardConfig
import colorsys

SLEEP_TIME = 0.5            # reading increment
KEY_MATRIX = {              # US keyboard
    # keyboard top row
    "esc" : [0, 0] ,
    "F1" : [0, 1] ,
    "F2" : [0, 2] ,
    "F3" : [0, 3],
    "F4" : [0, 4],
    "F5" : [0, 5],
    "F6" : [0, 6],
    "F7" : [0, 7],
    "F8" : [0, 8],
    "F9" : [0, 9],
    "F10" : [0, 10],
    "F11" : [0, 11],
    "F12" : [0, 12],
    "prtscn" : [0, 13] ,
    "delete" : [0, 14] ,
    # keyboard row 2
    "~" : [1, 0] ,
    "0" : [1, 10] ,
    "-" : [1, 11] ,
    "=" : [1, 12] ,
    "bs" : [1, 14] ,
    "pgup" : [1, 15] ,
    # keyboard row 3
    "tab" : [2, 0] ,
    "T" : [2, 6] ,
    "I" : [2, 9] ,
    "pgdn" : [2, 15] ,
    # keyboard row 4
    "capslock" : [3, 0] ,
    "D" : [3, 4] ,
    "F" : [3, 5] ,
    "home" : [3, 15] ,
    # keyboard row 5
    "C" : [4, 4] ,
    "N" : [4, 7] ,
    "M" : [4, 8]
    }
TEST_KEY = "home"
DISK_IO_MATRIX = KEY_MATRIX ["I"]   # keyboard row, column

BRIGHTNESS_MAX = 255        # 0-255

BYTES_IO_MIN = 0            # No indicated activity below this value
BYTES_IO_MAX = 500_000      # Sets highest activity brightness
BYTES_IO_DIV = BYTES_IO_MAX // BRIGHTNESS_MAX

CPU_LOAD_MATRIX = KEY_MATRIX ["C"]

CPU_TEMP_MATRIX = KEY_MATRIX ["T"]
CPU_TEMP_WARN = 50.0
CPU_TEMP_CRITICAL = 60.0

NVME_TEMP_MATRIX = KEY_MATRIX ["N"]

MEMORY_MATRIX = KEY_MATRIX ["M"]
MEMORY_TOTAL = None
MEMORY_WARN = 80.0
MEMORY_CRITICAL = 90.0

# Function to convert RGB to HSV (HSV values range from 0-255 in the library)
def rgb_to_hsv_pi(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    return [int(h * 255), int(s * 255), int(v * 255)]

# Define some colors using the converter
RED = rgb_to_hsv_pi(255, 0, 0)
GREEN = rgb_to_hsv_pi(0, 255, 0)
BLUE = rgb_to_hsv_pi(0, 0, 255)
YELLOW = rgb_to_hsv_pi (255, 255, 0)
ORANGE = rgb_to_hsv_pi (255,165,0)
OFF = (0, 0, 0) # Turn an LED off

all_leds = None
last_reading = None

def get_disk_io () :
    disk_io = psutil.disk_io_counters ()
    return disk_io._asdict()

def disk_io_diff (disk_io_last, disk_io_curr) :
    diff = {}
    for _, (io_id, io_val) in enumerate (disk_io_last.items ()) :
        diff [io_id] = disk_io_curr [io_id] - disk_io_last [io_id]
    return diff

keyboard = RPiKeyboardConfig ()     # keyboard setup
current_idx = keyboard.get_current_preset_index()
keyboard.set_led_direct_effect()
all_leds = keyboard.get_leds()      # For resetting
#
keyboard.set_led_by_matrix (matrix = DISK_IO_MATRIX ,
                           colour = OFF)
keyboard.set_led_by_matrix (matrix = CPU_LOAD_MATRIX ,
                           colour = OFF)
keyboard.set_led_by_matrix (matrix = CPU_TEMP_MATRIX ,
                           colour = OFF)
keyboard.set_led_by_matrix (matrix = MEMORY_MATRIX ,
                           colour = OFF)
# For testing KB mapping
#keyboard.set_led_by_matrix (matrix = KEY_MATRIX[TEST_KEY] ,
#                           colour = BLUE)
keyboard.send_leds()

util = psutil.virtual_memory ()
MEMORY_TOTAL = util.total   # Not used at this time

util = psutil.sensors_temperatures()
NVME_TEMP_CRITICAL = util["nvme"][0]._asdict()["critical"]
NVME_TEMP_WARN = NVME_TEMP_CRITICAL - 10

last_reading = get_disk_io ()
time.sleep (SLEEP_TIME)

def update_keyboard () :
    global last_reading
    while True :
        # disk io
        curr_io = get_disk_io ()
        diff_io = disk_io_diff (last_reading, curr_io)
        last_reading = curr_io
        bytes_io = diff_io["read_bytes"] + diff_io["write_bytes"]
        #print (bytes_io)
        brightness = 0
        color = RED
        if bytes_io > BYTES_IO_MIN :
            if bytes_io >= BYTES_IO_MAX :
                brightness = BRIGHTNESS_MAX
            else :
                brightness = bytes_io // BYTES_IO_DIV
        #print ("br=", brightness)
            color [2] = brightness
        else :
            color = GREEN
            brightness = 127
        color [2] = brightness
        keyboard.set_led_by_matrix (matrix = DISK_IO_MATRIX,
                                   colour = color)
        # CPU load
        cpu_load = psutil.cpu_percent()
        if cpu_load < 50.0 :
            color = GREEN
            color[2] = 127
        else :
            color = RED
            color[2] = int (round ((cpu_load * 2.55), 0))
        keyboard.set_led_by_matrix (matrix = CPU_LOAD_MATRIX,
                                   colour = color)
        # Temperatures
        temp_stats = psutil.sensors_temperatures()
        # cpu
        cpu_temp = temp_stats["cpu_thermal"][0]._asdict()["current"]
        #cpu_temp = temp_stats ["current"]
        color = GREEN
        color[2] = 127
        if cpu_temp >= CPU_TEMP_WARN :
            if cpu_temp >= CPU_TEMP_CRITICAL :
                color = RED
                color[2] = int(round((cpu_temp * 2.55), 0))
            else :
                color = ORANGE
                color[2] = int(round((cpu_temp * 2.55), 0))
        keyboard.set_led_by_matrix (matrix = CPU_TEMP_MATRIX ,
                                   colour = color)
        # nvme
        nvme_temp = temp_stats["nvme"][0]._asdict()["current"]
        color = GREEN
        color[2] = 127
        if nvme_temp >= NVME_TEMP_WARN :
            if nvme_temp >= NVME_TEMP_CRITICAL :
                color = RED
                color[2] = int (round ((nvme_temp * 2.55), 0))
            else:
                color = ORANGE
                color[2] = int (round((nvme_temp * 2.55), 0))
        keyboard.set_led_by_matrix (matrix=NVME_TEMP_MATRIX,
                                   colour=color)
        # Memory usage
        memory_stats = psutil.virtual_memory()
        usage_pc = memory_stats.percent
        color = GREEN
        color[2] = 127
        if usage_pc >= MEMORY_CRITICAL :
            color = RED
            color[2] = int(round((usage_pc * 2.55), 0))
        elif usage_pc >= MEMORY_WARN :
            color = ORANGE
            color[2] = int(round((usage_pc * 2.55), 0))
        keyboard.set_led_by_matrix (matrix = MEMORY_MATRIX,
                                   colour = color)
        #
        # Update keyboard leds
        keyboard.send_leds()
        time.sleep (SLEEP_TIME)

try :
    update_keyboard ()
except BaseException as e :     # catch all exceptions
    print ("Exception in update_keyboard:", e)

print ("Clean up")
for led in all_leds:
    keyboard.set_led_by_idx (idx = led.idx,
                             colour = led.colour)
keyboard.send_leds()
