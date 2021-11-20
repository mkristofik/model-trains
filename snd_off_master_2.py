"""Turn off Vegas train sound wirelessly when train pi sound is off
   _2 program adds shutdown program if master calls for train shutdown
"""
import socket
import threading
import time
from pathlib import Path
import sys
import os

def talk_to_master(startShutdown, shutdownComplete):  # upon signal from train pi
    with socket.socket() as sock:
        #sock.bind(('', 31337))
        sock.bind(('', 31330))
        sock.listen(5)
        conn, _ = sock.accept()
        print('train pi has asked master pi to turn off sound')
        startShutdown.set()
        shutdownComplete.wait()
        print('telling train pi master pi has turned off sound')
        #os.system("python3 /home/pi/Desktop/snd_on_master.py &")
        conn.close()


if __name__ == '__main__':
    # create a background thread to listen to a connection from the master pi
    # upon connection, background thread sets shutdown event
    # main thread begins shutdown
    # background thread waits for shutdown complete
    # background thread signals master pi that shutdown is complete
    # main thread joins on background thread

    startShutdown = threading.Event()
    shutdownComplete = threading.Event()
    bg = threading.Thread(target=talk_to_master, args=(startShutdown, shutdownComplete))
    bg.start()

    # Simulate the main loop of the train program.
    while not startShutdown.is_set():
        print('Vegas train sounds on')
        if os.path.isfile('/home/pi/Documents/stop/shutdown/Vegas_train_shutdown') == True:
            print('snd_off_master _2 program should shutdown')
            sys.exit("snd_off_master_2.py program shutdown")
        time.sleep(2)

    print('Vegas trains sound turning off')  # this is where stuff to control Vegas sound goes
    Path('/home/pi/Documents/stop/train_sounds_off').touch() #create sound off file
    for i in range(5, 0, -1):
        time.sleep(1)
        print(i)
    shutdownComplete.set()

    bg.join()  #reply signal to train pi that sound is off
    os.system("python3 /home/pi/Desktop/snd_on_master_2.py &")
    print('all done!')
    print('snd_off_master_2,py is shutdown')
    sys.exit()
