"""Auntie's Christmas village track involving a mountain.  Expected behavior copied from Dad's email:
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
import time


# Defining constants to give names to the GPIO pins we're using. Adjust the
# numbers as needed.
class IoPin(Enum):
    SENSOR_STATION = 12
    SENSOR_MOUNTAIN = 14
    SENSOR_SLOWDOWN = 16
    TRAIN_FORWARD = 23
    TRAIN_BACKWARD = 24
    TRAIN_VELOCITY = 25


def is_sensor_hit(pin):
    # return gpio.input(pin.value) == 1
    return False


# Lots of different states here. I use three states for each reed sensor so we
# can trap for false positives, and have a state to go back to that doesn't do
# anything but drive forward at a constant speed. All the fancy stuff happens
# in a separate state.
class State(Enum):
    DEPARTING = 1
    TO_MOUNTAIN = 2
    MOUNTAIN_MAYBE = 3
    MOUNTAIN = 4
    FROM_MOUNTAIN = 5
    SLOWDOWN_MAYBE = 6
    SLOWDOWN = 7
    TO_STATION = 8
    STATION_MAYBE = 9
    STATION = 10


class StateMachine():
    def __init__(self):
        self.state = State.DEPARTING
        self.startTime_sec = 0  # put units on your variable names
        self.soundsPlayed = 0
        # self.velo = gpio.PWM(IoPin.TRAIN_VELOCITY, 1000)


    def transition(self, newState):
        print('Switching to', newState.name)
        self.state = newState
        self.startTime_sec = time.perf_counter()
        self.soundsPlayed = 0


    def run(self):
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
            elif elapsed_sec > 10:
                # self.velo.ChangeDutyCycle(50)  # Medium speed
                pass
            elif elapsed_sec > 7:
                # self.velo.ChangeDutyCycle(25)  # Low speed
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
                self.transition(State.MOUNTAIN_MAYBE)

        elif self.state == State.MOUNTAIN_MAYBE:
            # Need two consecutive reed sensor hits to really be inside the
            # mountain. If not, assume false positive.
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN):
                self.transition(State.MOUNTAIN)
            else:
                self.transition(State.TO_MOUNTAIN)

        elif self.state == State.MOUNTAIN:
            # Stop inside the mountain for 30 seconds.
            if elapsed_sec < 30:
                # self.velo.ChangeDutyCycle(0)  # stopped
                pass
            else:
                # self.velo.ChangeDutyCycle(75)  # high speed
                self.transition(State.FROM_MOUNTAIN)

        elif self.state == State.FROM_MOUNTAIN:
            if is_sensor_hit(IoPin.SENSOR_SLOWDOWN):
                self.transition(State.SLOWDOWN_MAYBE)

        elif self.state == State.SLOWDOWN_MAYBE:
            if is_sensor_hit(IoPin.SENSOR_SLOWDOWN):
                self.transition(State.SLOWDOWN)
            else:
                self.transition(State.FROM_MOUNTAIN)

        elif self.state == State.SLOWDOWN:
            # Decelerate to low speed, then start looking for the station reed sensor.
            if elapsed_sec > 3:
                # self.velo.ChangeDutyCycle(25)  # low speed
                self.transition(State.TO_STATION)
            else:
                # self.velo.ChangeDutyCycle(50)  # medium speed
                pass

        elif self.state == State.TO_STATION:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.transition(State.STATION_MAYBE)

        elif self.state == State.STATION_MAYBE:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.transition(State.STATION)
            else:
                self.transition(State.TO_STATION)

        elif self.state == State.STATION:
            if elapsed_sec > 25:
                self.transition(State.DEPARTING)
            elif self.soundsPlayed == 0:
                # self.velo.ChangeDutyCycle(0)  # stopped
                # TODO: play 'Welcome to Christmas village'
                self.soundsPlayed = 1


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
