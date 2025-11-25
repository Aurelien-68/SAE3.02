import socket
import threading
import json

BUF = 4096
ENC = 'utf-8'

# Thread pour écouter les messages entrants
def listen(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    s.listen(5)
    print(f"[CLIENT] En écoute sur 127.0.0.1:{port}")
    while True:
        conn, addr = s.accept()
        data = conn.recv(BUF).decode(ENC)
        if data:
            print(f"\n[RECU] {data}")
        conn.close()

def main():
    host = input("IP du premier routeur : ").strip()
    port_routeur = int(input("Port du premier routeur : ").strip())
    port_ecoute = int(input("Port où ce client va écouter : ").strip())

    # Lancer le thread d'écoute
    threading.Thread(target=listen, args=(port_ecoute,), daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port_routeur))
    print(f"[CLIENT] Connecté au routeur {host}:{port_routeur}")

    while True:
        msg = input("> ").strip()
        if not msg:
            continue
        path_str = input("Chemin (host:port,host:port,...): ").strip()
        path = []
        if path_str:
            for hop in path_str.split(","):
                hop = hop.strip()
                if hop:
                    try:
                        h, p = hop.split(":")
                        path.append([h.strip(), int(p.strip())])
                    except ValueError:
                        print(f"Format invalide pour le saut: '{hop}', utiliser host:port")
                        continue
        paquet = {"path": path, "data": msg}
        sock.sendall(json.dumps(paquet).encode(ENC))

if __name__ == '__main__':
    main()

