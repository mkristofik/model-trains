# AUDIENCE BUTTON CONTROL AND BACKGROUND MUSIC
#  near finished
# TO DO
# add shutdown stop path
# clean up ending with erase path for buttons ending
# erase fortran programming
# background music on/off option and volume control
# adding carnival music button w/same relay/speaker as dogs

#import libraries
import RPi.GPIO as GPIO
import time
import pygame
from pathlib import Path
import sys
from time import sleep
import os


#set GPIO numbering mode and input pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#switches/buttons
#GPIO.setup(36,GPIO.IN)   #dogs
GPIO.setup(36,GPIO.IN,GPIO.PUD_UP)
#GPIO.setup(38,GPIO.IN)   #birds
GPIO.setup(38,GPIO.IN,GPIO.PUD_UP)
#GPIO.setup(40,GPIO.IN)   #wigwag
GPIO.setup(40,GPIO.IN,GPIO.PUD_UP)
#GPIO.setup(36,GPIO.IN)   #carnival
GPIO.setup(32,GPIO.IN,GPIO.PUD_UP)
#define relays for speaker/wigwag power with HIGH being off
GPIO.setup(37,GPIO.OUT)  #dogs relay speaker
GPIO.output(37,GPIO.HIGH)
GPIO.setup(35,GPIO.OUT)  #birds relay speaker
GPIO.output(35,GPIO.HIGH)
GPIO.setup(21,GPIO.OUT)  #wigwag relay speaker was 33
GPIO.output(21,GPIO.HIGH)
GPIO.setup(19,GPIO.OUT)  #wigwag relay power was 19
GPIO.output(19,GPIO.HIGH)

#set up button sound files
pygame.mixer.init()
dogs = pygame.mixer.Sound("/home/pi/Music/Audio_2015/Xmas_Dogs_nl.wav")
birds = pygame.mixer.Sound("/home/pi/Music/Audio_2015/bird_ed_nl.wav")
wigwag = pygame.mixer.Sound("/home/pi/Music/Audio_2015/wigwag_sound_nl.wav")
carnival = pygame.mixer.Sound("/home/pi/Music/Audio_2015/merrygornd_nl.wav")
#background = pygame.mixer.music.load("/home/pi/Music/Audio_2015/bckgrnd_music_n_nr.mp3")
background = pygame.mixer.music.load("/home/pi/Music/Audio_2015/background_combo_nr.mp3")
pygame.mixer.music.set_volume(0.10)

#set up subroutines

#subroutine carnival
def false_carnival(delay,cycle):
    global carnivalsoundPlayed
    global startTime_sec
    if cycle == 0:
      startTime_sec = time.perf_counter()

    elapsed_sec = time.perf_counter() - startTime_sec
    if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == False and carnivalsoundPlayed == False and os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == False:
        Path('/home/pi/Documents/stop/train_sounds_off').touch() #turn off train  sounds
        pygame.mixer.music.pause()
        carnival.set_volume(0.9)  #play volume at 50%
        GPIO.output(37,GPIO.LOW)    #relay on for sound
        carnival.play()
        print ("play carnival")
        carnivalsoundPlayed = True
    if elapsed_sec > delay and carnivalsoundPlayed == True:
        GPIO.output(37,GPIO.HIGH)   #relay off no sound
        pygame.mixer.music.unpause()
        os.remove('/home/pi/Documents/stop/train_sounds_off')
        carnivalsoundPlayed = False
        return


#subroutine dogs
def false_dogs(delay,cycle):
    global dogsoundPlayed
    global startTime_sec
    if cycle == 0:
      startTime_sec = time.perf_counter()

    elapsed_sec = time.perf_counter() - startTime_sec

    if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == False and dogsoundPlayed == False and os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == False:
        Path('/home/pi/Documents/stop/train_sounds_off').touch() #turn off train  sounds
        pygame.mixer.music.pause()
        dogs.set_volume(0.9)  #play volume at 50%
        GPIO.output(37,GPIO.LOW)    #relay on for sound
        dogs.play()
        print ("play dogs")
        dogsoundPlayed = True
    if elapsed_sec > delay and dogsoundPlayed == True:
        GPIO.output(37,GPIO.HIGH)   #relay off no sound
        pygame.mixer.music.unpause()
        os.remove('/home/pi/Documents/stop/train_sounds_off')
        dogsoundPlayed = False
        return

# Subroutine Birds
def false_birds(delay,cycle):
    global birdssoundPlayed
    global startTime_sec

    if cycle == 0:
      startTime_sec = time.perf_counter()

    elapsed_sec = time.perf_counter() - startTime_sec

    if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == False and birdssoundPlayed == False and os.path.isfile('/home/pi/Documents/stop/buttons_sounds_off') == False:
        Path('/home/pi/Documents/stop/train_sounds_off').touch() #turn off train  sounds
        pygame.mixer.music.pause()
        birds.set_volume(0.5) #play volume at 50%

        print("play birds")
        GPIO.output(35,GPIO.LOW)    #sound relay on
        birds.play()
        birdssoundPlayed = True
      #time.sleep(10)         #play time for music
    if elapsed_sec > delay and birdssoundPlayed == True:
        GPIO.output(35,GPIO.HIGH)   #relay off no sound
        pygame.mixer.music.unpause()
        os.remove('/home/pi/Documents/stop/train_sounds_off')
        birdssoundPlayed = False
        return

# Subroutine wigwag
def false_wigwag(delay,cycle):
    global wigwagsoundPlayed
    global startTime_sec

    if cycle == 0:
        startTime_sec = time.perf_counter()

    elapsed_sec = time.perf_counter() - startTime_sec

    if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == False and wigwagsoundPlayed == False:
        Path('/home/pi/Documents/stop/train_sounds_off').touch() #turn off train  sounds
        Path('/home/pi/Documents/stop/train_wigwag_on').touch() #let train program know wigwag on
        wigwag.set_volume(0.5) #play volume at 50%
        wigwag.play()
        print("play wigwag")
        GPIO.output(19,GPIO.LOW)    #power relay on
        GPIO.output(21,GPIO.LOW)    #relay on for sound was 33
        wigwagsoundPlayed = True
      # delay is playtime for music
    if elapsed_sec > delay and wigwagsoundPlayed == True:

        GPIO.output(21,GPIO.HIGH)
        GPIO.output(19,GPIO.HIGH)   #power relay off
        os.remove('/home/pi/Documents/stop/train_sounds_off')
        os.remove('/home/pi/Documents/stop/train_wigwag_on')
        wigwagsoundPlayed = False

        return


#main program
global dogsoundPlayed
global birdssoundPlayed
global wigwagsoundPlayed
global carnivalsoundPlayed

dogsoundPlayed = False
birdssoundPlayed = False
wigwagsoundPlayed = False
carnivalsoundPlayed = False
pause = False
try:
    pygame.mixer.music.play(0)



    #pygame.mixer.music.queue("/home/pi/Music/Audio_2015/Peaceful_Xmas_Display_version_n_nr.mp3")
    while True:
        #pygame.mixer.music.queue("/home/pi/Music/Audio_2015/Peaceful_Xmas_Display_version_n_nr.mp3")
        if os.path.isfile('/home/pi/Documents/stop/pause_background_music') == True: #pause for chimes
            pygame.mixer.music.pause()
            pause = True
        if os.path.isfile('/home/pi/Documents/stop/pause_background_music') == False and pause == True:
            pygame.mixer.music.unpause()
            pause = False

        # Dog button pressed
        if GPIO.input(36)==0 and birdssoundPlayed == False and wigwagsoundPlayed == False and carnivalsoundPlayed == False:
            false_dogs(delay=29,cycle=0)
        if dogsoundPlayed == True:
            false_dogs(delay=29,cycle=1)

        # Bird button pressed
        if GPIO.input(38)==0 and dogsoundPlayed == False and wigwagsoundPlayed == False and carnivalsoundPlayed == False:           #dogs button open
            false_birds(delay=25,cycle=0)
        if birdssoundPlayed == True:
            false_birds(delay=25,cycle=1)


        # Wigwag button pressed
        if GPIO.input(40)==0 and dogsoundPlayed == False and birdssoundPlayed == False and carnivalsoundPlayed == False:

            false_wigwag(delay=10,cycle=0)
        if wigwagsoundPlayed == True:
            false_wigwag(delay=10,cycle=1)

        # Carnival button pressed
        if GPIO.input(32)==0 and birdssoundPlayed == False and wigwagsoundPlayed == False and dogsoundPlayed == False:
            false_carnival(delay=20,cycle=0)
        if carnivalsoundPlayed == True:
            false_carnival(delay=20,cycle=1)

        if os.path.isfile('/home/pi/Documents/stop/shutdown_buttons') == True:
            break

        time.sleep(0.1) #10 hrtz loop

except KeyboardInterrupt:
  pygame.mixer.music.stop()
  #os.remove('/home/pi/Documents/stop/shutdown_buttons')
  GPIO.cleanup()
  print("quit test")

pygame.mixer.music.stop()
os.remove('/home/pi/Documents/stop/shutdown_buttons')
if os.path.isfile('/home/pi/Documents/stop/train_wigwag_on') == True:
    os.remove('/home/pi/Documents/stop/train_wigwag_on')
if os.path.isfileos.remove('/home/pi/Documents/stop/train_sounds_off') == True:
    os.remove('/home/pi/Documents/stop/train_sounds_off')
if os.path.isfile('/home/pi/Documents/stop/pause_background_music') == True:
    os.remove('/home/pi/Documents/stop/pause_background_music')
GPIO.cleanup()
print("shutdown test")
