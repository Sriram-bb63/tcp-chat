import socket
import threading

HOST = "127.0.0.1"
PORT = 9090

global client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nope_nicknames = ["server"]

global nickname
while True:
	nickname = input("Enter nickname: ")
	if nickname.lower() not in nope_nicknames:
		break
	else:
		print("CLIENT: Nickname not allowed")

def send_message():
	while True:
		message = input("")
		message = f"{nickname}: {message}"
		client.send(message.encode("utf-8"))

def receive_message():
	while True:
		message = client.recv(1024).decode("utf-8")
		if message == "NICKNAME":
			client.send(nickname.encode("utf-8"))
		else:
			print(message)


send_thread = threading.Thread(target=send_message)
send_thread.start()

receive_thread = threading.Thread(target=receive_message)
receive_thread.start()