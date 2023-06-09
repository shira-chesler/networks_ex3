import socket

from Shared import change_cc_algorithm, receive_from

RECEIVER_PORT = 20059
RECEIVER_NAME = 'localhost'
BUFFER_SIZE = 1024
ID_XOR = b'1101000000011'


def handle_request(sender_socket) -> None:
    """
    This function handles the request. It divides the file into 2 parts using the handle_file function,
    sends the first part of the file, then awaits for authentication.
    Next, it changes the congestion control algorithm from cubic to reno using the change_cc_algorithm function,
    and sends the second part of the file.
    Afterward, it asks the sender - whether to send the file again or not.
    If not - notifies the receiver that closes the sender socket.
    :param sender_socket: the socket sender through it connecting to the receiver
    """
    first_file_part, second_file_part = handle_file()
    while True:
        sender_socket.send(str(len(bytes(first_file_part))).encode())
        received = sender_socket.recv(2)
        if received.decode() == "ok":
            bytes_send_first = sender_socket.send(bytes(first_file_part))
            print("---------Number of bytes sent from first file:", bytes_send_first, "------------")
        auth = receive_from(sender_socket, len(ID_XOR))
        if auth.encode() == ID_XOR:
            print("-----------Authentication succeeded-----------")
        else:
            print("-----------Authentication did not succeeded-----------")
        change_cc_algorithm(sender_socket)
        sender_socket.send(str(len(bytes(second_file_part))).encode())
        received = sender_socket.recv(2)
        if received.decode() == "ok":
            bytes_send_second = sender_socket.send(bytes(second_file_part))
            print("---------Number of bytes sent from second file", bytes_send_second, "------------")
        while True:
            user = input("Enter: do you want to send again? (yes/no) ")
            if user.lower() != "yes" and user.lower() != "no":
                continue
            break
        received = sender_socket.recv(2)
        if received.decode() == "ok":
            if user.lower() == "yes":
                again_message = b'0'
                sender_socket.send(again_message)
                change_cc_algorithm(sender_socket)
            if user.lower() == "no":
                exit_message = b'1'
                sender_socket.send(exit_message)
                break
            continue


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
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((RECEIVER_NAME, RECEIVER_PORT))
        handle_request(sender_socket)
        sender_socket.close()
    except socket.error:
        print(f"Socket Error {socket.error}")
        exit(1)


if __name__ == '__main__':
    tcp_connect_to_receiver()
