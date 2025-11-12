import socket

HOST = '0.0.0.0'   # écoute sur toutes les interfaces
PORT = 2000        # port du serveur

server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"[SERVEUR] En écoute sur le port {PORT}")

while True:  # permet de gérer plusieurs clients successifs
    print("[SERVEUR] En attente d’un client...")
    conn, address = server_socket.accept()
    print(f"[SERVEUR] Connexion depuis {address}")

    while True:  # communication avec le client
        message = conn.recv(1024).decode()
        if not message:
            break

        print(f"[CLIENT] : {message}")

        # Messages de protocole
        if message.lower() == "bye":
            print("[SERVEUR] Client déconnecté.")
            break
        elif message.lower() == "arret":
            print("[SERVEUR] Arrêt du serveur demandé.")
            conn.send("Serveur arrêté.".encode())
            conn.close()
            server_socket.close()
            exit(0)

        # Le serveur répond
        reply = input("[SERVEUR] > ")
        conn.send(reply.encode())

    conn.close()
    print("[SERVEUR] En attente d’un nouveau client...")
