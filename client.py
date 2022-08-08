import socket
import threading
import sys


def send_message():
	while True:
		message = input("")
		if message == "ADMIN LOGIN":
			username = input("Username: ")
			password = input("Password: ")
			message = f"ADMIN {username} {password}"
		else:
			message = f"{nickname}: {message}"
		client.send(message.encode("utf-8"))

def receive_message():
	while True:
		message = client.recv(1024).decode("utf-8")
		global nickname
		if message == "NICKNAME":
			client.send(f"{nickname}".encode("utf-8"))
		elif message == "ADMIN OK":
			nickname = f"(A) {nickname}"
			print("You are now an admin")
		elif message == "ADMIN NOT OK":
			print("Admin login failed")
		else:
			print(message)

def run_threads():
	print("run threads")
	send_thread = threading.Thread(target=send_message)
	send_thread.start()
	receive_thread = threading.Thread(target=receive_message)
	receive_thread.start()


HOST = "127.0.0.1"
PORT = 9090
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nope_nicknames = ["server", "admin"]
nickname = input("Enter nickname: ")
if nickname.lower() not in nope_nicknames:
	run_threads()
else:
	print("CLIENT: Nickname not allowed")
	sys.exit()