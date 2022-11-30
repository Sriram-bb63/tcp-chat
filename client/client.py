import socket
import threading
from datetime import datetime

ENCODING_FORMAT = "utf-8"
HOST = "127.0.0.1"
PORT = 9090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def send_message():
    while True:
        message = input("")
        time = datetime.now().strftime("%H:%M:%S")
        message = f"{time}  " + f"{nickname}: " + message
        client.send(message.encode(ENCODING_FORMAT))
        # print(f"MESSAGE SENT to {client}")

def receive_message():
    while True:
        message = client.recv(1024).decode(ENCODING_FORMAT)
        if message == "NICKNAME":
            client.send(f"{nickname}".encode(ENCODING_FORMAT))
        else:
            print(message)

def run_threads():
    send_thread = threading.Thread(target=send_message)
    send_thread.start()
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()


nickname = input("Enter nickname: ")
run_threads()
