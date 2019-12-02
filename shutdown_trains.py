"""Controller script for shutting down the train lines. Signal the shutdown and
wait for an ACK that says they have shut down.
"""
import RPi.GPIO as gpio
import time


# Define constants to give names to the GPIO pins.
OUTPUT_SHUTDOWN = 5
INPUT_SHUTDOWN = [7, 11, 13]
shutdownCount = {pin: 0 for pin in INPUT_SHUTDOWN}


def check_status():
    for pin in INPUT_SHUTDOWN:
        if gpio.input(pin) == 1:
            shutdownCount[pin] += 1
        else:
            shutdownCount[pin] = 0

    return all(shutdownCount[pin] >= 2 for pin in shutdownCount)


if __name__ == '__main__':
    # init GPIO and pins
    gpio.setmode(gpio.BOARD)
    gpio.setup(OUTPUT_SHUTDOWN, gpio.OUT)
    for pin in INPUT_SHUTDOWN:
        gpio.setup(pin, gpio.IN)

    # signal all trains to shut down
    gpio.output(OUTPUT_SHUTDOWN, gpio.HIGH)

    # monitor for them to respond that they have shut down.
    try:
        isDone = False
        while not isDone:
            isDone = check_status()
            time.sleep(0.5)  # 2 Hz clock
        print('All train lines have shut down.')
    except KeyboardInterrupt:
        print('Stopping manually')
    finally:
        gpio.cleanup()
