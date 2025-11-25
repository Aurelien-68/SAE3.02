import socket
import threading
import json
import traceback

BUF = 4096
ENC = "utf-8"

def log(*args):
    print("[ROUTEUR]", *args)

class Router:
    def __init__(self, host='0.0.0.0', port=10000):
        self.host = host
        self.port = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(20)

        log(f"Routeur lancé sur {host}:{port}")

    def serve_forever(self):
        while True:
            conn, addr = self.server.accept()
            log(f"Connexion entrante : {addr}")
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        try:
            while True:
                raw = conn.recv(BUF)
                if not raw:
                    break  # Le client a fermé la connexion

                msg = json.loads(raw.decode(ENC))
                path = msg.get("path", [])
                data = msg.get("data", "")

                if not path:
                    log(f"Aucun chemin à suivre pour le message de {addr}")
                    continue  # Connexion reste ouverte

                next_hop = path.pop(0)
                next_host, next_port = next_hop[0], int(next_hop[1])

                if len(path) == 0:
                    log(f"Livraison finale vers {next_host}:{next_port}")
                    self.send_to_dest(next_host, next_port, data.encode(ENC))
                else:
                    forward_msg = {"path": path, "data": data}
                    raw_fwd = json.dumps(forward_msg).encode(ENC)
                    log(f"Forward vers {next_host}:{next_port} (sauts restants : {len(path)})")
                    self.send_to_dest(next_host, next_port, raw_fwd)

        except Exception:
            print(traceback.format_exc())
        finally:
            conn.close()
            log(f"Fermeture connexion {addr}")

    def send_to_dest(self, host, port, raw):
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                s.sendall(raw)
        except Exception as e:
            log(f"Erreur vers {host}:{port} -> {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10000)
    args = parser.parse_args()

    r = Router(args.host, args.port)
    r.serve_forever()
