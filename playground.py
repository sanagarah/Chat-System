
HEADER_LENGTH = 8
CONTROL_LENGTH = 8
MESSAGE_LENGTH = 256 - HEADER_LENGTH - CONTROL_LENGTH
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 1234
CLIENT_ID = "1"
ALIVE_INTERVAL = 10  # seconds
def handle_normal_message(msg:str):
    recipient = msg[1:msg.index(']')][:CONTROL_LENGTH].ljust(CONTROL_LENGTH)
    message = msg[msg.index(']')+1:][:MESSAGE_LENGTH].ljust(MESSAGE_LENGTH).strip()
    msg = f"g{recipient}{CLIENT_ID}{message}".encode("utf-8")[:256].ljust(256)
    print(msg)


handle_normal_message("[1,2,3,4,5]")