# MANSEDS Lunar Rover -- Motor Controller
# Author: Ethan Ramsay


# Import dependencies
import RPi.GPIO as GPIO
import time
import Adafruit_PCA9685
import logging


# Logging config
logging.basicConfig(filename='motor.log', level=logging.DEBUG)


# GPIO config
GPIO.setmode(GPIO.BCM)


# System variables
wheel_diameter = 0.12 # m
pi = 3.14159
max_rpm = 26
max_ang_vel = max_rpm * pi / 30 # rad/s


# GPIO setup/functions/cleanup
def GPIO_set(enable, invert, second_input, status_flag):
    GPIO.setup(enable, GPIO.OUT)
    GPIO.setup(invert, GPIO.OUT)
    GPIO.setup(second_input, GPIO.OUT)
    GPIO.setup(status_flag, GPIO.IN)


def GPIO_clear():
    GPIO.cleanup()


# Adafruit setup
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
logging.debug('Set Adafruit pwm freq to 60')


# Calculate angular velocity for desired velocity
def calc_des_ang_vel(v):
    des_ang_vel = 2 * v / wheel_diameter # rad/s
    if des_ang_vel > max_ang_vel:
        if od:
            des_ang_vel = max_ang_vel
            print("Desired velocity exceeds maximum velocity, velocity set to maximum due to" + \
                                "overdrive, extended use of overdrive is not recommended")
        else:
            des_ang_vel = max_ang_vel * 0.9
    elif des_ang_vel >= 0.9 * max_ang_vel:
        if not od:
            des_ang_vel = 0.9 * max_ang_vel
    logging.debug("Calculated required angular velocity for desired velocity: %s", des_ang_vel)
    return des_ang_vel


def calc_dc(dc_min, dc_max, des_ang_vel):
    dc_range = dc_max - dc_min
    inter = dc_range * des_ang_vel / max_ang_vel
    dc = dc_min + inter
    logging.debug("Calculated required duty cycle for desired angular velocity: %s", dc)
    return dc


def calc_pl(pl_min, pl_max, des_ang_vel):
    pl_range = pl_max - pl_min
    inter = pl_range * des_ang_vel / max_ang_vel
    pl = pl_min + inter
    logging.debug("Calculated required pulse length for desired angular velocity: %s", pl)
    return int(pl)


if __name__ == "__main__":

    import argparse

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("v", help="Velocity (m/s)")
    parser.add_argument("t", help="Operation time (s)")

    # Arguments for direct GPIO control from Pi
    parser.add_argument("en", help="Enable Pin No. (BOARD)")
    parser.add_argument("inv", help="Invert Pin No. (BOARD)")
    parser.add_argument("inp", help="Secondary Input Pin No. (BOARD)")
    parser.add_argument("stat", help="Status Flag Pin No. (BOARD)")
    # parser.add_argument("dc_min", help="Minimum Duty Cycle")
    # parser.add_argument("dc_max", help="Maximum Duty Cycle")
    # parser.add_argument("pwm", help="PWM Pin No. (BOARD)")

    # Arguments for Adafruit PWM hat control
    parser.add_argument("pl_min", help="Minimum Pulse Length")
    parser.add_argument("pl_max", help="Maximum Pulse Length")
    parser.add_argument("channel", help="Channel No. (Adafruit PWM Hat)")

    # Optional arguments
    parser.add_argument("--od", help="Overdrive Enable", action="store_true")

    # Parse arguments
    args = parser.parse_args()
    v = float(args.v)
    t = float(args.t)
    en = int(args.en)
    inv = int(args.inv)
    inp = int(args.inp)
    stat = int(args.stat)
    # dc_min = float(args.dc_min)
    # dc_max = float(args.dc_max)
    # pwm = int(args.pwm)
    pl_min = float(args.pl_min)
    pl_max = float(args.pl_max)
    channel = int(args.channel)
    od = args.od
    if args.od:
        print("Overdrive enabled, not recommended for extended durations")
    logging.debug("Arguments parsed: v=%s, t=%s, en=%s, inv=%s, inp=%s, stat=%s, " + \
                            "pl_min=%s, pl_max=%s, channel=%s od=%s", v, t, en, inv, inp, stat, + \
                            pl_min, pl_max, channel, od)


    # Calculate angular velocity for desired velocity
    des_ang_vel = calc_des_ang_vel(v)
    print("Desired angular velocity is: "+str(des_ang_vel))


    # Calculate interpolated duty cycle
    # dc = calc_dc(dc_min, dc_max, des_ang_vel)
    # print("Required duty cycle is: "+str(dc))


    # Calculate interpolated pulse length
    pl = calc_pl(pl_min, pl_max, des_ang_vel)
    print("Required pulse length is: "+str(pl))


    # Setup Motor GPIO pins
    GPIO_clear()
    GPIO_set(en, inv, inp, stat)


    # Activate motor through GPIO
    # GPIO_set(pwm, dc)
    # time.sleep(t)
    # GPIO_clear()


    # Activate motor through Adafruit PWM hat
    print("Start motor")
    pwm.set_pwm(channel, 0, pl)
    time.wait(t)
    pwm.set_pwm(channel, 0, 0)

    print("Motion completed")
