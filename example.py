"""Demonstration of event loop and state machine concepts."""
import RPi.GPIO as gpio
import time


def init_gpio():
    gpio.setmode(gpio.BOARD)
    gpio.setup(32, gpio.IN)
    gpio.setup(36, gpio.OUT)


# Define little helper functions so you can change the pin states in plain English.
def start_train():
    gpio.output(36, gpio.LOW)


def stop_train():
    gpio.output(36, gpio.HIGH)


def is_sensor_hit():
    return gpio.input(32) == 1


def main():
    # define possible train states, see the flowchart
    RUNNING = 0
    MAYBE = 1
    STATION = 2

    start_train()

    # Variables used to keep track of where the train is and how long it has
    # been there.  If you were running more than one train we might use
    # multiple sets of these.
    trainState = RUNNING
    framesAtStation = 0
    framesRunning = 0

    # An infinite loop is the hallmark of real-time software such as
    # fighter jets or model train controllers.  The numbers I use in here
    # assume the loop is running on a 5 Hz clock.  If you adjust the sleep
    # at the end of the loop, you'll have to change all the numbers
    # accordingly.
    while True:
        # Treat each state like an independent little program.  No sleeping
        # is necessary inside of the state machine because it's just going
        # to come around again.

        if trainState == RUNNING:
            framesRunning += 1
            # Gives the train 5 Hz * 2 seconds to escape the sensor before we start
            # checking whether it has made it around the track again.
            if framesRunning > 10 and is_sensor_hit():
                trainState = MAYBE

        elif trainState == MAYBE:
            # Require two high signals in a row trying to avoid electrical interference.
            if is_sensor_hit():
                # Notice how I'm only doing work on the transition between states.
                # Being disciplined about when you modify data is PROFESSIONAL.
                stop_train()
                trainState = STATION
                framesAtStation = 0
            else:
                trainState = RUNNING

        elif trainState == STATION:
            framesAtStation += 1
            if framesAtStation > 150:  # 5 Hz * 30 seconds
                start_train()
                trainState = RUNNING
                framesRunning = 0
            # There is no else case. Nothing is happening while the train
            # is stopped at the station, so the code does nothing but count
            # frames until we get to 30 seconds.

        else:
            print('Error: train in an unknown state', trainState)
            break

        # Before the loop restarts, sleep for 200 ms so we don't hog the processor.
        # Notice that this is inside the loop but outside all the if-statements.
        # I'm betting that this loop doesn't need to run faster than 5 Hz.
        time.sleep(0.2)


# I don't do anything at global scope except define functions.  This block runs
# automatically when you start the program.
if __name__ == '__main__':
    try:
        init_gpio()
        main()
    finally:
        gpio.cleanup()
