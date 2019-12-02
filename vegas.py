"""Copy of Auntie's Christmas village track code with different GPIO pins.
"""
from enum import Enum
import RPi.GPIO as gpio
import math
import time


# Defining constants to give names to GPIO pins. Adjust these numbers as
# needed, including to deconflict with another train being controlled by the
# same Pi.
SENSOR_STATION = 18
SENSOR_MOUNTAIN_L = 16
SENSOR_MOUNTAIN_R = 22
TRAIN_FORWARD = 8
TRAIN_BACKWARD = 10
TRAIN_VELOCITY = 12
INPUT_SHUTDOWN = 5
OUTPUT_SHUTDOWN = 13


# Defining constants for the different states.
class State(Enum):
    STATION = 1
    DEPARTING = 2
    OUTBOUND = 3
    INBOUND = 4
    SHUTTING_DOWN = 5
    SHUTDOWN = 6


def is_sensor_hit(pin):
    if gpio.input(pin) == 1:
        print('Sensor', pin)
        return 1
    else:
        return 0


# Because the behavior is symmetrical and the Pi doesn't control what direction
# the train goes (automatically reverses after hitting bumpers), we can reuse
# the code for both mountains.
class StateMachine():
    def __init__(self):
        self.state = State.DEPARTING
        self.startTime_sec = 0  # put units on your variable names
        self.soundPlayed = False
        self.sensorHits = 0
        self.shutdownHits = 0

        gpio.output(TRAIN_FORWARD, gpio.HIGH)
        gpio.output(TRAIN_BACKWARD, gpio.LOW)
        self.velo = gpio.PWM(TRAIN_VELOCITY, 1000)
        self.velo.start(65)  # Medium speed


    def transition(self, newState):
        print('Switching to', newState.name)
        self.state = newState
        self.startTime_sec = time.perf_counter()
        self.soundPlayed = False
        self.sensorHits = 0


    def check_shutdown(self):
        if self.state == State.SHUTDOWN or self.state == State.SHUTTING_DOWN:
            return
        if is_sensor_hit(INPUT_SHUTDOWN):
            self.shutdownHits += 1
        else:
            self.shutdownHits = 0
        if self.shutdownHits >= 2:
            if self.state == State.STATION:
                self.transition(State.SHUTDOWN)
            else:
                self.transition(State.SHUTTING_DOWN)


    def check_mountain_sensor(self):
        if is_sensor_hit(SENSOR_MOUNTAIN_L) or is_sensor_hit(SENSOR_MOUNTAIN_R):
            self.sensorHits += 1
        else:
            self.sensorHits = 0
        return self.sensorHits >= 2


    def check_station_sensor(self):
        if is_sensor_hit(SENSOR_STATION):
            self.sensorHits += 1
        else:
            self.sensorHits = 0
        return self.sensorHits >= 2


    def run(self):
        self.check_shutdown()

        # Compute how long we've been in the current state
        elapsed_sec = time.perf_counter() - self.startTime_sec

        if self.state == State.DEPARTING:
            # Play departure announcement and accelerate out of the station.
            # Start looking for the mountain reed.  As with the other script,
            # define the timings in reverse order so things don't get repeated.
            if elapsed_sec > 5:
                self.velo.ChangeDutyCycle(65)  # Medium speed
                if self.check_mountain_sensor():
                    self.transition(State.OUTBOUND)
            # Disabling smooth acceleration to avoid moving too slowly
            # through the curve when sharing power with the other train line.
            #elif elapsed_sec > 5:
                #speed = math.floor(elapsed_sec - 5) * 10 + 35
                #self.velo.ChangeDutyCycle(speed)
            elif not self.soundPlayed:
                # TODO: play 'Now departing station'
                self.soundPlayed = True

        elif self.state == State.OUTBOUND:
            # Come to an immediate stop inside the mountain to simulate
            # visiting some far-off station. After some time, set medium speed
            # to hit the bumper and reverse. Sit inside the mountain again, and
            # then approach the station.
            if elapsed_sec > 11:
                if self.check_mountain_sensor():
                    self.transition(State.INBOUND)
            elif elapsed_sec > 10:  # TODO: was 30, shortened for debugging.
                self.velo.ChangeDutyCycle(65)  # medium speed
            else:
                self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.INBOUND:
            if elapsed_sec > 11:
                if self.check_station_sensor():
                    self.transition(State.STATION)
            # Disabling smooth deceleration for now to avoid the possibility
            # of the train getting stuck at a bumper. If we ever miss a
            # sensor hit, we could be moving too slowly to reverse.
            #elif elapsed_sec > 12:
                # decelerate at 10 units per second
                #speed = 75 - math.floor(elapsed_sec - 12) * 10
                #self.velo.ChangeDutyCycle(speed)
            elif elapsed_sec > 10:  # TODO: was 30, shortened for debugging
                self.velo.ChangeDutyCycle(65)  # medium speed
            else:
                self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.STATION:
            if elapsed_sec > 10:  # TODO: was 30, shortened for debugging
                self.transition(State.DEPARTING)
            elif not self.soundPlayed:
                self.velo.ChangeDutyCycle(0)  # stopped
                # play 'Now arriving'
                self.soundPlayed = True

        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we reach the
            # station. It doesn't matter which direction we're facing.
            self.velo.ChangeDutyCycle(65)  # medium speed
            if self.check_station_sensor():
                self.transition(State.SHUTDOWN)

        elif self.state == State.SHUTDOWN:
            self.velo.ChangeDutyCycle(0)
            gpio.output(OUTPUT_SHUTDOWN, gpio.HIGH)
            time.sleep(5)  # TODO: Adjust this as needed to make sure master Pi
                           # sees the signal.
            return True


if __name__ == '__main__':
    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setup(SENSOR_STATION, gpio.IN)
    gpio.setup(SENSOR_MOUNTAIN_L, gpio.IN)
    gpio.setup(SENSOR_MOUNTAIN_R, gpio.IN)
    gpio.setup(INPUT_SHUTDOWN, gpio.IN)
    gpio.setup(TRAIN_FORWARD, gpio.OUT)
    gpio.setup(TRAIN_BACKWARD, gpio.OUT)
    gpio.setup(TRAIN_VELOCITY, gpio.OUT)
    gpio.setup(OUTPUT_SHUTDOWN, gpio.OUT)

    machine = StateMachine()
    try:
        isDone = False
        while not isDone:
            isDone = machine.run()
            time.sleep(0.02)  # 50 Hz clock
    except KeyboardInterrupt:
        print('Stopping manually')
    finally:
        print('Bye!')
        gpio.cleanup()
