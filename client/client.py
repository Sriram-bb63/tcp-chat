import socket
import threading
from datetime import datetime
import sys

ENCODING_FORMAT = "utf-8"
HOST = "127.0.0.1"
PORT = 9090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def send_message():
    while True:
        message = input("")
        if message.startswith("SEND FILE"):
            path = message.split()[-1]
            filename = path.split("/")[-1]
            with open(path, "r") as f:
                content = f.read()
                client.send(f"SEND FILE {filename} >>> {content}".encode(ENCODING_FORMAT))
        else:
            time = datetime.now().strftime("%H:%M:%S")
            message = f"{time}  " + f"{nickname}: " + message
            client.send(message.encode(ENCODING_FORMAT))
            # print(f"MESSAGE SENT to {client}")

def receive_message():
    while True:
        message = client.recv(1024).decode(ENCODING_FORMAT)
        if message == "NICKNAME":
            client.send(f"{nickname}".encode(ENCODING_FORMAT))
        elif message.startswith("SEND FILE"):
            filename = message.split()[2]
            content = message.split(" >>> ")[-1]
            # print(f"filename {filename}")
            # print(f"content {content}")
            path = f"client/files/{filename}"
            with open(path, "w+") as f:
                f.write(content)
                print(f"{path} has been created")
        elif message.endswith("END"):
            sys.exit()
        else:
            print(message)

def run_threads():
    send_thread = threading.Thread(target=send_message)
    send_thread.start()
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()


nickname = input("Enter nickname: ")
run_threads()