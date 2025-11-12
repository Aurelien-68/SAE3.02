import socket

HOST = '127.0.0.1'   # adresse du serveur (ou celle de ton voisin)
PORT = 2000

client_socket = socket.socket()
client_socket.connect((HOST, PORT))
print(f"[CLIENT] Connecté à {HOST}:{PORT}")

while True:
    message = input("[CLIENT] > ")
    client_socket.send(message.encode())

    if message == "bye" or message== "arret":
        print("[CLIENT] Déconnexion.")
        break

    reply = client_socket.recv(1024).decode()
    print(f"[SERVEUR] : {reply}")

client_socket.close()
