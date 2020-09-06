"""Simulate the shutdown sequence on the master pi."""
import socket
import threading
import time


def talk_to_train():
    with socket.socket() as sock:
        # TODO: replace localhost with static ip of train pi
        # port number has to match the socket.bind() of the other program.
        sock.connect(('localhost', 31337))
        print('made connection to train pi, asked for shutdown')

        # Wait until the train pi has signaled its shutdown is complete. We
        # don't actually need to receive any data. This call blocks until the
        # connection is gracefully closed by the train pi, or broken due to a
        # network error. In either case, we assume it has shut down.
        sock.recv(1024)
        print('shutdown acknowledged')


if __name__ == '__main__':
    # when shutdown is pressed create a background thread that will create a socket to
    # connect to the train pi
    # main thread goes through shutdown sequence
    # background thread waits for signal that train pi has shut down
    # when both threads have completed, gracefully exit

    input('Press enter to begin shutdown...')
    bg = threading.Thread(target=talk_to_train)
    bg.start()

    # Simulate the work of shutting down master pi programs.
    for i in range(10, 0, -1):
        print(i)
        time.sleep(1)

    print('master pi shutdown, waiting for train pi')
    bg.join()
    print('shutdown complete')
