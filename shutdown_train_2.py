"""Simulate the shutdown sequence on the train pi."""
import socket
import threading
import time

# Phase 2
# listen for shutdown message instead of just the connection
# send sound on/off command to master
# - maybe just an input() to toggle it?
# should master pi have the server socket?

def talk_to_master(startShutdown, shutdownComplete):
    with socket.socket() as sock:
        #sock.bind(('', 31337))
        #sock.listen()
        #conn, _ = sock.accept()
        #print('master pi has asked us to shutdown')
        #startShutdown.set() 
        #shutdownComplete.wait()
        #print('telling master pi we have shutdown')
        #conn.close()

        # TODO: replace localhost with static ip of train pi
        # port number has to match the socket.bind() of the other program.
        sock.connect(('localhost', 31337))
        print('made connection to master pi')
        while True:
            toWrite = []
            # if we want to send a message:
            #     toWrite.append(sock)
            readable, writable, _ = select.select([sock], toWrite, [], 1)
            for s in readable:
                msg = s.recv(1024)
                # if len(msg) > 0:
                #    assume we were told to shutdown


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
        print('trains doing train stuff')
        time.sleep(2)

    print('trains returning to station')
    for i in range(20, 0, -1):
        time.sleep(1)
        print(i)
    shutdownComplete.set()

    bg.join()
    print('all done!')
