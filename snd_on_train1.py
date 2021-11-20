"""Tell master pi to turn on Vegas train sounds."""
import socket
import threading
import time
import os
import sys
from pathlib import Path

def talk_to_train():
    with socket.socket() as sock:
        # TODO: replace localhost with static ip of train pi
        # port number has to match the socket.bind() of the other program.
        #sock.connect(('localhost', 31337))
        sock.connect(('192.168.1.76', 31333)) #192.168.1.13 home,  ATT ...1.83 currently
        print('made connection to master pi, asked for sound turned on')

        # Wait until the train pi has signaled its shutdown is complete. We
        # don't actually need to receive any data. This call blocks until the
        # connection is gracefully closed by the train pi, or broken due to a
        # network error. In either case, we assume it has shut down.
        sock.recv(1024)
        print('Vegas train sound turn on acknowledged')


if __name__ == '__main__':
    # when shutdown is pressed create a background thread that will create a socket to
    # connect to the train pi
    # main thread goes through shutdown sequence
    # background thread waits for signal that train pi has shut down
    # when both threads have completed, gracefully exit
    while os.path.isfile('/home/pi/Documents/model-trains/sound_off') == True:
        time.sleep(1)
        print(' waiting for train pi to say yes to sound')
        if os.path.isfile('/home/pi/Documents/model-trains/shutdown/oval_shut_it_down') == True:
            print("snd_on_train1.py signing off")
            sys.exit()
        continue
    #input('Press enter to begin turn on sound...')
    bg = threading.Thread(target=talk_to_train)
    bg.start()

    # Simulate the work of shutting down master pi programs.
    for i in range(10, 0, -1):
        print(i)
        time.sleep(1)

    print('awaiting acknowledgment from master pi of Vegas train sound on')
    bg.join()
    #Turn on wait for sound off signal program
    os.system("python3 /home/pi/Desktop/snd_off_train1.py &")
    print('shutdown complete')
    sys.exit()