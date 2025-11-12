import socket

host = '127.0.0.1'
port = 2000 #au dessus de 1000

client_socket = socket.socket()
client_socket.connect((host, port))

message = input("[CLIENT] Message à envoyer : ")
client_socket.send(message.encode())

reply = client_socket.recv(1024).decode()
print(f"[CLIENT] Réponse du serveur : {reply}")

client_socket.close()
