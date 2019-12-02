# import for X-10 programming
import os
import sys
from time import sleep
# import for sound
import pygame
import RPi.GPIO as GPIO

# Clean up any latent state from a previous run
GPIO.setwarnings(False)
GPIO.cleanup()

# add sounds using pygame
pygame.init()
# trolley toot toot sound
toot = pygame.mixer.Sound("/home/pi/Music/Audio 2015/toot_toot_nl.wav")
# ice skaters intro music
skaters = pygame.mixer.Sound("/home/pi/Music/Audio 2015/charlie_nr_n.wav")
# bird sounds
birds = pygame.mixer.Sound("/home/pi/Music/Audio 2015/bird_ed_nl.wav")

os.system("python3 /home/pi/Documents/foo.py &")
os.system("python3 /home/pi/Documents/bar.py &")
#os.system("python3 /home/pi/Documents/chimes.chimes.py &")
#os.system("python3 /home/pi/Documents/button.py &")
# run os.system Vegas train right before Train X-10 
sys.exit()

#os.system("sudo /home/pi/.heyu/heyu-2.10")
#sleep(5) #slight pause to starup heyu program not sure need
# turn on Gondola
os.system("heyu on k3")
sleep(5)
#sleep(1)
# turn on skating pond
os.system("heyu on k4")
skaters.play()
sleep(25)
#sleep(1)
# turn on drive in screen
os.system("heyu on m2")
sleep(5)
#sleep(1)
# turn on downhill skiers
os.system("heyu on k5")
sleep(5)
#sleep(1)
# turn on sledders
os.system("heyu on k6")
sleep(5)
#sleep(1)
# turn on birds
os.system("heyu on k7")
birds.play()
sleep(25)
#sleep(1)
# turn on cross country skiers
os.system("heyu off k3") #switch to k9 on when ready 12/1
sleep(5)
#sleep(1)
# turn on trains
#os.system("python3 /home/pi/Documents/model-trains/vegas.py &")
os.system("heyu off k7") #switch to k9 on when ready 12/1
sleep(5)
#sleep(1)


print ("good bye")