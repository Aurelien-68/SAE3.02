import socket
import threading

HOST = '127.0.0.1'
PORT = 2000

client_socket = socket.socket()
client_socket.connect((HOST, PORT))
print(f"[CLIENT] Connecté à {HOST}:{PORT}")

def receive_messages():
    while True:
        try:
            reply = client_socket.recv(1024).decode()
            if not reply:
                break
            print(f"\n[SERVEUR] : {reply}")
            if reply.lower() == "arret":
                print("[CLIENT] Serveur arrêté. Fermeture du client.")
                client_socket.close()
                exit(0)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

while True:
    message = input("[CLIENT] > ")
    client_socket.send(message.encode())
    if message.lower() == "bye":
        print("[CLIENT] Déconnexion.")
        break
    elif message.lower() == "arret":
        print("[CLIENT] Fermeture du client et du serveur demandée.")
        break

client_socket.close()
