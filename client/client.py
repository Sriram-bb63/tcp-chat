import socket
import threading
from datetime import datetime
import sys

ENCODING_FORMAT = "utf-8"
HOST = "127.0.0.1"
PORT = 9090
FILE_DESTINATION = "client/files"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def send_message():
    while True:
        message = input("")
        if message.startswith("SEND FILE"):
            path = message.split()[-1]
            filename = path.split("/")[-1]
            client.send(f"FILE NAME {filename}".encode(ENCODING_FORMAT))
            print("Filename sent successfully")
            with open(path, "rb") as f:
                data = f.read()
            data = b"<START>" + data + b"<END>"
            client.sendall(data)
            print("File sent successfully")
        else:
            time = datetime.now().strftime("%H:%M:%S")
            message = f"{time}  " + f"{nickname}: " + message
            client.send(message.encode(ENCODING_FORMAT))

def receive_message():
    filenames = []
    while True:
        message = client.recv(1024)
        if message[:7] == b"<START>":
            print(f"Receiving file: {filenames[0]}")
            data_buffer = message
            while data_buffer[-5:] != b"<END>":
                data = client.recv(1024)
                data_buffer += data
            data_buffer = data_buffer[7:-5]
            with open(f"{FILE_DESTINATION}/{filenames[0]}", "wb+") as f:
                f.write(data_buffer)
            print(f"File saved at {FILE_DESTINATION} as {filenames[0]}")
            filenames.clear()
        else:
            message = message.decode(ENCODING_FORMAT)
            if message == "NICKNAME":
                client.send(f"{nickname}".encode(ENCODING_FORMAT))
            elif message.startswith("FILE NAME"):
                filename = message.split()[-1]
                if len(filenames) <= 1:
                    print(f"Filename received: {filename}")
                    filenames.append(filename)
                else:
                    print("Filename stack full!")
                    filenames.clear()
                    print("Filename stack clearing...")
                    print("Try again")
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
while nickname == "" or len(nickname) >= 15:
    print("""
Nickname should not be empty
Nickname must be less than 15 characters long
""")
    nickname = input("Enter nickname again: ")

run_threads()