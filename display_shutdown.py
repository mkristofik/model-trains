import os
import time
import RPi.GPIO as GPIO

# In display_shutdown temp file for other programs to shutdown
from pathlib import Path
Path('/home/pi/Documents/model-trains/shut_it_down').touch()

# TODO: uncomment this when you want to shut down the trains
# There is no & at the end because you want to wait for this one to finish.
#os.system('python3 /home/pi/Documents/model-trains/shutdown_trains.py')

#os.system('heyu off m2') #drive in screen
#time.sleep(5)

os.system('heyu off m6') #vegas train power
time.sleep(3)

os.system('heyu off m5') #2-1-3 train power
time.sleep(3)

os.system('heyu off k8') #cross country skiers
time.sleep(3)

os.system('heyu off k7') #birds
time.sleep(3)

os.system('heyu off k6') #sledders
time.sleep(3)

os.system('heyu off k5') #downhill skiers
time.sleep(3)

os.system('heyu off k4') #skating pond
time.sleep(3)

os.system('heyu off k3') #gondola
time.sleep(3)

os.system('heyu off k2') #vegas lighting
time.sleep(3)

os.system('heyu off k1') #2-1-3 lighting
time.sleep(120)


os.remove('/home/pi/Documents/model-trains/shut_it_down')
GPIO.cleanup()


