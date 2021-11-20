# CHURCH BELL CHIMES CONTROL
#  near finished
# TO DO
# add shutdown stop path
# clean up ending with erase path for chimes ending
# erase fortran programming
#version 2 corrected a couple lines
import RPi.GPIO as GPIO
import pygame
import time
# importing time to get hours and minutes using strftime
from time import gmtime, strftime, localtime
import os
# In each program you want to shut down:
from pathlib import Path
#example below:
#if os.path.isfile(' /home/pi/Documents/model-trains/shut_it_down'):
    # do shut down code here

#set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)
#elinate errors on shutdown
GPIO.setwarnings(False)
#define relays for speaker with HIGH being off
GPIO.setup(31,GPIO.OUT)  #church relay speaker
GPIO.output(31,GPIO.HIGH)
# for practice and reference printing hour time and seconds GMT or localtime to be deleted
#print(strftime("%I:%M:%S", localtime()))
#print(strftime("%I", localtime()))
def transition():
    global startTime_sec
    startTime_sec = time.perf_counter()
    print("transition")
def chimes(clock,delay):
    global soundPlayed
    elapsed_sec = time.perf_counter() - startTime_sec
    if elapsed_sec > 60:
        soundPlayed = False
        return


    if soundPlayed == False:
        print('create file')
        Path('/home/pi/Documents/stop/pause_background_music').touch()
        GPIO.output(31,GPIO.LOW) #relay switch from background to church
        bellfile = '/home/pi/Documents/chimes/bell_' + str(clock) +'_nr_n[1].wav'
        pygame.mixer.music.load(bellfile)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(.5)
        print("playrd",clock)
        soundPlayed = True
    if elapsed_sec > delay:
        GPIO.output(31,GPIO.HIGH) #relay switch from church to background

        if os.path.isfile('/home/pi/Documents/stop/pause_background_music') == True:
            os.remove('/home/pi/Documents/stop/pause_background_music')
            print("removed file")


def strike(clock,delay):
    global soundPlayed

    elapsed_sec = time.perf_counter() - startTime_sec
    if elapsed_sec > 60:
        soundPlayed = False
        return
    if elapsed_sec > delay:
        GPIO.output(31,GPIO.HIGH) #relay switch from church back to background
        #print (delay, "seconds")
        if os.path.isfile('/home/pi/Documents/stop/pause_background_music') == True:
            os.remove('/home/pi/Documents/stop/pause_background_music')
            print("removed file")


    if soundPlayed == False:
        print("should be creating pause file")
        Path('/home/pi/Documents/stop/pause_background_music').touch()
        GPIO.output(31,GPIO.LOW) #relay switch from background to church
        bellfile = '/home/pi/Documents/chimes/strike_sp_' + str(clock) +'_nr_n[1].wav'
        pygame.mixer.music.load(bellfile)
        pygame.mixer.music.set_volume(.5)
        pygame.mixer.music.play()
        soundPlayed = True
        print("hour", clock)


global soundPlayed
startTime_sec = time.perf_counter()
soundPlayed = False

sec = strftime("%S", localtime())
sec = int(sec)

min = strftime("%M", localtime())
min = int(min)

#start writing chimes/clock portion
pygame.mixer.init()

count = 0

#while count < 1440: #program runs a days worth
while count >= 0: #program always runs
   min = strftime("%M", localtime())
   min = int(min)
   hr = strftime("%I", localtime())
   hr= int(hr)
   if min == 15:
       if soundPlayed == False:
           transition()
       chimes(clock=15,delay=6)



   elif min == 30:
       if soundPlayed == False:
           transition()

       chimes(clock=30,delay=10)


   elif min == 45:
       if soundPlayed == False:
           transition()
       chimes(clock=45,delay=15)


   elif min == 0 and hr == 12:
       if soundPlayed == False:
           transition()
       strike(clock=12,delay=45)


   elif min == 0 and hr == 11:
       if soundPlayed == False:
           transition()
       strike(clock=11,delay=43)

   elif min == 0 and hr == 10:
       if soundPlayed == False:
           transition()
       strike(clock=10,delay=41)

   elif min == 0 and hr == 9:
       if soundPlayed == False:
           transition()
       strike(clock=9,delay=39)

   elif min == 0 and hr == 8:
       if soundPlayed == False:
           transition()
       strike(clock=8,delay=37)

   elif min == 0 and hr == 7:
       if soundPlayed == False:
           transition()
       strike(clock=7,delay=35)

   elif min == 0 and hr == 6:
       if soundPlayed == False:
           transition()
       strike(clock=6,delay=33)

   elif min == 0 and hr == 5:
       if soundPlayed == False:
           transition()
       strike(clock=5,delay=31)

   elif min == 0 and hr == 4:
       if soundPlayed == False:
           transition()
       strike(clock=4,delay=29)

   elif min == 0 and hr == 3:
       if soundPlayed == False:
           transition()
       strike(clock=3,delay=27)

   elif min == 0 and hr == 2:
       if soundPlayed == False:
           transition()
       strike(clock=2,delay=25)

   elif min == 0 and hr == 1:
       if soundPlayed == False:
           transition()
       strike(clock=1,delay=23)

   elif os.path.isfile('/home/pi/Documents/stop/shutdown_chimes') == True:
       break

#delay a minute so bells don't ring twice. changed delay to cycle time
   time.sleep(0.1)

print('Exiting')
os.remove ('/home/pi/Documents/stop/shutdown_chimes')
GPIO.cleanup()
