import socket
import threading
from requests import get
import sys
import json

ENCODING_FORMAT = "utf-8"
HOST = "127.0.0.1"
PORT = 9090
ALT_PORT = 9091
SERVER_TYPE = "Local Host"

print("""
Select server type:
1. Local host
2. Public host""")
server_type = input(">>> ")
if server_type == "1":
    HOST = "127.0.0.1"
    SERVER_TYPE = "Local Host"
elif server_type == "2":
    public_ip = get("https://api.ipify.org").content.decode(ENCODING_FORMAT)
    HOST = public_ip
    SERVER_TYPE = "Public Host"
else:
    print("Continuing with local host option")
    HOST = "127.0.0.1"
    SERVER_TYPE = "Local Host"

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
except:
    print(f"Port {PORT} is currently being used by another application")
    print(f"Trying alternate port {ALT_PORT}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        PORT = ALT_PORT
        s.bind((HOST, PORT))
    except:
        print(f"Port {ALT_PORT} is currently being used by another application")
        print("SERVER FAILED TO START")
        sys.exit()
s.listen(5)

clients = []
nicknames = []
with open("admins.json", "r") as f:
    admins_json = json.load(f)


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
            broadcast(f"SERVER------: {nicknames[i]} disconnected", client)
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
            broadcast(f"SERVER------: {nickname} connected", client)
            t = threading.Thread(target=handle_clients, args=[client, address])
            t.start()
        except Exception as e:
            print(f"ERROR --- {e}")
            break


print("\n")
print("SERVER START")
print(f"MODE:    {SERVER_TYPE}")
print(f"ADDRESS: {HOST}/{PORT}")

receive_clients()

print("SERVER STOP")
