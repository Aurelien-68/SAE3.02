import socket

host = '127.0.0.1'
port = 5001

client_socket = socket.socket()
client_socket.connect((host, port))
print(f"[CLIENT] Connecté à {host}:{port}")

while True:
    message = input("[CLIENT] > ")
    client_socket.send(message.encode())

    if message == "bye" or message == "arret":
        print("[CLIENT] Fermeture de la connexion.")
        break

    reply = client_socket.recv(1024).decode()
    print(f"[SERVEUR] : {reply}")

client_socket.close()
