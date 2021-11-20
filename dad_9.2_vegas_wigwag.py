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
    - ek updates 6/10 change GPIO output reverse Mikes with new setup
    - ek add sounds 7/31
    - ek add sounds and adjust timing to clock 8/13
    - ek learn to shutdown
    - ek version 9 fix relay on off with chimes and all aboard
    - ek 9.2 working with sound on off
"""
#from enum import auto, Enum,auto probably needs a udated python version for auto to work
#from enum import Enum, auto
from enum import Enum
import RPi.GPIO as gpio
import time
import pygame
from datetime import datetime as dt
from pygame import mixer
from pathlib import Path
import os
import sys
# Defining constants to give names to GPIO pins. Adjust these numbers as
# needed, including to deconflict with another train being controlled by the
# same Pi.
class IoPin(Enum):
    SENSOR_STATION = 22 # was 22
    SENSOR_PLATFORM = 16
    SENSOR_MOUNTAIN = 18 # was18
    TRAIN_FORWARD = 8
    TRAIN_BACKWARD = 10
    TRAIN_VELOCITY = 12

    INPUT_SHUTDOWN = 5   #CHECKOUT TBD
    OUTPUT_SHUTDOWN = 13  #CHECKOUT TBD

    WIGWAG_POWER = 19  # TODO: assign pins relay 8 to wigwag had originally 20
    WIGWAG_SOUND = 21  # relay #7
    WIGWAG_BUTTON = 40 # WigWag audience button 06/10
    STATION_SOUND = 23   # relay #6

# State names identify which direction the train is facing with _L or _R.
class State(Enum):
    #STATION_L = auto()
    #DEPARTING_L = auto()
    #PLATFORM_L = auto()
    #INBOUND_R = auto()
    #STATION_R = auto()
    #DEPARTING_R = auto()
    #MOUNTAIN_R = auto()
    #INBOUND_L = auto()
    #SHUTTING_DOWN = auto()
    #SHUTDOWN = auto()
    STATION_L = 1 #above auto did not work with Python version
    DEPARTING_L = 2
    PLATFORM_L = 3
    INBOUND_R = 4
    STATION_R = 5
    DEPARTING_R = 6
    MOUNTAIN_R = 7
    INBOUND_L = 8
    SHUTTING_DOWN = 9
    SHUTDOWN = 10

# add sound using pygame
pygame.init()
toot = pygame.mixer.Sound("/home/pi/Music/Audio_2015/toot_toot_nl.wav")
toot.set_volume(0.5)
nextstop = pygame.mixer.Sound("/home/pi/Music/Audio_2015/NSLVa_v1_nl.wav")
nextstop.set_volume(0.3)
clang = pygame.mixer.Sound("/home/pi/Music/Audio_2015/double_clang_nl.wav")
clang.set_volume(0.8)
sndon = pygame.mixer.Sound("/home/pi/Music/Audio_2015/Sounds_On_nr.wav")
sndon.set_volume(0.3)
sndoff = pygame.mixer.Sound("/home/pi/Music/Audio_2015/Sounds_Off_nr.wav")
sndoff.set_volume(0.3)
allaboard = pygame.mixer.Sound("/home/pi/Music/Audio_2015/AA01_v1_nl.wav")
allaboard.set_volume(0.5)
merryxmas = pygame.mixer.Sound("/home/pi/Music/Audio_2015/merry_xmas_nl.wav")
merryxmas.set_volume(0.3)
welcome = pygame.mixer.Sound("/home/pi/Music/Audio_2015/W2LVa_v1_nl.wav")
welcome.set_volume(0.3)
wigwag = pygame.mixer.Sound("/home/pi/Music/Audio_2015/wigwag_sound_nl.wav")
wigwag.set_volume(0.8)
#background_music = pygame.mixer.music.load("/home/pi/Music/Audio_2015/bckgrnd_music_n_nr.mp3")
#background_music.set_volume(0.3)
background = pygame.mixer.music.load("/home/pi/Music/Audio_2015/bckgrnd_music_n_nr.mp3")
pygame.mixer.music.set_volume(0.3)

def is_sensor_hit(pin):
    if gpio.input(pin.value) == 0: # was ==1 pin now HIGH until activated 06/10
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
        self.velo.start(65)  # was 65 Medium speed 07/28
        self.start = 0 # test to eliminate startup sound

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
        if os.path.isfile('/home/pi/Documents/stop/shutdown/Vegas_train_shutdown') == True:
            if self.state == State.STATION_L or self.state == State.STATION_R:
                self.transition(State.SHUTDOWN)
            else:
                self.transition(State.SHUTTING_DOWN)


    def check_sensor(self, pin):
        if gpio.input(pin.value) == 0: #was ==1 but now 0  06/10
            print('Sensor hit', pin)
            self.sensorHits += 1
        else:
            self.sensorHits = 0  #should not get a false signal so should never see 06/10
        return self.sensorHits >= 1  #original was 2 07/31


    def train_go(self):
        self.velo.ChangeDutyCycle(60)  # Medium speed  original 65 07/31


    def train_stop(self):
        self.velo.ChangeDutyCycle(0)


    def wigwag_off(self):
        gpio.output(IoPin.WIGWAG_POWER.value, gpio.HIGH) #Turn off wigwag power relay
        gpio.output(IoPin.WIGWAG_SOUND.value, gpio.HIGH) #Turn off wigwag speaker relay
        #gpio.output(IoPin.STATION_SOUND.value, gpio.LOW) #turn on Vegas Station Speaker
        if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == True:
            os.remove('/home/pi/Documents/stop/train_wigwag_on')





    def wigwag_on(self):
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True: #don't go on if train pi says sound off
            return
        else:
            Path('/home/pi/Documents/stop/train_wigwag_on').touch()
            gpio.output(IoPin.STATION_SOUND.value, gpio.HIGH) #turn off Vegas Station Speaker
            gpio.output(IoPin.WIGWAG_POWER.value, gpio.LOW) # turn on Wigwag power relay
            gpio.output(IoPin.WIGWAG_SOUND.value, gpio.LOW) # turn on Wigwag speaker relay


    def station_off(self): # Vegas station speaker off may not need but might need with audience buttons
        gpio.output(IoPin.STATION_SOUND.value, gpio.HIGH)

    def station_on(self):
        gpio.output(IoPin.STATION_SOUND.value, gpio.LOW)

    def merry_xmas_on(self):
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True:
            return
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == False:
            Path('/home/pi/Documents/stop/buttons_sounds_off').touch()
            self.station_on()
            #allaboard.play()
            merryxmas.play()
            #tune()

    #def all_aboard_off(self):
    def merry_xmas_off(self):
        self.station_off()
        if os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/buttons_sounds_off')

    def all_aboard_on(self):
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True:
            return
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == False:
            Path('/home/pi/Documents/stop/buttons_sounds_off').touch()
            self.station_on()
            allaboard.play()
            #merryxmas.play()
            #tune()

    #def all_aboard_off(self):
    def all_aboard_off(self):
        self.station_off()
        if os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/buttons_sounds_off')

    def clang_on(self):
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True:
            return
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == False:
            Path('/home/pi/Documents/stop/buttons_sounds_off').touch()
            self.station_on()
            print ("clang funtion")
            clang.play()
            #tune()

    #def clang_off(self):
    def clang_off(self):
        self.station_off()
        if os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/buttons_sounds_off')


#    def run(self):
#        self.check_shutdown()
#        elapsed_sec = time.perf_counter() - self.startTime_sec
# STATION DEPARTING LEFT
#       if self.state == State.DEPARTING_L:
#            if elapsed_sec > 12:
#                if self.check_sensor(IoPin.SENSOR_PLATFORM):
#                    self.transition(State.PLATFORM_L)
#            elif elapsed_sec > 11 and self.soundPlayed == False:  #initally 10
#                self.wigwag_on()
#                #create wigwag file on
#                #self.station_off
#                if self.start > 1:
#                    #self.wigwag_on
#                    wigwag.play()
#                    self.soundPlayed = True
#                #if self.check_sensor(IoPin.SENSOR_PLATFORM):
#                #    self.transition(State.PLATFORM_L)
#            elif elapsed_sec > 10.9 and elapsed_sec < 11:
#                self.soundPlayed = False #test
#            elif elapsed_sec > 10:
#                self.train_go()
#                self.clang_off()
#            elif elapsed_sec > 4 and self.soundPlayed == False:
#                if self.start > 1:
#                    self.clang_on()
#                    self.soundPlayed = True
#            elif elapsed_sec > 3.9 and elapsed_sec < 4:
#                self.soundPlayed = False #test
#                self.all_aboard_off()
#            elif not self.soundPlayed:
#                # TODO: play departure announcement
#                #toot.play()
#                #background.play()
#                #mixer.music.set_volume(0.6)
#                #mixer.music.play()
#                #wigwag.play()
#                #clang.play()
#                if self.start > 0:
#                    self.station_on()
#                    #allaboard.play()
#                    #all_aboard_on(self)
#                    self.all_aboard_on()
#                    print("toot")
#                self.start = self.start + 1

    def run(self):
        self.check_shutdown()
        elapsed_sec = time.perf_counter() - self.startTime_sec
# STATION DEPARTING LEFT2222222222
        if self.state == State.DEPARTING_L:
            if elapsed_sec > 16:
                if self.check_sensor(IoPin.SENSOR_PLATFORM):
                    self.transition(State.PLATFORM_L)
            elif elapsed_sec > 15 and self.soundPlayed == False:  #initally 10
                self.wigwag_on()
                #create wigwag file on
                #self.station_off
                if self.start > 1:
                    #self.wigwag_on
                    wigwag.play()
                    self.soundPlayed = True
                #if self.check_sensor(IoPin.SENSOR_PLATFORM):
                #    self.transition(State.PLATFORM_L)
            elif elapsed_sec > 14.9 and elapsed_sec < 15:
                self.soundPlayed = False #test
            elif elapsed_sec > 14:
                self.train_go()
                self.clang_off()
            elif elapsed_sec > 10 and self.soundPlayed == False:
                if self.start > 1:
                    self.clang_on()
                    print("toot clang")
                    self.soundPlayed = True
            elif elapsed_sec > 9.9 and elapsed_sec < 10:
                self.soundPlayed = False
            elif elapsed_sec > 9 and elapsed_sec < 9.9:
                self.all_aboard_off()
            elif elapsed_sec > 5 and self.soundPlayed == False: #add 1 second
                if self.start > 1:
                    self.all_aboard_on()
                    print("toot aboard")
                    self.soundPlayed = True
            elif elapsed_sec > 4.9 and elapsed_sec < 5: #add 1 second
                self.soundPlayed = False #test
                self.merry_xmas_off()
            elif not self.soundPlayed:
                # TODO: play departure announcement
                #toot.play()
                #background.play()
                #mixer.music.set_volume(0.6)
                #mixer.music.play()
                #wigwag.play()
                #clang.play()
                if self.start > 0:
                    self.station_on()
                    #allaboard.play()
                    #all_aboard_on(self)
                    self.merry_xmas_on()
                    print("toot xmas")
                self.start = self.start + 1


                self.soundPlayed = True





# PLATFORM LEFT
        elif self.state == State.PLATFORM_L:
            if elapsed_sec > 7:
                if self.check_sensor(IoPin.SENSOR_PLATFORM):
                    self.transition(State.INBOUND_R)
            elif elapsed_sec > 6.5: #was 10 originally
                self.train_go()
            else:
                #self.wigwag_off()
                self.train_stop()
# AT PLATFORM BOUND FOR STATION
        elif self.state == State.INBOUND_R:
            if elapsed_sec > 46: #original 15 add 30 to 16
                self.wigwag_off() # replaced just below
                if self.check_sensor(IoPin.SENSOR_STATION):
                    self.transition(State.STATION_R)
            #elif elapsed_sec > 14: #original 14
             #   self.wigwag_off()
            elif elapsed_sec > 43: #original 12 add 30 to 13
                #self.wigwag_on()
                self.train_go()
            elif elapsed_sec > 34: #original 5 add 30 to 4
                self.wigwag_on()
                if self.soundPlayed == False:
                    #wigwag.set_volume(0.8)
                    wigwag.play()#self.train_go()
                    self.soundPlayed = True #test
            else:
                self.train_stop()
                self.wigwag_off()
#ARRIVING AT STATION FROM PLATFORM
        elif self.state == State.STATION_R:
            # test
            a = (3, 8)
            if (dt.now().minute % 10) in a and dt.now().second > 35: # was 30 chg to 35
                self.transition(State.DEPARTING_R)

            #if elapsed_sec > 15:
            #    self.transition(State.DEPARTING_R)
            if elapsed_sec > 4:
                self.sound_Played = False
                self.clang_off()
            elif not self.soundPlayed:
                self.train_stop()
                # TODO: play arrival announcement
                #clang.play()
                self.clang_on()
                self.soundPlayed = True
 # AT STATION BOUND RIGHT TOWARDS MOUNTAIN
        elif self.state == State.DEPARTING_R:
            if elapsed_sec > 8:
                if self.check_sensor(IoPin.SENSOR_MOUNTAIN):
                    self.transition(State.MOUNTAIN_R)
            elif elapsed_sec > 7:
                self.train_go()
                self.clang_off()
            elif elapsed_sec > 4 and self.soundPlayed == False:
                if self.start > 1:
                    #clang.play()
                    self.clang_on()
                    self.soundPlayed = True
            elif elapsed_sec > 3.9 and elapsed_sec < 4:
                self.soundPlayed = False #test
                self.all_aboard_off()
            elif not self.soundPlayed:
                # TODO: play departure announcement
                #allaboard.play()
                self.all_aboard_on()
                self.soundPlayed = True
                self.start = self.start + 1
# ARRIVE AT MOUNTAIN BOUND FOR BUMPER AND BACK TO MOUNTAIN
        elif self.state == State.MOUNTAIN_R:
            if elapsed_sec > 11:
                if self.check_sensor(IoPin.SENSOR_MOUNTAIN):
                    self.transition(State.INBOUND_L)
            elif elapsed_sec > 10:
                self.train_go()
            else:
                self.train_stop()
# ARRIVE AT MOUNTAIN BOUND FOR STATION
        elif self.state == State.INBOUND_L:
            if elapsed_sec > 51: # delay 11 + 40
                if self.check_sensor(IoPin.SENSOR_STATION):
                    self.transition(State.STATION_L)
            elif elapsed_sec > 50: # delay 10 + 40
                self.train_go()
            else:
                self.train_stop()
# ARRIVE AT STATION FROM MOUNTAIN
        elif self.state == State.STATION_L:
            # timed to coincide with other 2 train lines
            a = (0, 5) # departure set for leaving for platform every 5 minutes
            if (dt.now().minute % 10) in a and dt.now().second > 30:
                self.transition(State.DEPARTING_L)

            #if elapsed_sec > 15:
                #self.transition(State.DEPARTING_L)
            if elapsed_sec > 4:
                self.sound_Played = False
                self.clang_off()

            elif not self.soundPlayed:
                self.train_stop()
                # TODO: play arrival announcement
                self.clang_on()
                self.soundPlayed = True

        elif self.state == State.SHUTTING_DOWN:
            # Proceed at medium speed from wherever we are until we reach the
            # station. It doesn't matter which direction we're facing.
            self.train_go()
            if self.check_sensor(IoPin.SENSOR_STATION):
                self.transition(State.SHUTDOWN)

        elif self.state == State.SHUTDOWN:
            self.train_stop()
            gpio.output(IoPin.OUTPUT_SHUTDOWN.value, gpio.HIGH)
            time.sleep(5)  # TODO: Adjust this as needed to make sure master Pi
                           # sees the signal.
            return True

# turn on sound off program receptor from train pi wirelessly
#os.system("python3 /home/pi/Desktop/snd_off_master_1.py &")

if __name__ == '__main__':
    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)
    gpio.setup(IoPin.SENSOR_STATION.value, gpio.IN,gpio.PUD_UP) # add ,gpio.PUD_UP 6/16
    gpio.setup(IoPin.SENSOR_PLATFORM.value, gpio.IN,gpio.PUD_UP) # add ,gpio.PUD_UP 6/16
    gpio.setup(IoPin.SENSOR_MOUNTAIN.value, gpio.IN,gpio.PUD_UP)# add ,gpio.PUD_UP 6/16
    gpio.setup(IoPin.INPUT_SHUTDOWN.value, gpio.IN) # not connected 6/16
    gpio.setup(IoPin.TRAIN_FORWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_BACKWARD.value, gpio.OUT)
    gpio.setup(IoPin.TRAIN_VELOCITY.value, gpio.OUT)
    gpio.setup(IoPin.OUTPUT_SHUTDOWN.value, gpio.OUT)
    gpio.setup(IoPin.WIGWAG_POWER.value, gpio.OUT)
    gpio.setup(IoPin.WIGWAG_SOUND.value, gpio.OUT)
    gpio.setup(IoPin.STATION_SOUND.value, gpio.OUT) #added 08/12

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
        os.remove('/home/pi/Documents/stop/shutdown/Vegas_train_shutdown')
        time.sleep(3)
        if os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/buttons_sounds_off')
        time.sleep(3)
        if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/train_sounds_off')
        time.sleep(3)
        if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == True:
            os.remove('/home/pi/Documents/stop/train_wigwag_on')
        gpio.cleanup()
