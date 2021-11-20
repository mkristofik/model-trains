"""
    - Sit for X seconds/or time clock
    - Departure Announcement
    - Accelerate to right mountain/or maybe just go to operating speed
    - Stop at Right Mountain Reed for X seconds/ or time clock
    -
    - reverse
    - Proceed to station
    - Decelerate approaching station
    - Stop at station reed
    - Announce arrival
    - Stop for X seconds (completing a cycle)

    - Then  for a second variation Trolley blows by the station periodically.
    - Version 2 is just a basic working version with sounds and startup,,no shutdown 1/21/2020
    - This version 3 adds shutdown 1/21/2020
    - This version 4 adds sound on off button and 10 minute shutdown.
    - This version 5 adds clock time depart from all 3/4 stops missing station1
    - This version 6 adds station bypass.
    - This version 7 cleans up some stuff and corrects comments
    - This version 8 changes shutdown via file corrections
    - This version 9 includes changing defective GPIO 36 to 22
"""
from enum import Enum
import RPi.GPIO as gpio
import math
import time
from time import sleep
import pygame
import os
import random
from datetime import datetime as dt
from pathlib import Path
import os.path
import sys
import threading

# Defining constants to give names to GPIO pins. Adjust these numbers as
# needed, including to deconflict with another train being controlled by the
# same Pi.
pygame.init()

class IoPin(Enum):
    SENSOR_STATION = 38
    SENSOR_MOUNTAIN_L = 22 #was 36 but defective
    SENSOR_MOUNTAIN_R = 40
    TRAIN_FORWARD = 3
    TRAIN_BACKWARD = 5
    TRAIN_VELOCITY = 7
    INPUT_SHUTDOWN = 37 #maybe later will use master pi wireless
    OUTPUT_SHUTDOWN = 33 #maybe later


# Defining constants for the different states.
class State(Enum):
    DEPARTING = 1
    TO_MOUNTAIN_L = 2
    MOUNTAIN_L = 3
    ML_RETURN = 4
    STATION_BYPASS = 5
    STATION_1 = 6
    TO_MOUNTAIN_R = 7
    MOUNTAIN_R = 8
    MR_RETURN = 9
    STATION_2 = 10
    STARTUP_LEFT =11
    STARTUP_RIGHT =12
    SHUTTING_DOWN = 13
    SHUTDOWN_L =14
    SHUTDOWN_R = 15
    SHUTDOWN = 16
##################################
# add tread related sounds
sndon = pygame.mixer.Sound("/home/pi/Music/train_snd_on.wav")
sndoff = pygame.mixer.Sound("/home/pi/Music/train_snd_off.wav")
# audience train sound button
#Set the board physical GPIO pin numbers
gpio.setmode(gpio.BOARD)
sound = 23
gpio.setup(sound,gpio.IN,gpio.PUD_UP) #wired so don't need to test for false signal anymore
# THREAD sound button routine/function
def sndcycle():
    while True:

        startTime_sec = time.perf_counter() #time count

        while gpio.input(23) == gpio.HIGH and time.perf_counter() - startTime_sec < 600:# should be 600
            time.sleep(0.3)
            pass
# if 10 minutes pass sound off when file created and sound off announced
# or button pressed ditto above
        Path('/home/pi/Documents/model-trains/sound_off').touch()
        sndoff.set_volume(0.6)
        sndoff.play()
        sleep(3) # allow for Walt's voice

# next await button to be pressed to turn sound back on
        while gpio.input(23) == gpio.HIGH:
            time.sleep(0.3) #to prevent button kickback
            pass
# button pressed to turn sounds back on for 10 minutes and await next button pressed
# first erase sound off file
        os.remove('/home/pi/Documents/model-trains/sound_off')
# play sounds on
        sndon.set_volume(0.5)
        sndon.play()
        sleep(3)
##############################################
def is_sensor_hit(pin):
    if (gpio.input(pin.value)) == 0:
        print('Sensor', pin)

        return 1
    else:
        return gpio.input(pin.value) == 0

def play_sound(snd): # function on whether sound is on or off
        if not os.path.isfile('/home/pi/Documents/model-trains/sound_off'):
            snd.play()


class StateMachine():
    def __init__(self):
        self.state = State.STARTUP_LEFT
        self.startTime_sec = 0  # put units on your variable names
        self.soundsPlayed = 0
        self.sensorHits = 0
        self.shutdownHits = 0
        self.cycles = -1
        self.departTime_sec = 0 # part of adjusting trolley timing
        self.mountainTime_sec = 0 # part of adjusting trolley timing
        self.speedMult = 1 # part of adjusting trolley timing

        gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH) # trolley goes towards left mountain
        gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW) # with above
        self.velo = gpio.PWM(IoPin.TRAIN_VELOCITY.value, 1000)
        self.velo.start(65)  # Medium speed

        self.sndIntro = pygame.mixer.Sound('/home/pi/Music/Merry_Xmas_All_Aboard_v2_nl.wav')
        self.sndIntro.set_volume(0.3)
        self.sndToot = pygame.mixer.Sound('/home/pi/Music/double_clang_nl.wav')#change to clang
        self.sndToot.set_volume(0.4)
        self.sndArr = pygame.mixer.Sound('/home/pi/Music/Vil2_silv_A_a_nl.wav')#emk added
        self.sndArr.set_volume(0.3) #emk added
        self.sndDep = pygame.mixer.Sound('/home/pi/Music/Vil2_silv_D_a_nl.wav')#emk added
        self.sndDep.set_volume(0.4) #emk added

    def transition(self, newState):
        print('Switching to', newState.name)
        self.state = newState
        self.startTime_sec = time.perf_counter()
        self.soundPlayed = False
        self.sensorHits = 0


    def check_shutdown(self):
        if self.state == State.SHUTDOWN or self.state == State.SHUTTING_DOWN or self.state == State.SHUTDOWN_L or self.state == State.SHUTDOWN_R:
            return
        # if shutdown button pressed or shutdown file established begin shutting down
        if is_sensor_hit(IoPin.INPUT_SHUTDOWN) or os.path.isfile('/home/pi/Documents/model-trains/shutdown/bf_shut_it_down'):
            if self.state == State.STATION_2:
                self.transition(State.SHUTDOWN)
            elif self.state == State.STATION_1:
                self.transition(State.SHUTDOWN)
            else:
                self.transition(State.SHUTTING_DOWN)




    def check_mountain_L_sensor(self):
        if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_L):
            self.sensorHits += 1

        else:
            self.sensorHits = 0
        return self.sensorHits >= 2


    def check_station_sensor(self):
        if is_sensor_hit(IoPin.SENSOR_STATION):
            self.sensorHits += 1
        else:
            self.sensorHits = 0
        return self.sensorHits >= 2

    def check_mountain_R_sensor(self):
        if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_R):
            self.sensorHits += 1
        else:
            self.sensorHits = 0
        return self.sensorHits >= 2

    def acceleration_function(self):
        self.velo.ChangeDutyCycle(65)  # Medium speed put aceleration later

    def run(self):
        self.check_shutdown()

        # Compute how long we've been in the current state
        elapsed_sec = time.perf_counter() - self.startTime_sec

        if self.state == State.DEPARTING:
            # Play departure announcement and accelerate out of the station.
            # Start looking for the mountain reed.  As with the other script,
            # define the timings in reverse order so things don't get repeated.
            if elapsed_sec > 10:
                self.velo.ChangeDutyCycle(65)  # Medium speed
                #                 if self.check_mountain_L_sensor():
                self.transition(State.TO_MOUNTAIN_L)
            # Disabling smooth acceleration to avoid moving too slowly
            # through the curve when sharing power with the other train line.
            #elif elapsed_sec > 5:
                #speed = math.floor(elapsed_sec - 5) * 10 + 35
                #self.velo.ChangeDutyCycle(speed)
#            elif not self.soundPlayed:
                # TODO: play 'Now departing station'
#                self.soundPlayed = True
            elif elapsed_sec > 6 and self.soundsPlayed == 1:
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
                if play == 0 and os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:  #emk
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndIntro.play() #emk
                    play_sound(self.sndIntro)
                if play == 1 and os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                    #    self.sndDep.play() #emk added change
                    play_sound(self.sndDep)

                self.soundsPlayed += 1
                play = -1 #added 05/10


        elif self.state == State.TO_MOUNTAIN_L:

            if elapsed_sec > 7: #was 4

                if self.check_mountain_L_sensor():
                    self.transition(State.MOUNTAIN_L)
            elif elapsed_sec > 6:  # was 3
#
#                acceleration_function()     # insert later
                self.velo.ChangeDutyCycle(45)

            else:
                self.velo.ChangeDutyCycle(65)  # stopped

#######  change the direction
        elif self.state == State.MOUNTAIN_L:

            c = (3,8) #will move either direction and not wait as long on startup
            if elapsed_sec > 45 and (dt.now().minute % 10) in (c):
                print(dt.now().minute," minutes after the hour")
                print(dt.now().second," seconds")
                self.soundsPlayed = 0
                # train will stop at station every other time
                if (dt.now().minute % 10) == 8:
                    self.transition(State.STATION_BYPASS)
                else:
                    gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) #direction towards R Mtn
                    gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
                    self.velo.ChangeDutyCycle(75)
                    play_sound(self.sndArr)
                    self.transition(State.ML_RETURN)

            else:
                self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.ML_RETURN:
            if elapsed_sec > 3:
                if self.check_station_sensor():
                    play_sound(self.sndToot)
                    self.transition(State.STATION_1)
            # Disabling smooth deceleration for now t

            #elif elapsed_sec > 12:
                # decelerate at 10 units per second
                #speed = 75 - math.floor(elapsed_sec - 12) * 10
                #self.velo.ChangeDutyCycle(speed)
            #elif elapsed_sec > 3:  # for deceleration to do
            #    gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) #direction towards R Mtn
            #    gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
            #    self.velo.ChangeDutyCycle(65)  # medium speed
            #else:
            #    self.velo.ChangeDutyCycle(0)  # stopped
        elif self.state == State.STATION_BYPASS:
            if elapsed_sec > 4:
                play_sound(self.sndToot)
                self.transition(State.TO_MOUNTAIN_R)
            else:
                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) #direction towards R Mtn
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
                self.velo.ChangeDutyCycle(70)  # medium speed

        elif self.state == State.STATION_1:
            if elapsed_sec > 20:  # TODO: determine with 3 trains running
                self.soundsPlayed = 0
                self.transition(State.TO_MOUNTAIN_R)
            elif elapsed_sec > 16 and self.soundsPlayed == 1:
                #if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == False:
                #    self.sndToot.play()
                play_sound(self.sndToot)
                self.soundsPlayed += 1
            elif elapsed_sec > 10 and self.soundsPlayed == 0:
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
            elif not self.soundPlayed:
                self.velo.ChangeDutyCycle(0)  # stopped
                # play 'Now arriving'
                self.soundPlayed = True
            else:
                self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.TO_MOUNTAIN_R:
            # Come to an immediate stop inside the mountain to simulate
            # visiting some far-off station. After some time, set medium speed
            # and reverse. Sit inside the mountain again, and
            # then approach the station.
            if elapsed_sec > 4:
                if self.check_mountain_R_sensor():
                    self.transition(State.MOUNTAIN_R)
                else:  # TODO: was 30, shortened for debugging.

                    gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) #direction towards R Mtn
                    gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
                    self.velo.ChangeDutyCycle(70)  # medium speed


        elif self.state == State.MOUNTAIN_R:
#       elif self.state == State.INBOUND:
            #if elapsed_sec > 17:
            d = (4,9) #will move and not wait as long on startup
            if elapsed_sec > 17 and (dt.now().minute % 10) in (d):
                print(dt.now().minute," minutes after the hour")
                print(dt.now().second," seconds")
                self.soundsPlayed = 0
                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH) #direction towards R Mtn
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW)
                self.velo.ChangeDutyCycle(65) #was 65
                #play_sound(self.sndArr)
                self.transition(State.MR_RETURN)

            else:
                self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.MR_RETURN:
            if elapsed_sec > 9: # 9 for rochester 8 for Homewood
                if self.check_station_sensor():
                    play_sound(self.sndToot)
                    self.transition(State.STATION_2)
                    self.soundsPlayed = 0

            elif elapsed_sec > 8 and self.soundsPlayed == 0:  #8 Rochester 7 for Homewood..slow down to not pass reed in stopping
               self.velo.ChangeDutyCycle(40)  # medium speed changed from 40
               play_sound(self.sndArr) # moved from mountainR
               self.soundsPlayed += 1
            #else:
            #    self.velo.ChangeDutyCycle(0)  # stopped

        elif self.state == State.STATION_2:
            if elapsed_sec > 45:  # TODO: was 25, shortened for debugging ,45 05/06 emk
                #print(dt.now().minute)
                a = (1,6)
                b = (3,8) #Silverbell will move and not wait as long to see something on startup
                if (dt.now().minute % 10) in (a):
                    print(dt.now().minute," minutes after the hour")
                    print(dt.now().second," seconds")
                    self.transition(State.DEPARTING)
                elif (dt.now().minute % 10) in (b):
                    print(dt.now().minute," minutes after the hour")
                    print(dt.now().second," seconds")
                    self.transition(State.STATION_1)
                else:
                    self.soundsPlayed == 0
                    self.velo.ChangeDutyCycle(0)
                    gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH) # towards L Mtn to ensure STARTUP
                    gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW) # going toowards Left MTN
            #if elapsed_sec > 30:  # TODO: was 30, shortened for debugging
            #    self.soundsPlayed = 0
            #    self.transition(State.DEPARTING)
            #elif not self.soundPlayed:
            else:
                self.velo.ChangeDutyCycle(0)  # stopped
                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH) # towards L Mtn to ensure STARTUP
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW) # going toowards Left MTN
                # play 'Now arriving'
                #self.soundPlayed = True

        elif self.state == State.STARTUP_LEFT:

            if is_sensor_hit(IoPin.SENSOR_STATION):
                play_sound(self.sndToot)
                self.transition(State.STATION_2)
            else:
                self.velo.ChangeDutyCycle(60)
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_L):
                self.velo.ChangeDutyCycle(0)
                self.transition(State.STARTUP_RIGHT)

        elif self.state == State.STARTUP_RIGHT:

            if is_sensor_hit(IoPin.SENSOR_STATION):
                play_sound(self.sndToot)
                self.transition(State.STATION_2)
            elif elapsed_sec > 2:
                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) # towards R Mtn
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
                self.velo.ChangeDutyCycle(60)
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_R):
                self.velo.ChangeDutyCycle(0)
                self.transition(State.STARTUP_LEFT)

        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we arrive at
            # the station.
            self.velo.ChangeDutyCycle(60)
            if is_sensor_hit(IoPin.SENSOR_STATION):
#                self.sensorHits += 1
#            else:
#                self.sensorHits = 0
#            if self.sensorHits >= 2:
                self.transition(State.SHUTDOWN)
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_R):
                self.velo.ChangeDutyCycle(0)
                self.transition(State.SHUTDOWN_L)
            if is_sensor_hit(IoPin.SENSOR_MOUNTAIN_L):
                self.velo.ChangeDutyCycle(0)
                self.transition(State.SHUTDOWN_R)

        elif self.state == State.SHUTDOWN_R:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.transition(State.SHUTDOWN)
            elif elapsed_sec > 2:
                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.LOW) # towards R Mtn
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.HIGH)
                self.velo.ChangeDutyCycle(60)

        elif self.state == State.SHUTDOWN_L:
            if is_sensor_hit(IoPin.SENSOR_STATION):
                self.transition(State.SHUTDOWN)
            elif elapsed_sec > 2:

                gpio.output(IoPin.TRAIN_FORWARD.value, gpio.HIGH) # towards L Mtn
                gpio.output(IoPin.TRAIN_BACKWARD.value, gpio.LOW)
                self.velo.ChangeDutyCycle(60)

        elif self.state == State.SHUTDOWN:
            self.velo.ChangeDutyCycle(0)
            gpio.output(IoPin.OUTPUT_SHUTDOWN.value, gpio.HIGH)
            time.sleep(5)  # TODO: Adjust this as needed to make sure the
                           # master Pi sees the signal.
#        elif self.state == State.SHUTTING_DOWN:
#            # Proceed at medium speed from wherever we are until we reach the
#            # station. It doesn't matter which direction we're facing.
#            self.velo.ChangeDutyCycle(70)  # medium speed was 65 emk 5/5
#           #if self.check_station_sensor():
#            if self.check(IoPin.station_sensor):
#                self.transition(State.SHUTDOWN)
#
#        elif self.state == State.SHUTDOWN:
#            self.velo.ChangeDutyCycle(0)
#            gpio.output(OUTPUT_SHUTDOWN, gpio.HIGH)
#            time.sleep(5)  # TODO: Adjust this as needed to make sure master Pi
#                           # sees the signal.
            return True

##############
#tread portion of main program
if os.path.isfile('/home/pi/Documents/model-trains/sound_off'):
        os.remove('/home/pi/Documents/model-trains/sound_off')

#Start Thread
t = threading.Thread(target=sndcycle)
t.start()
#################

if __name__ == '__main__':
    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)
    gpio.setup(IoPin.SENSOR_STATION.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.SENSOR_MOUNTAIN_L.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.SENSOR_MOUNTAIN_R.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.INPUT_SHUTDOWN.value, gpio.IN,gpio.PUD_UP)
    gpio.setup(IoPin.TRAIN_FORWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_BACKWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_VELOCITY.value, gpio.OUT)
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
        #t.join()
        gpio.cleanup()
        Path('/home/pi/Documents/model-trains/shutdown/back_and_forth_off').touch()
        time.sleep(5)
        print('Bye!')
        sys.exit()
