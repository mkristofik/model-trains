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
      dad3 add sounds for station blow by and stop 05/10
      dad4 adding shutdown program via software
      dad5 add sound on sound off
      dad6 add no sound function and cleanup
      dad7 add sound adjustment for trolley based on speed.
      dad8 changing shutdown via file changes
      dad9.1 add create program to shut off Vegas train wirelessly
"""
from enum import Enum
import RPi.GPIO as gpio
import math
import pygame
import time
import random #emk
from datetime import datetime as dt
import os.path  # shutdown program
from pathlib import Path

# Defining constants to give names to the GPIO pins we're using. Adjust the
# numbers as needed.
class IoPin(Enum):
    SENSOR_STATION = 32
    SENSOR_MOUNTAIN = 26
    TRAIN_FORWARD = 8
    TRAIN_BACKWARD = 10
    TRAIN_VELOCITY = 12
    INPUT_SHUTDOWN = 37
    OUTPUT_SHUTDOWN = 35


def is_sensor_hit(pin):
    if (gpio.input(pin.value)) == 0:
        print('Sensor', pin)
    return gpio.input(pin.value) == 0

def play_sound(snd): # function on weather soundis on or off
    if not os.path.isfile('/home/pi/Documents/model-trains/sound_off'):
        snd.play()


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
        self.cycles = -1
        self.departTime_sec = 0 # part of adjusting trolley timing
        self.mountainTime_sec = 0 # part of adjusting trolley timing
        self.speedMult = 1 # part of adjusting trolley timing

        gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH)
        gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW)
        self.velo = gpio.PWM(IoPin.TRAIN_VELOCITY.value, 1000)
        self.velo.start(55)  # Medium speed

        self.sndIntro = pygame.mixer.Sound('/home/pi/Documents/Merry_Xmas_All_Aboard_v2_nl.wav')
        self.sndIntro.set_volume(0.3)
        self.sndToot = pygame.mixer.Sound('/home/pi/Documents/toot_toot_nl.wav')
        self.sndToot.set_volume(0.5)
        self.sndArr = pygame.mixer.Sound('/home/pi/Music/Vil1_vill_A_a_nl.wav')#emk added
        self.sndArr.set_volume(0.4) #emk added
        self.sndDep = pygame.mixer.Sound('/home/pi/Music/Vil1_vill_D_a_nl.wav')#emk added
        self.sndDep.set_volume(0.4) #emk added



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

        if os.path.isfile('/home/pi/Documents/model-trains/shutdown/oval_shut_it_down'):
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
            if elapsed_sec > 19:  #original 17 ek
                self.velo.ChangeDutyCycle(75)  # High speed was 75
                self.transition(State.TO_MOUNTAIN)
            elif elapsed_sec > 13:
                # accelerate at 10 units per second
                speed = math.floor(elapsed_sec - 13) * 10 + 40 #chg from 35 to 40 emk
                self.velo.ChangeDutyCycle(speed)
            elif elapsed_sec > 11:
                self.velo.ChangeDutyCycle(35)  # Pull away slowly chng from 35 to 40 emk
                self.departTime_sec = time.perf_counter() # part of adjusting trolley timing
            elif elapsed_sec > 7 and self.soundsPlayed == 2:
                print('Accelerate slowly')
                if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    self.sndToot.play()
                self.soundsPlayed += 1
            elif elapsed_sec > 5 and self.soundsPlayed == 1:
                #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                #    self.sndToot.play()
                play_sound(self.sndToot)
                self.soundsPlayed += 1
            elif self.soundsPlayed == 0:
                print('All aboard')
                play = -1  # 05/18/20
                play = random.randrange(2) # emk
                print(play)
                #self.sndIntro.play()
                if play == 0:  #emk
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndIntro.play() #emk
                    play_sound(self.sndIntro)
                if play == 1:
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndDep.play() #emk added change
                    play_sound(self.sndDep)

                self.soundsPlayed += 1
                play = -1 #added 05/10

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
                self.mountainTime_sec = time.perf_counter()# part of adjusting trolley timing

        elif self.state == State.MOUNTAIN:
            self.speedMult = (self.mountainTime_sec - self.departTime_sec)# part of adjusting trolley timing
            #print("start speed", self.speedMult) 8.5
            stopped_sec = 97  # how long to stop inside the mountain was30

            # randomly determine how many times trolley blows by station before stopping
            if self.cycles == -1: #emk 5/4 attempt
                self.cycles = random.randrange(2) #emk 5/4 attempt
                print("start speed", self.speedMult) #8.5

            if self.cycles == 0: #emk 5/4 attempt
                # part of adjusting trolley timing
                # drive_sec determines when to decelerate and train arrival announcement
                # constant 8.48 homewwod 7.50 rochester
                drive_sec = stopped_sec + 9*(self.speedMult/7.5) # emk add once around 5/1 was 10 make 8
            #if option == 1:
            if self.cycles == 1: #emk 5/4 attempt
                drive_sec = stopped_sec + 22.5*(self.speedMult/7.5) #emk added change twice around 5/1
            # add horn alert as trolley blows by station
            if drive_sec <= 110: # 110 leaves wiggle worm to adjust horn timing -5 -7 to -6 -8
                #change constant from 5 to 7
                if elapsed_sec > drive_sec - 7*(7.5/self.speedMult) and self.soundsPlayed == 6:# toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed += 1
                #change constant from 7 to 9
                if elapsed_sec > drive_sec - 9*(7.5/self.speedMult) and self.soundsPlayed == 0 :# toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed += 6
                    print(drive_sec)

            #if elapsed_sec > drive_sec - 5 and self.soundsPlayed == 6:# toot passing station
            #    self.sndToot.play()
            #    self.soundsPlayed += 1

            #if elapsed_sec > drive_sec - 7 and self.soundsPlayed == 0 :# toot passing station
            #    self.sndToot.play()
            #    self.soundsPlayed += 6

            if drive_sec > 110:
                #change  constant now 5 if needed for 2nd lap
                if elapsed_sec > drive_sec - 9*(7.5/self.speedMult) and self.soundsPlayed == 4:# toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed += 1
                    #print (drive_sec," 4")
                # change constant if needed for 2nd lap
                if elapsed_sec > drive_sec - 11*(7.5/self.speedMult) and self.soundsPlayed == 3:# toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed = 4
                    #print (drive_sec," 3")
                #change constant now 19 if needed for 1st lap
                if elapsed_sec > drive_sec - 21*(7.5/self.speedMult) and self.soundsPlayed == 2:# 17toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed = 3
                    #print (drive_sec," 2")
                #change constant now 21 if needed for 1st lap
                if elapsed_sec > drive_sec - 23*(7.5/self.speedMult) and self.soundsPlayed == 0:# 19toot passing station
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndToot.play()
                    play_sound(self.sndToot)
                    self.soundsPlayed = 2
                    #print (drive_sec," 1")




            #drive_sec = stopped_sec + 13  # how long to drive at full speed after leaving 5/1
                                          # the mountain original 21 emk

            # Decelerate to low speed, then start looking for the station reed sensor.
            if elapsed_sec > drive_sec + 2:# adjusted at GP from 3 to 6 to 2
                print('Now approaching station')
                self.velo.ChangeDutyCycle(40)  # low speed bhg from 35 to 40 emk
                self.soundsPlayed = 0
                # TODO: play 'Welcome to Christmas village'
                #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                #    self.sndArr.play() #emk addition town trolley now arriving track 2
                play_sound(self.sndArr)
                self.soundsPlayed = 1
                self.cycles = -1  #emk attempt 5/4
                self.transition(State.TO_STATION)
            elif elapsed_sec > drive_sec:
                # decelerate at 10 units per second
                speed = 75 - math.floor(elapsed_sec - drive_sec) * 10
                self.velo.ChangeDutyCycle(speed)
            elif elapsed_sec > stopped_sec:
                self.velo.ChangeDutyCycle(75)  # high speed
            # Stop inside the mountain for 30 seconds.
            else:
                self.velo.ChangeDutyCycle(0)  # stopped


        elif self.state == State.TO_STATION:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.sensorHits += 1
            else:
                self.sensorHits = 0
            if self.sensorHits >= 2:
                #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                #    self.sndToot.play() # toot when arrive at station
                play_sound(self.sndToot)

                self.transition(State.STATION)

        elif self.state == State.STATION:
            if elapsed_sec > 45:  # TODO: was 25, shortened for debugging ,45 05/06 emk
                #print(dt.now().minute)
                a = (0,5,10,15,20,25,30,35,40,45,50,55)
                if dt.now().minute in (a):
                    print(dt.now().minute," minutes after the hour")
                    print(dt.now().second," seconds")
                    self.transition(State.DEPARTING)

            elif self.soundsPlayed == 0:
                self.velo.ChangeDutyCycle(0)  # stopped
                # TODO: play 'Welcome to Christmas village'


        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we arrive at
            # the station.
            self.velo.ChangeDutyCycle(55)
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.sensorHits += 1
            else:
                self.sensorHits = 0
            if self.sensorHits >= 2:
                self.transition(State.SHUTDOWN)

        elif self.state == State.SHUTDOWN:
            self.velo.ChangeDutyCycle(0)
            gpio.output(IoPin.OUTPUT_SHUTDOWN.value, gpio.HIGH)
            time.sleep(5)  # TODO: Adjust this as needed to make sure the
                           # master Pi sees the signal.
            return True
#turn on program to relay sound on/off to Vegas train
#os.system("python3 /home/pi/Desktop/snd_off_train1.py &")

if __name__ == '__main__':
    pygame.init()

    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)
    gpio.setup(IoPin.SENSOR_STATION.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.SENSOR_MOUNTAIN.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.INPUT_SHUTDOWN.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.TRAIN_VELOCITY.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_FORWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_BACKWARD.value, gpio.OUT)
    gpio.setup(IoPin.OUTPUT_SHUTDOWN.value, gpio.OUT)

    machine = StateMachine()
    try:
        isDone = False
        while not isDone:
            isDone = machine.run()
            time.sleep(0.02)  # 50 Hz clock
    except KeyboardInterrupt:
        print('Stopping manually')
    finally:
        gpio.cleanup()
        Path('/home/pi/Documents/model-trains/shutdown/oval_off').touch()
        time.sleep(5)


    print('Bye!')
