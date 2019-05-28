#!/usr/bin/env python3

import time
import sys
import signal
import zmq
import camera
import server

def shutdown(signal=None, frame=None):
    """
    Called when the program is killed/terminated
    """

    print("Shutting down")

    # Close the camera
    camera.shutdown()

    time.sleep(0.25)
    sys.exit(0)

# Catch the interrupt signal
signal.signal(signal.SIGINT, shutdown)

def handle_msg(socket, msg):
    msg = msg['robot']

    print(msg)

    # TODO: specify resolution here?
    if 'get_image' in msg:
        #width, height = msg['get_image']
        image = camera.get_image()
        server.send_array(socket, image)

    if 'stop' in msg:
        drive.stop()

server.server_loop(handle_msg)

shutdown()
