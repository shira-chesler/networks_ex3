import socket
import time

from Shared import change_cc_algorithm, receive_from, CC_ALGORITHM

SERVER_PORT = 60059
SERVER_NAME = 'localhost'
BUFFER_SIZE = 1024
ID_XOR = b'1101000000011'


def handle_request(client_socket) -> None:
    """
    This function handles the request. It divides the file into 2 parts using the handle_file function,
    sends the first part of the file, then awaits for authentication.
    Next, it changes the congestion control algorithm from cubic to reno using the change_cc_algorithm function,
    and sends the second part of the file.
    Afterward, it asks the client - whether to send the file again or not.
    If not - notifies the receiver that closes the client socket.
    :param client_socket: the socket client through it connecting to the receiver
    """
    first_file_part, second_file_part = handle_file()
    # client_socket.setsockopt(socket.IPPROTO_TCP, CC_ALGORITHM, b'tahoe')
    while True:
        client_socket.send(str(len(bytes(first_file_part))).encode())
        bytes_send_first = client_socket.send(bytes(first_file_part))
        print("---------Number of bytes sent from first file:", bytes_send_first, "------------")
        auth = receive_from(client_socket, len(ID_XOR))
        if auth.encode() == ID_XOR:
            print("-----------Authentication succeeded-----------")
        else:
            print("-----------Authentication did not succeeded-----------")
        change_cc_algorithm(client_socket)
        client_socket.send(str(len(bytes(second_file_part))).encode())
        bytes_send_second = client_socket.send(bytes(second_file_part))
        print("---------Number of bytes sent from second file", bytes_send_second, "------------")
        while True:
            user = input("Enter: do you want to send again? (yes/no) ")
            if user.lower() != "yes" and user.lower() != "no":
                continue
            break
        if user.lower() == "yes":
            again_message = b'0'
            client_socket.send(again_message)
            change_cc_algorithm(client_socket)
            continue
        if user.lower() == "no":
            exit_message = b'1'
            client_socket.send(exit_message)
            time.sleep(1)
            break
    # client_socket.close()


def handle_file() -> tuple:
    """
    The function reads the given file, then divides it into 2 lists and returns them
    :return: the file divided into 2 lists
    """
    first_part = []
    second_part = []
    file = open("file.txt", "rb")
    bts = file.read()
    file.close()
    mid = int(len(bts) / 2)
    row_in_file = 0
    for row in bts:
        row_in_file += 1
        if row_in_file < mid:
            first_part.append(row)
        else:
            second_part.append(row)
    return first_part, second_part


def tcp_connect_to_receiver() -> None:
    """
    Open TCP socket in order to connect to the receiver TCP socket
    """
    print("----------TCP Connection----------")
    try:
        client_socket = socket.socket()
        client_socket.connect((SERVER_NAME, SERVER_PORT))
        handle_request(client_socket)
    except socket.error:
        print("Socket Error")
        exit(1)


if __name__ == '__main__':
    tcp_connect_to_receiver()
