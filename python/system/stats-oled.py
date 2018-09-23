#!/usr/bin/python3
from support import adafruit_oled as ada
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO
from time import sleep
import subprocess

def get_ip():

    cmd = 'hostname -I | cut -d\' \' -f1'
    output = subprocess.check_output(cmd, shell = True)
    # decoding bytes string:
    output_str = output.decode('utf-8').strip('\n')
    return output_str

def cpu_load():

    cmd = 'top -bn1 | grep \'load average\' | awk \'{printf \"%.2f\", $(NF-2)}\''
    output = subprocess.check_output(cmd, shell = True)
    # decoding bytes string:
    output_str = output.decode('utf-8').strip('\n')
    output_float = float(output_str)*100
    round_percent = '{0:.0f}'.format(output_float)

    return str(round_percent)


def mem_usage():

    cmd = "free -m | awk 'NR==2{printf \"%.0f%%\", $3*100/$2}'"
    # Detailed versions:
    #cmd = "free -m | awk 'NR==2{printf \"%s/%sMB %.0f%%\", $3,$2,$3*100/$2 }'"
    #cmd = "free -m | awk 'NR==2{printf \"Mem:%s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    output = subprocess.check_output(cmd, shell = True)
    # decoding bytes string:
    output_str = output.decode('utf-8').strip('\n')
    #output_float = float(output_str)

    return output_str


def disk_usage():

    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    output = subprocess.check_output(cmd, shell = True)
    # decoding bytes string:
    output_str = output.decode('utf-8').strip('\n')
    #output_float = float(output_str)

    return output_str


def temp():

    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    output = subprocess.check_output(cmd, shell = True)
    # decoding bytes string:
    output_str = output.decode('utf-8').strip('\n')
    output_float = int(output_str)/1000
    round_output = '{0:.2f}'.format(output_float)

    return str(round_output)


if __name__ == '__main__':

    '''
    It shows system stats on the OLED screen.

    Shell scripts for system monitoring form here:
    https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    '''


    disp = ada.OledBonnet()

    # Adafruit OLED Bonnet hardware settings
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(disp.a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    while True:

        current_ip = get_ip()
        current_cpu = cpu_load()
        memory = mem_usage()
        current_temp = temp()
        disk = disk_usage() # Not used for now

        disp.print_oled(['IP:'+current_ip, 'CPU:'+current_cpu+'% Mem:'+memory, 'Temp:'+current_temp+' C'])
        sleep(0.03)

        if not GPIO.input(disp.a_pin): # A button pressed.
            #sleep(0.05)
            break

    GPIO.cleanup()
