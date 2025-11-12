import socket

host = '127.0.0.1'
port = 5001

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', port))
server_socket.listen(1)
print(f"[SERVEUR] En écoute sur {host}:{port}")

conn, address = server_socket.accept()
print(f"[SERVEUR] Connexion depuis {address}")

while True:
    message = conn.recv(1024).decode()
    if not message:
        break

    print(f"[CLIENT] : {message}")

    # Gestion des commandes
    if message.lower() == "bye":
        print("[SERVEUR] Client déconnecté.")

    elif message.lower() == "arret":
        print("[SERVEUR] Arrêt du serveur.")
        conn.send("Serveur arrêté.".encode())
        conn.close()
        server_socket.close()
        exit(0)

    reply = input("[SERVEUR] > ")
    conn.send(reply.encode())

conn.close()
server_socket.close()
