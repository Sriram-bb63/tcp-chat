import socket
import threading

ENCODING_FORMAT = "utf-8"
HOST = "127.0.0.1"
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

clients = []
nicknames = []

def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message.encode(ENCODING_FORMAT))

def handle_clients(client, address):
    while True:
        try:
            message = client.recv(1024).decode(ENCODING_FORMAT)
            print(message)
            broadcast(message, client)
        except Exception as e:
            i = clients.index(client)
            broadcast(f"SERVER: {nicknames[i]} disconnected", client)
            print(f"DISCONNECT {nicknames[i]} | {address}")
            clients.pop(i)
            nicknames.pop(i)
            print(f"ERROR\n{e}")
            break

def receive_clients():
    while True:
        try:
            client, address = s.accept()
            print(f"NEW CONNECTION {address}")
            client.send("NICKNAME".encode(ENCODING_FORMAT))
            nickname = client.recv(1024).decode(ENCODING_FORMAT)
            clients.append(client)
            nicknames.append(nickname)
            print(f"CONNECTION NAMED: {address} | {nickname}")
            broadcast(f"SERVER: {nickname} connected", client)
            t = threading.Thread(target=handle_clients, args=[client, address])
            t.start()
        except Exception as e:
            print(f"ERROR --- {e}")
            break


print("SERVER START")

receive_clients()

print("SERVER STOP")
