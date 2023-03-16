from threading import Thread
from queue import Queue
import time
from datetime import datetime as dt
import numpy as np
import cv2
import vlc


RTSP_STR = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! queue ! appsink drop=1"
IMG_HEIGHT = 360
IMG_WIDTH = 640
IMG_CHANNEL = 3

BUFFER_SIZE = 1
FPS = 5.0

EMPTY_FRAME = np.zeros((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNEL), np.uint8)


def calc_sleep_time(prev_time: float):
    return max(1.0 / FPS - (time.time() - prev_time), 0)


class CameraThread():
    def __init__(self, source=RTSP_STR) -> None:
        self.source = source
        self.raw_frame_queue = Queue(BUFFER_SIZE)

        self.receive_thread = Thread(target=self.receive, args=())
        # self.prepare_thread = Thread(target=self.prepare, args=())

        self.cap = cv2.VideoCapture(self.source, cv2.CAP_GSTREAMER)

    def receive(self):
        while True:
            print(dt.now())
            # start_time = time.time()

            ret, frame = self.cap.read()

            if not ret:
                print(dt.now(), "ERROR!!!")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_GSTREAMER)
                # time.sleep(calc_sleep_time(start_time)/2)
                continue

            self.raw_frame_queue.put(frame)
            # time.sleep(calc_sleep_time(start_time)/2)

    def start(self):
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def end(self):
        self.cap.release()
        # self.receive_thread.join()

    def get_frame(self):
        raw_frame = self.raw_frame_queue.get() if not self.raw_frame_queue.empty() else EMPTY_FRAME
        frame = cv2.resize(raw_frame, (IMG_WIDTH, IMG_HEIGHT))
        return frame

# gst-launch-1.0 -v rtspsrc user-id=admin user-pw=8653 location=rtsp://192.168.68.100:554/live ! decodebin ! autovideosink
TEST_URL = "rtspsrc user-id=admin user-pw=8653 location='rtsp://192.168.68.100:554/live' ! decodebin ! autovideosink"
if __name__ == "__main__":
    # camera = CameraThread("rtsp://admin:8653@192.168.68.100:554/live")

    camera = CameraThread(TEST_URL)
    camera.start()

    while True:
        start_time = time.time()

        cv2.imshow("stream", camera.get_frame())

        key = cv2.waitKey(1)
        if key == ord('q'):
            camera.end()
            cv2.destroyAllWindows()
            exit(1)

        time.sleep(calc_sleep_time(start_time))
