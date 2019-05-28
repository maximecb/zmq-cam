import time
from threading import Thread
import numpy as np
import cv2

obs_width = 0
obs_height = 0

video_cap = None

# Image capture thread
thread = None

# Last captured image
last_img = None

# Flag to stop the capture thread
stop_thread = False

def init(width=64, height=64):
    global obs_width
    global obs_height
    global video_cap
    global thread

    obs_width = width
    obs_height = height

    # USB webcam
    video_cap = cv2.VideoCapture(1)

    if not video_cap.isOpened():
        raise Exception("Could not open video device")

    video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Not yet implemented in OpenCV
    #video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)

    stop_thread = False

    thread = Thread(target = capture_thread, args=[])
    thread.start()

def shutdown():
    global video_cap
    global stop_thread
    stop_thread = True
    thread.join()
    video_cap.release()
    video_cap = None

def get_image():
    return last_img

def capture_thread():
    """
    Thread to capture camera images continuously.
    This is needed because OpenCV performs some amount of buffering
    on captured images.
    """

    global last_img

    while stop_thread != True:
        last_img = _get_image()

    print('Camera thread stopping')

def _get_image():
    """
    Internal image read function used by capture thread. Do not call directly.
    """

    #print('reading image')

    re, img = video_cap.read()

    #print('img read')

    if not re:
        raise RuntimeError('Could not read image from camera.')

    #print('Resizing image to {}x{}'.format(obs_width, obs_height))

    # Drop some rows and columns to speed up resizing
    img = img[::2, ::2]

    # Resize to reduce the noise in the final image
    # We resize locally to minimize network bandwidth required
    #img = imresize(img, (obs_height, obs_width, 3), interp='cubic')
    img = cv2.resize(img, (obs_height, obs_width), interpolation=cv2.INTER_CUBIC)

    #print('img resized')

    # Convert image to RGB
    img = img[...,::-1]

    img = np.ascontiguousarray(img, dtype=np.uint8)

    return img

init()
