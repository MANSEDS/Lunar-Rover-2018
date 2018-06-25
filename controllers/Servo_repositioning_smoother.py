# MANSEDS Lunar Rover -- Servo Repositioning Smoother
# Author: Ethan Ramsay

# Abbreviations:
# GPIO = general purpose input/output
# dc = duty cycle
# pl = pulse length
# pin = IO pin no.


# Import dependencies
import RPi.GPIO as GPIO
import logging
import Adafruit_PCA9685
import time
import json


# Logging config
logging.basicConfig(filename='servo.log', level=logging.WARNING)


# System variables
position_info_file = "servo_position_data.json"


# Import position data
with open(position_info_file) as f:
    raw_json = f.read()
    positions = raw_json.load(raw_json)
    angles = positions[0]
    pls = positions[1]


# PWM functions
def calc_dc(dc_min, dc_max, angle):
    dc_range = dc_max - dc_min
    inter = dc_range * angle / 180
    dc = dc_min + inter
    logging.debug("Calculated required duty cycle for desired servo angle: %s", dc)
    return dc


def calc_pl(pl_min, pl_max, angle):
    pl_range = servo_max - servo_min
    inter = pl_range * angle / 180
    pl = pl_min + inter
    logging.debug("Calculated required pulse length for desired servo angle: %s", pl)
    pl = int(pl)
    return pl

# Get original position
def get_starting_pos(angles, channel):
    angle = int(angles[channel])


# Smooth movement
def move_smooth(angles, des_angles):
    for channel in angles.count():
        if abs(int(angles[channel]) - int(angles[channel])) > 5:
            new_angle = angles[channel] + 5
        elif int(angles[channel]) != int(angles[channel]):
            new_angle = des_angles[channel]
