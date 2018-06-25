# MANSEDS Lunar Rover 2018 -- Actuator Test
# Author: Ethan Ramsay

"""
This test script cycles through all the actuators in the MANSEDS lunar rover.
This includes 4 motors and up to 12 servos.
The test cycles through all actuators and cycles through their respective pulse length ranges.
The direction of each motor is also inverted at each speed.
As such, when this script is run all actuators should be watched to ensure they act as
expected. If they do not, this is an indicator of fault in either hardware or wiring.
"""


# Import dependencies
import RPi.GPIO as GPIO
import time
import Adafruit_PCA9685
import sys
import json


# System variables
## Import motor data including GPIO pin numbers, PWM channels & max RPM
try:
    with open('data/motor_data.json') as f:
        motor_data = json.load(f)
except IOError:
    error_message = "Exiting with error. Motor data file missing. "
    print(error_message)
    with open('logs/error.log') as f:
        logged_error = str(datetime.datetime.now()) + error_message
        f.write(logged_error)
    sys.exit(1)
motor_channels = [12, 13, 14, 15]
## Motor Pins
enable = motor_data["enable pins"]
invert = [
        motor_data["left bank"]["invert pin"], motor_data["left bank"]["invert pin"]
]
second_input = [] # Secondary input pins - keep low
second_input.append(motor_data["left bank"]["front motor"]["secondary input pin"])
second_input.append(motor_data["left bank"]["rear motor"]["secondary input pin"])
second_input.append(motor_data["right bank"]["front motor"]["secondary input pin"])
second_input.append(motor_data["right bank"]["rear motor"]["secondary input pin"])
status_flag = [
        motor_data["left bank"]["status flag pin"][0],
        motor_data["left bank"]["status flag pin"][1],
        motor_data["right bank"]["status flag pin"][0],
        motor_data["right bank"]["status flag pin"][1]
] # If high, there is a problem with the motors on that bank


servo_channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


# GPIO setup/functions/cleanup
def GPIO_set():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(enable, GPIO.OUT)
    GPIO.setup(invert, GPIO.OUT)
    GPIO.setup(second_input, GPIO.OUT)
    GPIO.output(invert, 0)
    GPIO.output(second_input, 0)
    GPIO.output(enable, 1)
    GPIO.setup(status_flag, GPIO.IN)
    # Event detection for status flag
    for i in range(0, len(status_flag)):
        GPIO.add_event_detect(status_flag[i], GPIO.FALLING, callback=stop_with_warning)


def GPIO_clear():
    GPIO.cleanup()


# Adafruit setup
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)


# STOP & EXIT
def stop_with_warning():
    for i in servo_channels:
        pwm.set_pwm(i, 0, 0)
    for i in motor_channels:
        pwm.set_pwm(i, 0, 0)
    GPIO_clear()
    print("Motor fault flagged by status pin. Test failed. Test exiting.")
    sys.exit(1)


# Test actuators
def actuator_test():
    print("Watch all motors and servos. Do they all move? Do all the motors change direction?")
    for i in range(0,9):
        for j in servo_channels:
            pwm.set_pwm(j, 0, 100*i)
        for j in motor_channels:
            pwm.set_pwm(j, 0, 500*i)
        GPIO.output(invert, 1)
        time.sleep(2.5)
        GPIO.output(invert, 1)
        time.sleep(2.5)
    for i in range(0,9):
        for j in servo_channels:
            pwm.set_pwm(j, 0, 1000-100*i)
        for j in motor_channels:
            pwm.set_pwm(j, 0, 4500-500*i)
        GPIO.output(invert, 1)
        time.sleep(2.5)
        GPIO.output(invert, 1)
        time.sleep(2.5)
    for j in servo_channels:
        pwm.set_pwm(j, 0, 0)
    for j in motor_channels:
        pwm.set_pwm(j, 0, 0)
    print("If so then the actuator test has been passed. If not, test wiring and components.")

if __name__ == "__main__":
    try:
