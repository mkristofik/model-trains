import time
from time import sleep
from pathlib import Path
import os.path
import sys
import pygame
global sd

pygame.init()
pwroff = pygame.mixer.Sound("/home/pi/Music/Power_Off_nr.wav")


sd = 0
def checkbfsd():
    if os.path.isfile('/home/pi/Documents/model-trains/back_and_forth_off'):
        sleep(2)
        os.remove('/home/pi/Documents/model-trains/shut_it_down')
        sleep(5)
        print ("removed shut_it_down_bf")
        os.remove('/home/pi/Documents/model-trains/back_and_forth_off')
        sleep(5)
        print ("removed back_and_forth_off")
        global sd
        sd = 1
    else:
        return
def checkovalsd():
    if os.path.isfile('/home/pi/Documents/model-trains/oval_off'):
        sleep(2)
        os.remove('/home/pi/Documents/model-trains/oval_shut_it_down')
        sleep(5)
        print ("removed oval_shut_it_down_bf")
        os.remove('/home/pi/Documents/model-trains/oval_off')
        sleep(5)
        print ("removed oval_off")
        global sd
        sd = 1
    else:
        return


# print shutdown file for bf
Path('/home/pi/Documents/model-trains/shut_it_down').touch()
print("created bf shutdown file")
startTime_sec = time.perf_counter()
while sd == 0 and time.perf_counter() - startTime_sec < 360:
    checkbfsd()
    sleep(1)
    pass
if time.perf_counter() - startTime_sec > 360:
    os.remove('/home/pi/Documents/model-trains/shut_it_down')
    sleep(5)

# shutdown file for oval
sd = 0
Path('/home/pi/Documents/model-trains/oval_shut_it_down').touch()
print("created oval shutdown file")
startTime_sec = time.perf_counter()
while sd == 0 and time.perf_counter() - startTime_sec < 60:
    checkovalsd()
    sleep(1)
    pass
if time.perf_counter() - startTime_sec > 60:
    os.remove('/home/pi/Documents/model-trains/oval_shut_it_down')
    sleep(5)
if os.path.isfile('/home/pi/Documents/model-trains/sound_off') == True:
    os.remove('/home/pi/Documents/model-trains/sound_off')
sleep(3)
pwroff.set_volume(0.2)
pwroff.play()
sleep(3)
#GPIO.cleanup()
print("see you later")
sleep(3)
os.system("sudo shutdown -h now")
#sys.exit()
