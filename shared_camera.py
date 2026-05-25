import cv2
import threading
import time


class SharedCamera:

    def __init__(self):

        self.cam = cv2.VideoCapture(0)

        self.latest_frame = None

        self.lock = threading.Lock()

        self.running = True

    def start(self):

        print("Camera thread started")

        while self.running:

            ret, frame = self.cam.read()

            if ret:

                with self.lock:

                    self.latest_frame = frame.copy()

            time.sleep(0.03)

    def get_frame(self):

        with self.lock:

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

