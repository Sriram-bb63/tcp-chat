import socket
import threading


HOST = "127.0.0.1"
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)


global clients
clients = []

global nicknames
nicknames = []


def broadcast(message, sender_client):
    for client in clients:
        if client != sender_client:
            client.send(message.encode("utf-8"))


def handle_clients(client, address):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            broadcast(message, client)
        except Exception as e:
            i = clients.index(client)
            # client.send("EXIT".encode("utf-8"))
            broadcast(f"SERVER: {nicknames[i]} disconnected", client)
            print(f"DISCONNECT --- {address} | {nicknames[i]}")
            clients.pop(i)
            nicknames.pop(i)
            break


def receive_clients():
    while True:
        try:
            client, address = s.accept()
            print(f"Connected with {address}")
            client.send("NICKNAME".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            clients.append(client)
            nicknames.append(nickname)
            print(f"NAME CHANGE --- {address} -> {nickname}")
            broadcast(f"SERVER: {nickname} connected", client)
            t = threading.Thread(target=handle_clients, args=[client, address])
            t.start()
        except Exception as e:
            print(f"ERROR --- {e}")
            break

print("SERVER START")

receive_clients()

print("SERVER STOP")