import threading
import time
import sys

class Spinner:
    """
    A simple text-based spinner class to display a loading animation in the console.

    Attributes:
        message (str): The message to display next to the spinner. Defaults to "Loading".
        delay (float): The delay between each animation step in seconds. Defaults to 0.1.
        running (bool): Whether the spinner is currently running. Defaults to False.
        spinner (threading.Thread): The thread that runs the spinner animation.

    Methods:
        start(): Starts the spinner animation.
        stop(): Stops the spinner animation.
    """
    
    def __init__(self, message="Loading", delay=0.1):
        """
        Initializes a new Spinner instance.

        Args:
            message (str, optional): The message to display next to the spinner. Defaults to "Loading".
            delay (float, optional): The delay between each animation step in seconds. Defaults to 0.1.
        """
        self.message = message
        self.delay = delay
        self.running = False
        self.spinner = threading.Thread(target=self._animate)

    def _animate(self):
        """
        Animates the spinner by printing the message and a rotating character.
        """
        chars = "|/-\\"
        while self.running:
            for char in chars:
                sys.stdout.write(f'\r{self.message} {char}')
                sys.stdout.flush()
                time.sleep(self.delay)

    def start(self):
        """
        Starts the spinner animation.
        """
        self.running = True
        self.spinner.start()

    def stop(self):
        """
        Stops the spinner animation and clears the console line.
        """
        self.running = False
        self.spinner.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()