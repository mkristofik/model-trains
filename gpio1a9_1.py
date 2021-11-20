##gpio1a9_1 trying to change from raspi 1 to raspi 3
##1st try correct movie path
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#>>>>>>>>>>>>> change pin 4 bouncetime to from 300 to 500
import time
from subprocess import Popen
import os
#import GPIO stuff
import RPi.GPIO as gpio

#blank background desktop
def blankscreen():
    os.system('xset s blank')
    os.system('xset s 5') #set to 1 for final version
    print('reduce blankscreen to 5 sec')
    
blankscreen()    

#setup GPIO pins:
gpio.setmode(gpio.BCM) #GPIO numbering scheme

#4 & 18 are input pins

#not using button for pin 18 available for expansion
#gpio.setup(18, gpio.IN, pull_up_down = gpio.PUD_DOWN) 
gpio.setup(4, gpio.IN, pull_up_down = gpio.PUD_UP)

gpio.setup(17, gpio.OUT) #sound pin
gpio.setup(22, gpio.OUT) #playground power pin

#pins 23-25 available for future expansion on mezzanine 
#gpio.setup(23, gpio.OUT)
#gpio.setup(24, gpio.OUT)
#gpio.setup(24, gpio.OUT)

#initially set pin 17 to off..prevents sound on reboot
gpio.output(17,True)

def playgroundon():
    print ("pin 22 on")
    gpio.output(22,True)
    
def playgroundoff():
    print ("pin 22 off")
    gpio.output(22,False)

def intermission():
     #print ("start playground")
     playgroundon()
     omxp = Popen(['omxplayer',movie_path])
     omxp.communicate()
     
     #print ("off playground")
     playgroundoff()    

movie_path = '/home/pi/Videos/drivein/drive-in_previewe.mp4'

def inputFunction(channel):
    print ('sound button pin 4 pressed')
    gpio.output(17,False)
    time.sleep(30) #time in seconds movie audio plays via push button
    gpio.output(17,True)
    
gpio.add_event_detect(4, gpio.RISING, callback=inputFunction, bouncetime=500)

# start Drive-in 

intermission()

# Create movies string

movies=[]

# Miracle on 34th Street
for i in range(1,22):  #(1,22) full movie    
  name = '/home/pi/Videos/drivein/miracle'+str(i)+'.mp4' 
  movies.append(name)
  print(name)
  
# It's a Wonderful Life       
for i in range(1,29):   #(1,29) full movie  
  name = '/home/pi/Videos/drivein/Wonderful_Life_'+str(i)+'.mp4' 
  movies.append(name)
  print(name)
  
# A Christmas Carol
for i in range(1,15):  #(1,15) full movie    
  name = '/home/pi/Videos/drivein/Xmas_Carol_'+str(i)+'.mp4' 
  movies.append(name)
  print(name)       

# Play movies  
for m in movies:
     print('Now Playing '+m)
     omxp = Popen(['omxplayer',m])
     omxp.communicate()
     intermission()

#movies over so drive-in off just playground on

playgroundon()

#gpio.cleanup()
print ("end of movie")