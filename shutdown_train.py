"""Simulate the shutdown sequence on the train pi."""
import socket
import threading
import time


def talk_to_master(startShutdown, shutdownComplete):
    with socket.socket() as sock:
        sock.bind(('', 31337))
        sock.listen()
        conn, _ = sock.accept()
        print('master pi has asked us to shutdown')
        startShutdown.set() 
        shutdownComplete.wait()
        print('telling master pi we have shutdown')
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
        print('trains doing train stuff')
        time.sleep(2)

    print('trains returning to station')
    for i in range(20, 0, -1):
        time.sleep(1)
        print(i)
    shutdownComplete.set()

    bg.join()
    print('all done!')
