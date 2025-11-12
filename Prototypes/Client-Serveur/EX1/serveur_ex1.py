import socket

host ='127.0.0.1'
port = 2000 #au dessus de 1000

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', port))
server_socket.listen(1)
print(f"[SERVEUR] En écoute sur {host}:{port}")

conn, address = server_socket.accept()
print(f"[SERVEUR] Connexion depuis {address}")

message = conn.recv(1024).decode()
print(f"[SERVEUR] Message reçu : {message}")

reply = "Message bien reçu par le serveur."
conn.send(reply.encode())

conn.close()
server_socket.close()
