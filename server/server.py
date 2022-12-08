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
SERVER_MESSAGE_PREFIX = "SERVER------:"

print("""
Select server type:
1. Local host
2. Public host""")
server_type = input(">>> ")
if server_type == "1":
    HOST = "127.0.0.1"
    SERVER_TYPE = "Local Host"
elif server_type == "2":
    public_ip = socket.gethostbyname(socket.gethostname())
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

clients = {}
admins = []
with open("server/admins.json", "r") as f:
    admins_json = json.load(f)


def admin_login(nickname, client, message):
    print(f"ADMIN LOGIN ATTEMPT {nickname}")
    password = message.split()[-1]
    if nickname in admins_json and admins_json[nickname] == password:
        admins.append(nickname)
        client.send(f"{SERVER_MESSAGE_PREFIX} ADMIN LOGIN SUCCESS".encode(ENCODING_FORMAT))
        print(f"ADMIN LOGIN SUCCESS {nickname}")
        broadcast(f"{SERVER_MESSAGE_PREFIX} {nickname} is now an admin", client)
    else:
        client.send(f"{SERVER_MESSAGE_PREFIX} WRONG CREDENTIALS! ADMIN LOGIN FAILED".encode(ENCODING_FORMAT))
        print(f"ADMIN LOGIN FAIL {nickname}")

def kick_client(nickname, client, message):
    if nickname in admins:
        to_kick = message.split()[-1]
        if to_kick not in clients:
            client.send(f"{SERVER_MESSAGE_PREFIX} Cannot find {to_kick} in this server".encode(ENCODING_FORMAT))
        else:
            print(f"KICK OUT {to_kick} | {clients[to_kick].getpeername()} by {nickname}")
            broadcast(f"{SERVER_MESSAGE_PREFIX} {to_kick} has been kicked out by {nickname}", client)
            to_kick_client = clients[to_kick]
            to_kick_client.send(f"{SERVER_MESSAGE_PREFIX} You have been kicked out by {nickname}".encode(ENCODING_FORMAT))
            to_kick_client.send("END".encode(ENCODING_FORMAT))
            del clients[to_kick]
            print(clients)
    else:
        client.send(f"{SERVER_MESSAGE_PREFIX} You have to be an admin to use this command".encode(ENCODING_FORMAT))


def broadcast(message, sender, encode=True):
    for client in clients:
        if clients[client] != sender:
            if encode:
                clients[client].send(message.encode(ENCODING_FORMAT))
            else:
                clients[client].sendall(message)

def handle_clients(nickname, client, address):
    while True:
        try:
            message = client.recv(1024)
            if message[:7] == b"<START>":
                print(f"Receiving file from {nickname}")
                data_buffer = message
                while data_buffer[-5:] != b"<END>":
                    data = client.recv(1024)
                    data_buffer += data
                print(f"Broadcasting file from {nickname}")
                broadcast(data_buffer, client, encode=False)
            else:     
                message = message.decode()
                if "ADMIN LOGIN" in message:
                    admin_login(nickname, client, message)
                elif "KICK" in message:
                    kick_client(nickname, client, message)
                else:
                    broadcast(message, client)
        except Exception as e:
            del clients[nickname]
            broadcast(f"{SERVER_MESSAGE_PREFIX} {nickname} disconnected", client)
            print(f"DISCONNECT {nickname} | {address}")
            print(e.__class__, e)
            break

def receive_clients():
    while True:
        try:
            client, address = s.accept()
            print(f"NEW CONNECTION {address}")
            client.send("NICKNAME".encode(ENCODING_FORMAT))
            nickname = client.recv(1024).decode(ENCODING_FORMAT)
            clients[nickname] = client
            print(f"CONNECTION NAMED: {address} | {nickname}")
            broadcast(f"{SERVER_MESSAGE_PREFIX} {nickname} connected", client)
            t = threading.Thread(target=handle_clients, args=[nickname, client, address])
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
