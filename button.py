"""First attempt at audience control switches.
"""
#import libraries
import RPi.GPIO as GPIO
import time
import pygame
#set GPIO numbering mode and input pins
GPIO.setmode(GPIO.BOARD)

#switches/buttons
GPIO.setup(36,GPIO.IN)   #dogs
GPIO.setup(38,GPIO.IN)   #birds
GPIO.setup(40,GPIO.IN)   #wigwag

#define relays for speaker/wigwag power with HIGH being off
GPIO.setup(37,GPIO.OUT)  #dogs relay speaker
GPIO.output(37,GPIO.HIGH)
GPIO.setup(35,GPIO.OUT)  #birds relay speaker
GPIO.output(35,GPIO.HIGH)
GPIO.setup(33,GPIO.OUT)  #wigwag relay speaker
GPIO.output(33,GPIO.HIGH)
GPIO.setup(19,GPIO.OUT)  #wigwag relay power
GPIO.output(19,GPIO.HIGH)
 
#set up button sound files
pygame.mixer.init()
dogs = pygame.mixer.Sound("/home/pi/Music/Audio 2015/Xmas_Dogs_nl.wav")
birds = pygame.mixer.Sound("/home/pi/Music/Audio 2015/bird_ed_nl.wav")
wigwag = pygame.mixer.Sound("/home/pi/Music/Audio 2015/wigwag_sound_nl.wav")
 
#set up subroutines

#subroutine dogs
def false_dogs():
  time.sleep(0.02) #filter to ensure button not activated by false signal
  if GPIO.input(36)==0:
      return
  else:
      dogs.set_volume(0.5)  #play volume at 50%
      GPIO.output(37,GPIO.LOW)    #relay on for sound
      dogs.play()
      time.sleep(15)        #play time for music
      GPIO.output(37,GPIO.HIGH)   #relay off no sound
      
def false_birds():
  time.sleep(0.02) #filter to ensure button not activated by false signal
  if GPIO.input(38)==0:
      return
  else:
      birds.set_volume(0.5)  #play volume at 50%
      GPIO.output(35,GPIO.LOW)    #relay on for sound
      birds.play()
      time.sleep(25)         #play time for music
      GPIO.output(35,GPIO.HIGH)   #relay off no sound
      
def false_wigwag():
  time.sleep(0.02) #filter to ensure button not activated by false signal
  if GPIO.input(40)==0:
      return
  else:
      wigwag.set_volume(0.5) #play volume at 50%
      wigwag.play()
      GPIO.output(19,GPIO.LOW)    #power relay on 
      GPIO.output(33,GPIO.LOW)    #relay on for sound
      time.sleep(25)         #play time for music
      GPIO.output(33,GPIO.HIGH)   #relay off no sound
      GPIO.output(19,GPIO.HIGH)   #power relay off 
      
#main program
try:
    while True:
        if GPIO.input(36)==0:           #dogs button open
           GPIO.output(37,GPIO.HIGH)   #dogs relay off no sound
           
        else:
            false_dogs()
            
        if GPIO.input(38)==0:           #birds button open
           GPIO.output(35,GPIO.HIGH)   #birds relay off no sound
           
        else:
            false_birds()
            
        if GPIO.input(40)==0:           #wigwag button open
           GPIO.output(33,GPIO.HIGH)   #wigwag relay off no sound
           GPIO.output(19,GPIO.HIGH)   #wigwag power relay off 
        else:
            false_dogs()    
