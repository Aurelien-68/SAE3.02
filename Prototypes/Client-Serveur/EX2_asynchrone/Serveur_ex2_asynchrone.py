import socket
import threading

HOST = '0.0.0.0'
PORT = 2000


def receive_messages(conn):
    while True:
        try:
            message = conn.recv(1024).decode()
            if not message:
                break
            print(f"[CLIENT {addr}] : {message}")

            if message.lower() == "bye":
                print(f"[SERVEUR] Client {addr} déconnecté.")
                break
            elif message.lower() == "arret":
                print("[SERVEUR] Arrêt du serveur demandé.")
                conn.send("Serveur arrêté.".encode())
                conn.close()
                server_socket.close()
                exit(0)
        except:
            break
def handle_client(conn, addr):
    print(f"[SERVEUR] Connexion depuis {addr}")
    threading.Thread(target=receive_messages,args=(conn,), daemon=True).start()

    while True:
        reply = input(f"[SERVEUR {addr}] > ")
        if reply:
            conn.send(reply.encode())
            if reply.lower() == "bye":
                print(f"[SERVEUR] Fermeture de la connexion avec {addr}")
                conn.close()
                break
            elif reply.lower() == "arret":
                print("[SERVEUR] Arrêt du serveur demandé.")
                conn.close()
                server_socket.close()
                exit(0)
    conn.close()

server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"[SERVEUR] En écoute sur le port {PORT}")

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
