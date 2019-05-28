import numpy as np
import zmq

SERVER_PORT = 5858

def send_array(socket, array):
    """
    Send a numpy array with metadata over zmq
    """

    md = dict(
        dtype=str(array.dtype),
        shape=array.shape,
    )

    # SNDMORE flag specifies this is a multi-part message
    # NOBLOCK prevents getting blocked if the client disconnects
    socket.send_json(md, flags=zmq.SNDMORE|zmq.NOBLOCK)
    return socket.send(array, copy=True, track=False, flags=zmq.NOBLOCK)

def recv_array(socket):
    """
    Receive a numpy array over zmq
    """

    md = socket.recv_json()
    msg = socket.recv(copy=True, track=False)
    buf = buffer(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    A = A.reshape(md['shape'])
    return A

def poll_socket(socket, timetick = 10):
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    # wait up to 10msec
    try:
        print("Poller ready")
        while True:
            obj = dict(poller.poll(timetick))
            if socket in obj and obj[socket] == zmq.POLLIN:
                yield socket.recv_json()
    except KeyboardInterrupt:
        print ("Stopping server")
        quit()

def server_loop(handle_msg):
    for message in poll_socket(socket):
        handle_msg(socket, message)

serverAddr = "tcp://*:%s" % SERVER_PORT
print('Starting server at %s' % serverAddr)
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind(serverAddr)
