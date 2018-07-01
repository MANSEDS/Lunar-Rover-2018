# MANSEDS Lunar Rover -- Arm Controller
# Author: Ethan Ramsay


# Import dependencies
import argparse
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import numpy as np
import logging
import json
import time


# Logging config
logging.basicConfig(filename='arm.log', level=logging.DEBUG)


# System variables
command_line_driven = True # Take commands from command line


# Import arm data including PWM channels, DH notation and joint servos
try:
    with open('data/arm_data.json') as f:
        arm_data = json.load(f)
except IOError:
    error_message = "Exiting with error. Arm data file missing. "
    print(error_message)
    with open('logs/error.log') as f:
        logged_error = str(datetime.datetime.now()) + error_message
        f.write(logged_error)
    sys.exit(1)


def reset_commands():
    commands = {
        "read" : False,
        "preset target": False,
        "presets" : {
            "deposit" : False,
            "extend" : False,
            "stow" : False
        },
        "target" : {
            "x" : False,
            "y" : False,
            "z" : False
        }
    }
    with open('commands/arm.cmnd', 'w+') as f:
        json.dump(commands, f)


# Setup Adafruit PWM Hat
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
logging.debug("Adafruit PWM freq set to 60")


# Positioning functions
def calc_servo_angles(target_vector):
    logging.debug("Desired gripper position vector: %s", target_vector)
    inverse_kinematics_solver(target_vector, arm_data)
    logging.debug("Calculated servo angles: %s", servo_angles)
    return servo_angles


def calc_pl(pl_min, pl_max, angle):
    pl_range = servo_max - servo_min
    inter = pl_range * angle / 180
    pl = pl_min + inter
    logging.debug("Calculated required pulse length for desired servo angle: %s", pl)
    pl = int(pl)
    return pl


# Control functions
def extend():
    val = 1
    while True:
        pwm.set_pwm(0, 0, pl_limits_arm[0][1]/5)
        pwm.set_pwm(1, 0, pl_limits_arm[1][1]/5)
        pwm.set_pwm(2, 0, pl_limits_arm[2][1]/5)
        pwm.set_pwm(3, 0, pl_limits_arm[3][1]/5)
        pwm.set_pwm(4, 0, pl_limits_arm[4][1]/5)
        pwm.set_pwm(5, 0, pl_limits_grip[0][1]/5)
        pwm.set_pwm(6, 0, pl_limits_grip[1][1]/5)
        if val > 0:
            logging.debug("Arm extended")
            val -= 1


def stow():
    val = 1
    while True:
        pwm.set_pwm(0, 0, pl_limits_arm[0][0])
        pwm.set_pwm(1, 0, pl_limits_arm[1][0])
        pwm.set_pwm(2, 0, pl_limits_arm[2][0])
        pwm.set_pwm(3, 0, pl_limits_arm[3][0])
        pwm.set_pwm(4, 0, pl_limits_arm[4][0])
        pwm.set_pwm(5, 0, pl_limits_grip[0][0])
        pwm.set_pwm(6, 0, pl_limits_grip[1][0])
        if val == 1:
            logging.debug("Arm stowed")
            val -= 1


def deposit_pos():
    val = 1
    while True:
        pwm.set_pwm(0, 0, deposit_pl[0])
        pwm.set_pwm(1, 0, deposit_pl[1])
        pwm.set_pwm(2, 0, deposit_pl[2])
        pwm.set_pwm(3, 0, deposit_pl[3])
        pwm.set_pwm(4, 0, deposit_pl[4])
        pwm.set_pwm(5, 0, deposit_pl[5])
        pwm.set_pwm(6, 0, deposit_pl[6])
        if val == 1:
            logging.debug("Gripper positioned above ice box")
            val -= 1


def position_gripper(target_vector):
    a = calc_servo_angles(target_vector)
    pl = [0, 0, 0, 0, 0]
    val = 1
    for i in range(0, 5, 1):
        pl[i] = calc_pl(pl_limits_arm[i][0], pl_limits_arm[i][1], a[i])
    while True:
        for i in range(0, 5, 1):
            pwm.set_pwm(i, 0, pl)
        if val == 1:
            logging.debug("Arm position command called for target vector: {}".format(target_vector))
            logging.debug("Calculated pulse lengths to achieve target vector: {}".format(pl))
            val -= 1


# Main
if __name__ == "__main__":
    try:

        # Takes commands from command line
        if command_line_driven:
            # Arguments
            parser = argparse.ArgumentParser()
            g = parser.add_mutually_exclusive_group(required=True)
            ge = g.add_mutually_exclusive_group()
            ge.add_argument("-e", "--extend", help="Extend arm", action="store_true")
            ge.add_argument("-s", "--stow", help="Stow arm", action="store_true")
            gp = g.add_mutually_exclusive_group()
            gp.add_argument("-p", "--position", help="Gripper Position Vector")
            gp.add_argument("-i", "--icebox", help="Position gripper above ice box to deposit sample")
            gg = g.add_mutually_exclusive_group()
            gg.add_argument("-g", "--grip", help="Grip", action="store_true")
            gg.add_argument("-d", "--drop", help="Release grip", action="store_true")
            args = parser.parse_args()
            if args.extend:
                e = args.extend
            else:
                extend = False
            if args.extend:
                e = args.stow
            else:
                extend = False
            if args.position:
                e = args.position
            else:
                position = False
            if args.icebox:
                e = args.icebox
            else:
                icebox = False
            s = args.stow
            p = args.position # <-- convert from string into ??? format???
            dep = args.icebox
            logging.debug("Arguments parsed: e=%s, s=%s, p=%s", + \
                                e, s, p)


            if (e or s):
                # GPIO_arm()
                if e:
                    extend()
                elif s:
                    stow()
            elif p or dep:
                # GPIO_arm()
                position_gripper(p)


        # Use commands generated from human machine interface
        else:
            reset_commands()
            while True:
                # Get commands from file
                with open('commands/arm.cmnd') as f:
                    commands = json.load(f)

                # Check if commands updated, if so then follow commands
                if commands["read"] == True:
                    if commands["preset target"] == True:
                        if commands["presets"]["deposit"]:
                            pass
                    elif commands["preset target"] == True:
                        if commands["presets"]["extend"]:
                            pass
                    elif commands["preset target"] == True:
                        if commands["presets"]["stow"]:
                            pass
                else:
                    time.sleep(0.3)

    finally:
        reset_commands()
