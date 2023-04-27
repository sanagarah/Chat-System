import socket
import threading
import time
from enum import Enum
import logging

HEADER_LENGTH = 8
CONTROL_LENGTH = 8
MESSAGE_LENGTH = 256 - HEADER_LENGTH - CONTROL_LENGTH
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1234
CLIENT_ID = input('Enter client ID: ')[:8].ljust(8)
ALIVE_INTERVAL = 10  # seconds

logging.basicConfig(level=logging.DEBUG)

class Command(Enum):
    CONNECT = "CONNECT".ljust(CONTROL_LENGTH)
    QUIT = "QUIT".ljust(CONTROL_LENGTH)
    ALIVE = "ALIVE".ljust(CONTROL_LENGTH)
    LIST = "LIST".ljust(CONTROL_LENGTH)






def handle_messages(sock):
    while True:
        try:
            msg = sock.recv(256).decode()
            if not msg:  # server closed the connection
                logging.info('Server disconnected')
                sock.close()
                break
                 
            else:
                # Exchange Messages with another clients via server: 10
                # Receiving client list from server (includes tokenization of message): 10
                # Displaying Client List: 5
                print(msg.strip())
        except OSError:  # socket closed
            break


def send_alive(sock):
    while True:
        time.sleep(ALIVE_INTERVAL)
        try:
            # Sending alive message: 5
            handle_notified_message(sock, Command.ALIVE)
        except OSError:  # socket closed
            break


def handle_notified_message(sock: socket, command: Command):
  
    msg = f"{command.value}{CLIENT_ID}".encode("utf-8")[:256].ljust(256)
    sock.send(msg)
def handle_normal_message(sock: socket, msg:str):
    recipient = msg[1:msg.index(')')][:CONTROL_LENGTH].ljust(CONTROL_LENGTH)
    message = msg[msg.index(')')+1:][:MESSAGE_LENGTH].ljust(MESSAGE_LENGTH).strip()
    msg = f"{recipient}{CLIENT_ID}{message}".encode("utf-8")[:256].ljust(256)
    sock.send(msg)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    # Sending connect message: 5
    handle_notified_message(sock, Command.CONNECT)

    t = threading.Thread(target=handle_messages, args=(sock,))
    t.start()
    t2 = threading.Thread(target=send_alive, args=(sock,))
    t2.start()
    while True:
        msg = input("-> ").strip()
        # Sending Message to server (includes creation of message in specified format): 10
        if msg == '@Quit':
            # Sending quit message: 5
            handle_notified_message(sock=sock, command=Command.QUIT)
            break
        elif msg == '@List':
            handle_notified_message(sock=sock, command=Command.LIST)
            
        elif len(msg) > 0 and msg[0] == '(' and ')' in msg:
            handle_normal_message(sock=sock,msg=msg)
        else:
            logging.error("Wrong Format start with @ for command or (#id)#message when you want to send a message ")
    t.join()
    t2.join()
    sock.close()


if __name__ == '__main__':
    main()
