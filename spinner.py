import threading
import time
import sys

class Spinner:
    def __init__(self, message="Loading", delay=0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.spinner = threading.Thread(target=self._animate)

    def _animate(self):
        chars = "|/-\\"
        while self.running:
            for char in chars:
                sys.stdout.write(f'\r{self.message} {char}')
                sys.stdout.flush()
                time.sleep(self.delay)

    def start(self):
        self.running = True
        self.spinner.start()

    def stop(self):
        self.running = False
        self.spinner.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()