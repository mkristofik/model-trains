import os
import sys
from time import sleep

os.system("python3 /home/pi/Documents/chimes_2_2021.py &")
sleep(2)
os.system("python3 /home/pi/Desktop/snd_off_master_2.py &")
sleep(2)
#os.system("python3 /home/pi/Desktop/pi_master.py &")
sleep(2)
os.system("python3 /home/pi/Documents/model-trains/dad_9.2_vegas_wigwag.py &")
sleep(2)
os.system("python3 /home/pi/Documents/buttons_5_2020.py &")
sleep(2)

print ("test startup good bye")