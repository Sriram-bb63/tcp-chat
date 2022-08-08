import socket
import threading
import json


HOST = "127.0.0.1"
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

clients = []
nicknames = []

with open("admins.json", "r") as f:
    admins = json.load(f)
active_admins = []

def broadcast(message, sender_client):
    for client in clients:
        if client != sender_client:
            client.send(message.encode("utf-8"))


def handle_clients(client, address):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message.split()[0] == "ADMIN":
                username = message.split()[1]
                password = message.split()[2]
                if username in admins and admins[username] == password:
                    active_admins.append(client)
                    i = clients.index(client)
                    message = f"SERVER: {nicknames[i]} is now an admin"
                    print(f"NEW ADMIN --- {address} | {nicknames[i]}")
                    client.send("ADMIN OK".encode("utf-8"))
                else:
                    client.send("ADMIN NOT OK".encode("utf-8"))
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