import socket
import time
from statistics import mean
from Shared import receive_from, change_cc_algorithm

SERVER_PORT = 20059
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


def handle_request(client_socket) -> None:
    """
    The function handles the requests from the client. Receives the file parts
    (sending back authentication after receiving the first) and measuring the time it took for each of the file parts
    to arrive.
    it uses the change_cc_algorithm to change the Congestion Control algorithm to suit the Sender.
    The function receives from the Sender both parts of the file again and again until gets an exit message,
    then it prints the time each file part took to arrive and the mean of the times and closes the client socket.
    :param client_socket: The socket of the client, through it receiving the data and sending the authentication
    message.
    """

    while True:
        size = client_socket.recv(BUFFER_SIZE)
        start = time.time()
        print("----starting to get the first file----")
        data = receive_from(client_socket, int(size.decode()))
        end = time.time()
        print("----finished receiving the first file----")
        add_time("first", end - start)
        client_socket.send(ID_XOR)
        change_cc_algorithm(client_socket)
        size = client_socket.recv(BUFFER_SIZE)
        start = time.time()
        print("----starting to get the second file----")
        data = receive_from(client_socket, int(size.decode()))
        end = time.time()
        print("----finished receiving the second file----")
        add_time("second", end - start)
        message = receive_from(client_socket, 1)
        if message == "1":
            print_and_calculate_mean()
            print("----Closing connection with client----")
            break
        elif message == "0":
            change_cc_algorithm(client_socket)
            print("----Getting the file again----")
            continue
    client_socket.close()  # close the client_socket


def start_server() -> None:
    """
    Open TCP server socket, binds it to local host with port 20059. Listens to get one client at a time,
    then receiving the data the client sends using the handle_request function.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen(1)
        print("-----SERVER IS UP-------")
        while True:
            client_socket, address = server_socket.accept()
            print(f"-----Client connected. Client address: {address}")
            handle_request(client_socket)
    except socket.error:
        print("Socket Error")
        exit(1)


if __name__ == '__main__':
    start_server()
