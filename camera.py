import time
from threading import Thread
import numpy as np
import cv2
import pyrealsense2 as rs

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
    global pipeline

    obs_width = width
    obs_height = height

    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 60)

    pipeline = rs.pipeline()

    print('starting pipeline')
    profile = pipeline.start(config)

    #sensor = profile.get_device().query_sensors()[1]

    #exp = sensor.get_option(rs.option.exposure)
    #print('exposure:', exp)

    #sensor.set_option(rs.option.enable_auto_exposure, 1)
    #sensor.set_option(rs.option.enable_auto_white_balance, 1)

    #sensor.set_option(rs.option.exposure, 50)
    #sensor.set_option(rs.option.gamma, 100)
    #sensor.set_option(rs.option.gain, 64)

    #sensor.set_option(rs.option.saturation, 64)
    #sensor.set_option(rs.option.sharpness, 30)
    #sensor.set_option(rs.option.white_balance, 3200)
    #sensor.set_option(rs.option.backlight_compensation, 0)

    print('camera ready')

def shutdown():
    global pipeline
    pipeline.stop()

def get_image():
    global pipeline

    frames = pipeline.wait_for_frames()
    img = frames.get_color_frame()
    img = np.asanyarray(img.get_data())

    #print(img.dtype)
    #print(img.shape)

    img = cv2.resize(img, (obs_height, obs_width), interpolation=cv2.INTER_CUBIC)

    img = np.ascontiguousarray(img, dtype=np.uint8)

    return img

init()
