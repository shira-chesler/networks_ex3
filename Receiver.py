import socket
import time
from statistics import mean
from Shared import receive_from, change_cc_algorithm

RECEIVER_PORT = 20059
BUFFER_SIZE = 1024
ID_XOR = b'1101000000011'

times_first_part = []
times_second_part = []


def average(lst):
    """
    Returns the average of a list
    :param lst: The list to calculate the average of
    :return: The average of the given list
    """
    return mean(lst)


def add_time(file_part, time_measured) -> None:
    """
    Adding the time it took for a part of a file to arrive to a list of this file
    :param file_part: The list of the file part we want to add the time to.
    :param time_measured: The time we would like to add
    """
    if file_part == "first":
        times_first_part.append(time_measured)
    elif file_part == "second":
        times_second_part.append(time_measured)


def print_and_calculate_mean() -> None:
    """
    Prints the list of the times it took to receive each one of the part file at each time by receiving order,
    then prints the average time of each list.
    """
    print("Times of receiving first file, Cubic algorithm: ", times_first_part)
    print("Times of receiving first file, Reno algorithm: ", times_second_part)
    print("Average time receiving files send by Cubic: ", average(times_first_part), " seconds")
    print("Average time receiving files send by Reno: ", average(times_second_part), " seconds")


def handle_request(sender_socket) -> None:
    """
    The function handles the requests from the sender. Receives the file parts
    (sending back authentication after receiving the first) and measuring the time it took for each of the file parts
    to arrive.
    it uses the change_cc_algorithm to change the Congestion Control algorithm to suit the Sender.
    The function receives from the Sender both parts of the file again and again until gets an exit message,
    then it prints the time each file part took to arrive and the mean of the times and closes the sender socket.
    :param sender_socket: The socket of the sender, through it receiving the data and sending the authentication
    message.
    """

    while True:
        size = sender_socket.recv(BUFFER_SIZE)
        sender_socket.send("ok".encode())
        start = time.time()
        print("----starting to get the first file----")
        data = receive_from(sender_socket, int(size.decode()))
        end = time.time()
        print("----finished receiving the first file----")
        add_time("first", end - start)
        sender_socket.send(ID_XOR)
        change_cc_algorithm(sender_socket)
        size = sender_socket.recv(BUFFER_SIZE)
        sender_socket.send("ok".encode())
        start = time.time()
        print("----starting to get the second file----")
        data = receive_from(sender_socket, int(size.decode()))
        end = time.time()
        print("----finished receiving the second file----")
        sender_socket.send("ok".encode())
        add_time("second", end - start)
        message = sender_socket.recv(1)
        if message.decode() == "1":
            print_and_calculate_mean()
            print("----Closing connection with sender----")
            break
        elif message.decode() == "0":
            change_cc_algorithm(sender_socket)
            print("----Getting the file again----")
            continue


def start_receiver() -> None:
    """
    Open TCP receiver socket, binds it to local host with port 20059. Listens to get one sender at a time,
    then receiving the data the sender sends using the handle_request function.
    """
    try:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        receiver.bind(('', RECEIVER_PORT))
        receiver.listen(1)
        print("-----Receiver IS UP-------")
        while True:
            sender_socket, address = receiver.accept()
            print(f"-----Sender connected. Sender address: {address}")
            handle_request(sender_socket)
            receiver.close()
            break
    except socket.error:
        print(f"Socket Error {socket.error}")
        exit(1)


if __name__ == '__main__':
    start_receiver()
