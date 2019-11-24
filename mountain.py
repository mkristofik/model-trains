"""Auntie's Christmas village track involving a mountain.  Expected behavior
copied from Dad's email:
    - trolley would start at station and accelerate to max speed.
    - inside mountain trolley would stop at mountain reed for specified period.
    - Trolley would leave mountain and decelerate approaching the
      station...deceleration start would be either a 3rd reed or a timing
      function from mountain reed since low medium and high speeds can be
      measured.
    - trolley would stop at station reed for a period of time
    - Station master would announce "Welcome to Xmas village" station.
    - Prior to departure station master would announce "all aboard" and a couple of toots
    - repeat or maybe, complicating the issue but adding variety, trolley does
      the next lap without stopping/decelerating at either reeds until  it
      decelerates and stops at station again after doing a full circle without
      stopping
      then repeat.
    - One final procedure not yet determined....before power shutdown and yet
      TBD how it's commanded, trolley is sitting at station.
"""
from enum import Enum
import math
import time


# Defining constants to give names to the GPIO pins we're using. Adjust the
# numbers as needed.
class IoPin(Enum):
    SENSOR_STATION = 12
    SENSOR_MOUNTAIN = 14
    TRAIN_FORWARD = 23
    TRAIN_BACKWARD = 24
    TRAIN_VELOCITY = 25
    INPUT_SHUTDOWN = 31
    OUTPUT_SHUTDOWN = 32


def is_sensor_hit(pin):
    # return gpio.input(pin.value) == 1
    return False


class State(Enum):
    DEPARTING = 1
    TO_MOUNTAIN = 2
    MOUNTAIN = 3
    TO_STATION = 4
    STATION = 5
    SHUTTING_DOWN = 6
    SHUTDOWN = 7


class StateMachine():
    def __init__(self):
        self.state = State.TO_STATION
        self.startTime_sec = 0  # put units on your variable names
        self.soundsPlayed = 0
        self.sensorHits = 0
        self.shutdownHits = 0
        # self.velo = gpio.PWM(IoPin.TRAIN_VELOCITY, 1000)
        # self.velo.ChangeDutyCycle(55)  # Medium speed


    def transition(self, newState):
        print('Switching to', newState.name)
        self.state = newState
        self.startTime_sec = time.perf_counter()
        self.soundsPlayed = 0
        self.sensorHits = 0


    def check_shutdown(self):
        if self.state == State.SHUTDOWN or self.state == State.SHUTTING_DOWN:
            return
        if is_sensor_hit(IoPin.INPUT_SHUTDOWN):
            self.shutdownHits += 1
        else:
            self.shutdownHits = 0
        if self.shutdownHits >= 2:
            if self.state == State.STATION:
                self.transition(State.SHUTDOWN)
            else:
                self.transition(State.SHUTTING_DOWN)


    def run(self):
        self.check_shutdown()

        # Compute how long we've been in the current state
        elapsed_sec = time.perf_counter() - self.startTime_sec

        if self.state == State.DEPARTING:
            # Play sounds and accelerate out of the station. Everything happens
            # on a clock so no possibility of false sensor hits causing a
            # problem. Can adjust timings with trial and error.

            # Define the timeline in reverse order so sounds don't get played
            # more than once.
            if elapsed_sec > 13:
                # self.velo.ChangeDutyCycle(75)  # High speed
                self.transition(State.TO_MOUNTAIN)
            elif elapsed_sec > 9:
                # accelerate at 10 units per second
                speed = math.floor(elapsed_sec - 9) * 10 + 35
                # self.velo.ChangeDutyCycle(speed)
            elif elapsed_sec > 7:
                # self.velo.ChangeDutyCycle(35)  # Pull away slowly
                pass
            elif elapsed_sec > 6 and self.soundsPlayed == 2:
                # TODO: play 'toot'
                self.soundsPlayed += 1
            elif elapsed_sec > 5 and self.soundsPlayed == 1:
                # TODO: play 'toot'
                self.soundsPlayed += 1
            elif self.soundsPlayed == 0:
                # TODO: play 'All Aboard!'
                self.soundsPlayed += 1

        elif self.state == State.TO_MOUNTAIN:
            # Start looking for the mountain reed sensor.
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN):
                self.sensorHits += 1
            else:
                self.sensorHits = 0
            # Need two consecutive reed sensor hits to really be inside the
            # mountain. If not, assume false positive.
            if self.sensorHits >= 2:
                self.transition(State.MOUNTAIN)

        elif self.state == State.MOUNTAIN:
            # Decelerate to low speed, then start looking for the station reed sensor.
            if elapsed_sec > 64:
                # self.velo.ChangeDutyCycle(35)  # low speed
                self.transition(State.TO_STATION)
            elif elapsed_sec > 60:
                # decelerate at 10 units per second
                speed = 75 - math.floor(elapsed_sec - 60) * 10
                # self.velo.ChangeDutyCycle(speed)
            elif elapsed_sec > 30:
                # self.velo.ChangeDutyCycle(75)  # high speed
                pass
            # Stop inside the mountain for 30 seconds.
            else:
                # self.velo.ChangeDutyCycle(0)  # stopped
                pass

        elif self.state == State.TO_STATION:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.sensorHits += 1
            else:
                self.sensorHits = 0
            if self.sensorHits >= 2:
                self.transition(State.STATION)

        elif self.state == State.STATION:
            if elapsed_sec > 25:
                self.transition(State.DEPARTING)
            elif self.soundsPlayed == 0:
                # self.velo.ChangeDutyCycle(0)  # stopped
                # TODO: play 'Welcome to Christmas village'
                self.soundsPlayed = 1

        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we arrive at
            # the station.
            # self.velo.ChangeDutyCycle(55)
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.sensorHits += 1
            else:
                self.sensorHits = 0
            if self.sensorHits >= 2:
                self.transition(State.SHUTDOWN)

        elif self.state == State.SHUTDOWN:
            # self.velo.ChangeDutyCycle(0)
            # gpio.output(IoPin.OUTPUT_SHUTDOWN, gpio.HIGH)
            pass


if __name__ == '__main__':
    # TODO: init GPIO and pins
    machine = StateMachine()
    try:
        while True:
            machine.run()
            time.sleep(0.2)  # 5 Hz clock
    finally:
        # TODO: GPIO cleanup
        pass
