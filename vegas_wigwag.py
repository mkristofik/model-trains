"""The Vegas train line from Auntie's Christmas display:
    - Departing Announcement (relay so sound goes in to correct speaker)
    - Accelerate towards left platform
    - Turn on Wigwag and sound (2 relays one for wigwag one for sound)
    - Decelerate (probably same start timing as Wigwag)
    - Stop at platform reed
    - Shut off Wigwag
    - Sit for X seconds
    - Proceed to left bumper and reverse
    - Stop at platform reed again for x seconds.
    - Turn on Wigwag and sound
    - Accelerate  towards station
    - Turn off wigwag
    - Decelerate approaching station
    - Stop at station reed
    - Announce arrival
    - Sit for X seconds
    - Departure Announcement
    - Proceed to right mountain (small tree lined distance to mountain  so no
      need to accelerate)
    - Stop at Right Mountain Reed for X seconds
    - Proceed to right bumper and reverse
    - Stop at right mountain reed again for x seconds.
    - Proceed to station
    - Stop at station reed
    - Announce arrival
    - Stop for X seconds (completing a cycle)
"""
from enum import Enum
import RPi.GPIO as gpio
import time


# Defining constants to give names to GPIO pins. Adjust these numbers as
# needed, including to deconflict with another train being controlled by the
# same Pi.
class IoPin(Enum):
    SENSOR_STATION = 18
    SENSOR_PLATFORM = 16
    SENSOR_MOUNTAIN = 22
    TRAIN_FORWARD = 8
    TRAIN_BACKWARD = 10
    TRAIN_VELOCITY = 12
    INPUT_SHUTDOWN = 5
    OUTPUT_SHUTDOWN = 13
    WIGWAG_POWER = 20  # TODO: assign pins to wigwag
    WIGWAG_SOUND = 21


# State names identify which direction the train is facing with _L or _R.
class State(Enum):
    STATION_L = auto()
    DEPARTING_L = auto()
    PLATFORM_L = auto()
    INBOUND_R = auto()
    STATION_R = auto()
    DEPARTING_R = auto()
    MOUNTAIN_R = auto()
    INBOUND_L = auto()
    SHUTTING_DOWN = auto()
    SHUTDOWN = auto()


def is_sensor_hit(pin):
    if gpio.input(pin.value) == 1:
        print('Sensor hit', pin)
        return True


class StateMachine():
    def __init__(self):
        self.state = State.DEPARTING_L
        self.startTime_sec = time.perf_counter()
        self.soundPlayed = False
        self.sensorHits = 0
        self.shutdownHits = 0
        gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH)
        gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW)
        self.velo = gpio.PWM(IoPin.TRAIN_VELOCITY.value, 1000)
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
        if is_sensor_hit(IoPin.INPUT_SHUTDOWN):
            self.shutdownHits += 1
        else:
            self.shutdownHits = 0
        if self.shutdownHits >= 2:
            if self.state == State.STATION_L or self.state == State.STATION_R:
                self.transition(State.SHUTDOWN)
            else:
                self.transition(State.SHUTTING_DOWN)


    def check_sensor(self, pin):
        if gpio.input(pin.value) == 1:
            print('Sensor hit', pin)
            self.sensorHits += 1
        else:
            self.sensorHits = 0
        return self.sensorHits >= 2


    def train_go(self):
        self.velo.ChangeDutyCycle(65)  # Medium speed


    def train_stop(self):
        self.velo.ChangeDutyCycle(0)


    def wigwag_on(self):
        gpio.output(IoPin.WIGWAG_POWER.value, gpio.HIGH)
        gpio.output(IoPin.WIGWAG_SOUND.value, gpio.HIGH)


    def wigwag_off(self):
        gpio.output(IoPin.WIGWAG_POWER.value, gpio.LOW)
        gpio.output(IoPin.WIGWAG_SOUND.value, gpio.LOW)


    def run(self):
        self.check_shutdown()
        elapsed_sec = time.perf_counter() - self.startTime_sec

        if self.state == State.DEPARTING_L:
            if elapsed_sec > 10:
                self.wigwag_on()
                if self.check_sensor(IoPin.SENSOR_PLATFORM):
                    self.transition(State.PLATFORM_L)
            elif elapsed_sec > 7:
                self.train_go()
            elif not self.soundPlayed:
                # TODO: play departure announcement
                self.soundPlayed = True

        elif self.state == State.PLATFORM_L:
            if elapsed_sec > 11:
                if self.check_sensor(IoPin.SENSOR_PLATFORM):
                    self.transition(State.INBOUND_R)
            elif elapsed_sec > 10:
                self.train_go()
            else:
                self.wigwag_off()
                self.train_stop()

        elif self.state == State.INBOUND_R:
            if elapsed_sec > 15:
                if self.check_sensor(IoPin.SENSOR_STATION):
                    self.transition(State.STATION_R)
            elif elapsed_sec > 14:
                self.wigwag_off()
            elif elapsed_sec > 10:
                self.wigwag_on()
                self.train_go()
            else:
                self.train_stop()

        elif self.state == State.STATION_R:
            if elapsed_sec > 15:
                self.transition(State.DEPARTING_R)
            elif not self.soundPlayed:
                self.train_stop()
                # TODO: play arrival announcement
                self.soundPlayed = True
        
        elif self.state == State.DEPARTING_R:
            if elapsed_sec > 8:
                if self.check_sensor(IoPin.SENSOR_MOUNTAIN):
                    self.transition(State.MOUNTAIN_R)
            elif elapsed_sec > 7:
                self.train_go()
            elif not self.soundPlayed:
                # TODO: play departure announcement
                self.soundPlayed = True

        elif self.state == State.MOUNTAIN_R:
            if elapsed_sec > 11:
                if self.check_sensor(IoPin.SENSOR_MOUNTAIN):
                    self.transition(State.INBOUND_L)
            elif elapsed_sec > 10:
                self.train_go()
            else:
                self.train_stop()

        elif self.state == State.INBOUND_L:
            if elapsed_sec > 11:
                if self.check_sensor(IoPin.SENSOR_STATION):
                    self.transition(State.STATION_L)
            elif elapsed_sec > 10:
                self.train_go()
            else:
                self.train_stop()

        elif self.state == State.STATION_L:
            if elapsed_sec > 15:
                self.transition(State.DEPARTING_L)
            elif not self.soundPlayed:
                self.train_stop()
                # TODO: play arrival announcement
                self.soundPlayed = True

        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we reach the
            # station. It doesn't matter which direction we're facing.
            self.train_go()
            if self.check_sensor(IoPin.SENSOR_STATION)
                self.transition(State.SHUTDOWN)

        elif self.state == State.SHUTDOWN:
            self.train_stop()
            gpio.output(IoPin.OUTPUT_SHUTDOWN.value, gpio.HIGH)
            time.sleep(5)  # TODO: Adjust this as needed to make sure master Pi
                           # sees the signal.
            return True


if __name__ == '__main__':
    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setup(IoPin.SENSOR_STATION.value, gpio.IN)
    gpio.setup(IoPin.SENSOR_PLATFORM.value, gpio.IN)
    gpio.setup(IoPin.SENSOR_MOUNTAIN.value, gpio.IN)
    gpio.setup(IoPin.INPUT_SHUTDOWN.value, gpio.IN)
    gpio.setup(IoPin.TRAIN_FORWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_BACKWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_VELOCITY.value, gpio.OUT)
    gpio.setup(IoPin.OUTPUT_SHUTDOWN.value, gpio.OUT)
    gpio.setup(IoPin.WIGWAG_POWER.value, gpio.OUT)
    gpio.setup(IoPin.WIGWAG_SOUND.value, gpio.OUT)

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
