import socket
import select
import logging

HEADER_LENGTH = 256
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

logging.basicConfig(level=logging.DEBUG)

sockets_list = [server_socket]

clients = {}
clientIds = []

logging.debug(f'Listening for connections on {IP}:{PORT}')


def receive_message(client_socket):
    try:
        message_data = client_socket.recv(HEADER_LENGTH)
        if not len(message_data):
            return False
        command = message_data[0:8].decode()
        client = message_data[8:16].decode()
        message = message_data[16:256].decode()

        return {'Command': command.strip(), 'client': client.strip(), "message": message.strip()}
    except:
        return False


def sendingUsersList(client_socket, sendForOne: bool = False):
    msg = f"Online Users: {clientIds}".encode("utf-8")[:256].ljust(256)
    # Creating Client List: 5
    # Sending Client List: 5
    # Resetting Client life on receiving alive message: 5
    for client_socket in clients:
        if not sendForOne:
            client_socket.send(msg)
            continue

        if client_socket == notified_socket:
            client_socket.send(msg)


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            print(user)
            if user is False:
                continue
            # Adding new Client to List: 5
            sockets_list.append(client_socket)
            clients[client_socket] = user
            clientIds.append(user["client"])
            logging.info(
                f'Accepted new connection from {client_address[0]}:{client_address[1]} username:{user["client"]}')
            sendingUsersList(client_socket)
        else:
            message = receive_message(notified_socket)
            # Message is empty
            if message is False:
                logging.info(
                    f'Closed connection from {clients[notified_socket]["client"]}')
                # Deleting Client from List: 5
                # Informing about change in List: 5
                sockets_list.remove(notified_socket)
                clientIds.remove(clients[notified_socket]["client"])
                del clients[notified_socket]
                sendingUsersList(client_socket)

                continue
            # When client Quit
            if message['Command'] == "QUIT":
                logging.info(
                    f'Closed connection from {clients[notified_socket]["client"]}')
                # Deleting Client from List: 5
                # Informing about change in List: 5
                sockets_list.remove(notified_socket)
                clientIds.remove(clients[notified_socket]["client"])
                del clients[notified_socket]
                sendingUsersList(client_socket)
                continue
            # When client asks for list
            if message['Command'] == "LIST":
                logging.debug(
                    f'Ask for Lists connection from {clients[notified_socket]["client"]}')
                sendingUsersList(client_socket, sendForOne=True)
                continue
            # When client ALIVE
            if message['Command'] == "ALIVE":
                logging.debug(message)  # show only on debug mode

            if message['Command'].startswith("g"):
                usersString = message['Command'][1:]
                usersList = usersString.split(",")
                print(usersString)
                print(usersList)
                print(clientIds)
                senderID = message['client']
                message = message['message']

                for user in usersList:
                    if (user not in clientIds):
                        msg = f"No User with Id:{user}".encode(
                            "utf-8")[:256].ljust(256)
                        for client_socket in clients:
                            if client_socket == notified_socket:
                                client_socket.send(msg)
                    else:
                        msg = f"\nfrom:{senderID}\nmsg:{message} ".encode(
                            "utf-8")[:256].ljust(256)
                        for client_socket in clients:
                            if clients[client_socket]['client'] == user:
                                client_socket.send(msg)

                    continue

            else:
                receiverID = message['Command']
                senderID = message['client']
                message = message['message']
                # Case if user not exist in the list
                # Reply Message if message for offline Client: 5
                if (receiverID not in clientIds):
                    msg = f"No User with Id:{receiverID}".encode(
                        "utf-8")[:256].ljust(256)
                    for client_socket in clients:
                        if client_socket == notified_socket:
                            client_socket.send(msg)
                else:
                    # \nfrom:{senderID}\nmsg: is always less then 16 so we are safe
                    # Forward/Reply Message to client (includes creation of message in specified format): 5
                    msg = f"\nfrom:{senderID}\nmsg:{message} ".encode(
                        "utf-8")[:256].ljust(256)
                    for client_socket in clients:
                        if clients[client_socket]['client'] == receiverID:
                            client_socket.send(msg)

                continue

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
