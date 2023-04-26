import socket
import struct

BUFFER_SIZE = 1024
CC_ALGORITHM = 13


def change_cc_algorithm(a_socket) -> None:
    """
    The function gets the current congestion control of the given socket, then changes it to the other one
    (the 2 CC algorithms the function changes from and to are Reno and Cubic).
    :param a_socket: The socket that the function changes the CC algorithm to.
    """
    cc_algo = a_socket.getsockopt(socket.IPPROTO_TCP, CC_ALGORITHM)
    cc_algo_old_str = struct.pack('I', cc_algo).decode()

    if cc_algo_old_str == "reno":
        try:
            a_socket.setsockopt(socket.IPPROTO_TCP, CC_ALGORITHM, b'cubic')
            cc_algo = a_socket.getsockopt(socket.IPPROTO_TCP, CC_ALGORITHM)
            cc_algo_str = struct.pack('I', cc_algo).decode()
            print(f"----Change CC algorithm FROM: {cc_algo_old_str} TO: {cc_algo_str}")
        except socket.error:
            print("------failed changing algorithm-------")
            exit(1)
    else:  # cc_algo == 'cubic'
        try:
            a_socket.setsockopt(socket.IPPROTO_TCP, CC_ALGORITHM, b'reno')
            cc_algo = a_socket.getsockopt(socket.IPPROTO_TCP, CC_ALGORITHM)
            cc_algo_str = struct.pack('I', cc_algo).decode()
            print(f"----Change CC algorithm FROM: {cc_algo_old_str} TO: {cc_algo_str}")
        except socket.error:
            print("-----failed changing algorithm-------")
            exit(1)


def receive_from(a_socket, size) -> str:
    """
    The function receives data with size "size" from the given socket
    :param a_socket: The given socket to receive data from
    :param size: The amount of data to receive from the socket
    :return:
    """
    received_data = b''
    while True:
        chunk = a_socket.recv(BUFFER_SIZE)
        if not chunk:
            return received_data.decode()
        received_data += chunk
        if len(received_data) == size:
            return received_data.decode()
