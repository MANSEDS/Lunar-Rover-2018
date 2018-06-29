# MANSEDS Lunar Rover -- Drive Controller
# Author: Ethan Ramsay


# Import dependencies
import argparse
import RPi.GPIO as GPIO
import time
import logging
import json
import sys
import datetime
import os
import Adafruit_PCA9685


# Logging config
logging.basicConfig(filename='drive.log', level=logging.DEBUG)


# System variables
pi = 3.14159
wheel_diameter = 0.12 # m
wheel_width = 0.06 # m
axle_length = 0.18 # m
wheel_base = 0.155 # m
command_line_driven = True # Take commands from command line


# Import motor data including GPIO pin numbers, PWM channels & max RPM
try:
    with open('data/motor_data.json') as f:
        motor_data = json.load(f)
    max_rpm = motor_data["left bank"]["front motor"]["max rpm"]
    max_ang_vel = max_rpm * 2 * pi / 60
except FileNotFoundError:
    error_message = "Exiting with error. Motor data file missing. "
    print(error_message)
    with open('logs/error.log') as f:
        logged_error = str(datetime.datetime.now()) + error_message
        f.write(logged_error)
    sys.exit(1)


def reset_commands():
    commands = {
        "read" : False,
        "linear" : {
            "forward" : False,
            "backwards" : False,
            "distance" : 0,
            "speed" : 0
        },
        "rotational" : {
            "turn left" : False,
            "turn right" : False,
            "angle" : 0,
            "speed" : 0
        }
    }
    with open('commands/drive.cmnd', 'w+') as f:
        json.dump(commands, f)



def exit_with_error(pin):
    error_message = "Exiting with error. Motor status flag activated. "
    left_fault_message = "Fault indicated in left motor bank"
    right_fault_message = "Fault indicated in right motor bank"
    print(error_message)
    if pin == motor_data["left bank"]["status flag pin"]:
        error_message += left_fault_message
        print(error_message)
    else:
        error_message += right_fault_message
        print(error_message)
    with open('logs/error.log', 'a+') as f:
        logged_error = str(datetime.datetime.now()) + error_message
        f.write(logged_error)
    sys.exit(1)



def GPIO_set(motor_data):
    # Setup GPIO numbering
    GPIO.setmode(GPIO.BCM)

    # Get pin numbers
    enable = motor_data["enable pins"]
    status = [motor_data["left bank"]["status flag pin"][0],
                    motor_data["left bank"]["status flag pin"][1],
                    motor_data["right bank"]["status flag pin"][0],
                    motor_data["right bank"]["status flag pin"][1]]
    sec_inp = [] # Secondary input pins
    sec_inp.append(motor_data["left bank"]["front motor"]["secondary input pin"])
    sec_inp.append(motor_data["left bank"]["rear motor"]["secondary input pin"])
    sec_inp.append(motor_data["right bank"]["front motor"]["secondary input pin"])
    sec_inp.append(motor_data["right bank"]["rear motor"]["secondary input pin"])
    invert = [] # Invert pins
    invert.append(motor_data["left bank"]["invert pin"])
    invert.append(motor_data["right bank"]["invert pin"])

    # Set pins as inputs and outputs
    GPIO.setup(enable, GPIO.OUT)
    GPIO.setup(sec_inp, GPIO.OUT)
    GPIO.setup(invert, GPIO.OUT)
    GPIO.setup(status, GPIO.IN)

    # Set default output values
    GPIO.output(enable, 1) # If enable is not high, motors will not move
    GPIO.output(sec_inp, 0) # Keep the secondary input pin low as PWM pin varies
    GPIO.output(invert, 0) # Invert off by default

    # Add event detection on motor status flags
    for pin in status:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=exit_with_error)


def GPIO_forward():
    # Set invert pins to low
    invert = []
    invert.append(motor_data["left bank"]["invert pin"])
    invert.append(motor_data["right bank"]["invert pin"])
    GPIO.output(invert, 0)


def GPIO_backwards():
    # Invert direction of both banks
    invert = []
    invert.append(motor_data["left bank"]["invert pin"])
    invert.append(motor_data["right bank"]["invert pin"])
    GPIO.output(invert, 1)


def GPIO_left():
    # Invert left bank
    GPIO.output(motor_data["left bank"]["invert pin"], 1)
    GPIO.output(motor_data["right bank"]["invert pin"], 0)


def GPIO_right():
    # Invert right bank
    GPIO.output(motor_data["left bank"]["invert pin"], 0)
    GPIO.output(motor_data["right bank"]["invert pin"], 1)


# Adafruit setup
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
logging.debug('Set Adafruit pwm freq to 60')


# Calculate angular velocity for desired velocity
def calc_des_ang_vel(v):
    des_ang_vel = 2 * v / wheel_diameter # rad/s
    if des_ang_vel > max_ang_vel:
        if overdrive:
            des_ang_vel = max_ang_vel
            print("Desired velocity exceeds maximum velocity, velocity set to maximum due to" + \
                                "overdrive, extended use of overdrive is not recommended")
        else:
            des_ang_vel = max_ang_vel * 0.9
    elif des_ang_vel >= 0.9 * max_ang_vel:
        if not overdrive:
            des_ang_vel = 0.9 * max_ang_vel
    return des_ang_vel


# Calculate pulse length for velocity
def calc_pl(pl_min, pl_max, des_ang_vel):
    pl_range = pl_max - pl_min
    inter = pl_range * des_ang_vel / max_ang_vel
    per = inter / pl_range
    pl = pl_min + inter
    logging.debug("Calculated required pulse length for desired angular velocity: %s", pl)
    return int(pl), per


# Calculate time to turn by desired angle at 80% of max velocity
def turn_time(a):
    # Calculate turning diameter,d, using Pythagoras
    l1 = (axle_length + wheel_width) / 2 # m
    l2 = (wheel_base) / 2 # m
    d = (l1 ** 2 + l2 ** 2) ** (0.5) # m
    # Calculate angle turned through 1 revolution of tyres
    th = 360 * wheel_diameter / d * pi  # degrees
    # Calculate number of revolutions to turn by desired angle
    n = a / th # revs
    # Calculate revs/s of wheel at 80% max velocity
    om = max_rpm * 0.8 / 60
    # Calculate turn time
    t = 9 * n / om
    print(t)
    return t


# Calculate duration of motion to travel $distance at $speed
def calc_motion_duration(distance, speed):
    duration = distance / speed
    return duration


def actuate_motors(channels, pl):
    for channel in channels:
        pwm.set_pwm(channel, 0, pl);


if __name__ == "__main__":
    try:
        # Set up static motor logic pins
        GPIO_set(motor_data)

        # If run off command line
        if command_line_driven:
            # Arguments
            parser = argparse.ArgumentParser()


            # Command arguments
            g = parser.add_mutually_exclusive_group(required=True)
            gd = g.add_mutually_exclusive_group()
            gd.add_argument("-f", "--forward", help="Drive forwards", action="store_true")
            gd.add_argument("-b", "--backwards", help="Drive backwards", action="store_true")
            gt = g.add_mutually_exclusive_group()
            gt.add_argument("-l", "--left", help="Turn left", action="store_true")
            gt.add_argument("-r", "--right", help="Turn right", action="store_true")


            # Optional arguments
            parser.add_argument("-v", "--velocity", help="Drive velocity (m/s)")
            parser.add_argument("-d", "--duration", help="Drive duration (s)")
            parser.add_argument("-od", "--overdrive", help="Enable overdrive",
                                                action="store_true")
            parser.add_argument("-a", "--angle", help="Turn Angle (Degrees)")


            # Parse arguments
            args = parser.parse_args()
            f = args.forward
            b = args.backwards
            l = args.left
            r = args.right
            if args.velocity is not None:
                v = float(args.velocity)
            else:
                v = None
            if args.duration is not None:
                d = float(args.duration)
            else:
                d = None
            overdrive = args.overdrive
            if args.angle is not None:
                a = int(args.angle)
            else:
                a = None
            logging.debug("Arguments parsed: f=%s, b=%s, l=%s, r=%s, v=%s, d=%s, od=%s, a=%s", + \
                        f, b, l, r, v, d, overdrive, a)
            motor_channels = [
                motor_data["left bank"]["front motor"]["pwm channel"],
                motor_data["left bank"]["rear motor"]["pwm channel"],
                motor_data["right bank"]["front motor"]["pwm channel"],
                motor_data["right bank"]["rear motor"]["pwm channel"]
                ]



            # Main control
            if (f or b):
                if (v and d):
                    des_ang_vel = calc_des_ang_vel(v)
                    if f:
                        GPIO_forward()
                        for i in range(0,4,1):
                            # dc = calc_dc(motor_dc_limits[i[0]], motor_dc_limits[i[1]], des_ang_vel)
                            # m = motor_insts[i]
                            # m.start(dc)
                            pl, per = calc_pl(1, 4000, des_ang_vel)
                            pwm.set_pwm(motor_channels[i], 0, pl)
                        time.sleep(d)
                        for i in range(0, 4, 1):
                            # m = motor_insts[i]
                            # m.stop()
                            pwm.set_pwm(motor_channels[i], 0, 0)
                    elif b:
                        GPIO_backwards()
                        for i in range(0,4,1):
                            # dc = calc_dc(motor_dc_limits[i[0]], motor_dc_limits[i[1]], des_ang_vel)
                            # m = motor_insts[i]
                            # m.start(dc)
                            pl, per = calc_pl(1, 4000, des_ang_vel)
                            pwm.set_pwm(motor_channels[i], 0, pl)
                        time.sleep(d)
                        for i in range(0, 4, 1):
                            # m = motor_insts[i]
                            # m.stop()
                            pwm.set_pwm(motor_channels[i], 0, 0)
                else:
                    print("Please specify velocity AND duration of travel")
            elif (l or r):
                if a:
		    i=0
                    while a > 360:
                        a -= 360
                        i = i + 1
                        if i > 10:
                            print("Specify an angle between 0 and 360 degrees")
                            break

                    t = turn_time(a)
                    if l:
                        GPIO_left()
                        for i in range(0,4,1):
                            # dc = calc_dc(motor_dc_limits[i[0]], motor_dc_limits[i[1]], des_ang_vel)
                            # m = motor_insts[i]
                            # m.start(dc)
                            pl, per = calc_pl(1, 4000, 0.8*max_ang_vel)
                            pwm.set_pwm(motor_channels[i], 0, pl)
                        time.sleep(t)
                        for i in range(0, 4, 1):
                            # m = motor_insts[i]
                            # m.stop()
                            pwm.set_pwm(motor_channels[i], 0, 0)
                    elif r:
                        GPIO_right()
                        for i in range(0,4,1):
                            # dc = calc_dc(motor_dc_limits[i[0]], motor_dc_limits[i[1]], des_ang_vel)
                            # m = motor_insts[i]
                            # m.start(dc)
                            pl, per = calc_pl(1, 4000, 0.8*max_ang_vel)
                            pwm.set_pwm(motor_channels[i], 0, pl)
                            per = - per
                        time.sleep(t)
                        for i in range(0, 4, 1):
                            # m = motor_insts[i]
                            # m.stop()
                            pwm.set_pwm(motor_channels[i], 0, 0)
                else:
                    print("Please specify angle of turn (degrees)")


        else:
            # Running automatically off human machine interface
            while True:
                # Get commands from file
                with open('commands/drive.cmnd') as f:
                    commands = json.load(f)

                # Check if commands updated, if so then follow commands
                if commands["read"] == True:
                    if commands["linear"]["forward"] == True:
                        if commands["linear"]["distance"] != 0 and commands["linear"]["speed"] != 0:
                            pl, per = calc_pl(0, 4500, commands["linear"]["speed"])
                            GPIO_forward()
                            dur = calc_motion_duration(commands["linear"]["distance"],
                                commands["linear"]["speed"])
                            actuate_motors(motor_channels, pl)
                            time.sleep(dur)
                            actuate_motors(motor_channels, 0)
                    elif commands["linear"]["backwards"] == True:
                        if commands["linear"]["distance"] != 0 and commands["linear"]["speed"] != 0:
                            pl, per = calc_pl(0, 4500, commands["linear"]["speed"])
                            GPIO_backwards()
                            dur = calc_motion_duration(commands["linear"]["distance"],
                                commands["linear"]["speed"])
                            actuate_motors(motor_channels, pl)
                            time.sleep(dur)
                            actuate_motors(motor_channels, 0)
                    elif commands["rotational"]["turn left"] == True:
                        if commands["rotational"]["angle"] != 0 and \
                                commands["rotational"]["speed"] != 0:
                            pl, per = calc_pl(0, 4500, commands["linear"]["speed"])
                            GPIO_left()
                            dur = calc_motion_duration(commands["linear"]["distance"],
                                commands["linear"]["speed"])
                            actuate_motors(motor_channels, pl)
                            time.sleep(dur)
                            actuate_motors(motor_channels, 0)
                    elif commands["rotational"]["turn right"] == True:
                        if commands["rotational"]["angle"] != 0 and \
                                commands["rotational"]["speed"] != 0:
                            pl, per = calc_pl(0, 4500, commands["linear"]["speed"])
                            GPIO_right()
                            dur = calc_motion_duration(commands["linear"]["distance"],
                                commands["linear"]["speed"])
                            actuate_motors(motor_channels, pl)
                            time.sleep(dur)
                            actuate_motors(motor_channels, 0)
                    reset_commands()
                else:
                    time.sleep(0.3)


    finally:
        # GPIO clean up
        GPIO.cleanup()
        reset_commands()
