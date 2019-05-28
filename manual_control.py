#!/usr/bin/env python3

import time
import sys
import zmq
import numpy as np
import pyglet
from ctypes import byref, POINTER
from pyglet.gl import *
from pyglet.window import key

window = pyglet.window.Window(640, 640, style=pyglet.window.Window.WINDOW_STYLE_DIALOG)

def recv_array(socket):
    """
    Receive a numpy array over zmq
    """

    md = socket.recv_json()
    msg = socket.recv(copy=True, track=False)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    A = A.reshape(md['shape'])
    return A

def update(dt):
    # Get an image from the camera
    print('requesting image')
    global last_img
    socket.send_json({ 'robot': { 'get_image': None }})
    last_img = recv_array(socket)
    print('img received')

def step(vels, pos=None):
    global last_img

    req = {
        "set_vels": vels,
        #"get_image": None
    }

    if pos != None:
        req['set_pos'] = pos

    socket.send_json({"robot": req})

@window.event
def on_key_press(symbol, modifiers):

    """
    if symbol == key.BACKSPACE or symbol == key.SLASH:
        print('RESET')
        env.reset()
        env.render('pyglet')
        return
    """

    if symbol == key.ESCAPE:
        sys.exit(0)

@window.event
def on_key_release(symbol, modifiers):
    pass

@window.event
def on_draw():
    img_height, img_width, _ = last_img.shape

    # Draw the human render to the rendering window
    img = np.ascontiguousarray(np.flip(last_img, axis=0))
    img_data = pyglet.image.ImageData(
        img_width,
        img_height,
        'RGB',
        img.ctypes.data_as(POINTER(GLubyte)),
        pitch=img_width * 3,
    )
    img_data.blit(
        0,
        0,
        0,
        width=window.width,
        height=window.height
    )

    # Force execution of queued commands
    glFlush()

@window.event
def on_close():
    pyglet.app.exit()

# Connect to the Gym bridge ROS node
addr_str = "tcp://%s:%s" % ('flogo.local', 5858)
#addr_str = "tcp://%s:%s" % ('localhost', 5858)
print("Connecting to %s ..." % addr_str)
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect(addr_str)

last_img = np.zeros(shape=(64, 64, 3), dtype=np.uint8)
last_img[:, :, 0] = 255

pyglet.clock.schedule_interval(update, 1/30.0)

pyglet.app.run()
