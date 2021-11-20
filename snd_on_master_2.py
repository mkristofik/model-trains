"""Turn on Vegas train sound wirelessly when train pi sound on button pressed
    _2  adding shutdown when trains are shutdown
"""
import socket
import threading
import time
import os
from pathlib import Path
import sys

def talk_to_master(startShutdown, shutdownComplete):  # upon signal from train pi
    with socket.socket() as sock:
        #sock.bind(('', 31337))
        sock.bind(('', 31333))
        sock.listen(5)
        conn, _ = sock.accept()
        print('snd_on_train pi has asked master pi to turn on sound')
        startShutdown.set()
        shutdownComplete.wait()
        print('snd_on_telling train pi that master pi turned on sound')
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
        print('Vegas train sounds off')
        if os.path.isfile('/home/pi/Documents/stop/shutdown/Vegas_train_shutdown') == True:
            sys.exit("snd_on_master_2.py program shutdown")
        time.sleep(2)

    if os.path.isfile('/home/pi/Documents/stop/train_sounds_off') == True:
            os.remove('/home/pi/Documents/stop/train_sounds_off')
    print('trains returning to station')  # this is where stuff to control Vegas sound goes
    for i in range(20, 0, -1):
        time.sleep(1)
        print(i)
    shutdownComplete.set()

    bg.join()  #reply signal to train pi that sound is off
    os.system("python3 /home/pi/Desktop/snd_off_master_2.py &")

    print('all done!')
    sys.exit("snd_on_master_2.py program off")
