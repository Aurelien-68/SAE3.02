
import socket
import threading

from rsa_utils import rsa_decrypt_bytes, cipher_from_str
from onion_format import parse_layer

BUF = 4096
ENC = "utf-8"

RESET = "\033[0m"
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"


class RouterOnion:
    def __init__(self, host, port, private_key, name="RX"):
        self.host = host
        self.port = port
        self.private_key = private_key
        self.name = name

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(20)

        print(BLUE + "[%s] Routeur lancé sur %s:%d" %
              (self.name, host, port) + RESET)

    def serve_forever(self):
        while True:
            conn, addr = self.server.accept()
            print(CYAN + "[%s] Connexion entrante %s" % (self.name, addr) + RESET)
            t = threading.Thread(target=self.handle_client, args=(conn, addr))
            t.daemon = True
            t.start()

    def handle_client(self, conn, addr):
        try:
            raw = b""
            while True:
                chunk = conn.recv(BUF)
                if not chunk:
                    break
                raw += chunk

            if not raw:
                return

            msg = raw.decode(ENC)
            print(BLUE + "[%s] Layer externe : %s" %
                  (self.name, msg[:120]) + RESET)

            # couche externe N|next_ip|next_port|cipher_str
            type_flag, _ip, _port, cipher_str = parse_layer(msg)
            if type_flag != "N":
                print(RED + "[%s] Type externe inattendu : %s" %
                      (self.name, type_flag) + RESET)
                return

            cipher_list = cipher_from_str(cipher_str)
            inner_bytes = rsa_decrypt_bytes(cipher_list, self.private_key)
            inner = inner_bytes.decode(ENC)

            print(MAGENTA + "[%s] Inner déchiffré : %s" %
                  (self.name, inner[:120]) + RESET)

            t2, ip2, port2, rest = parse_layer(inner)

            if t2 == "F":
                # couche finale
                message = rest
                print(YELLOW + "[%s] Livraison finale vers %s:%d" %
                      (self.name, ip2, port2) + RESET)
                self._send_raw(ip2, port2, message.encode(ENC))
            elif t2 == "N":
                print(CYAN + "[%s] Forward vers %s:%d" %
                      (self.name, ip2, port2) + RESET)
                self._send_raw(ip2, port2, inner.encode(ENC))
            else:
                print(RED + "[%s] Type interne inconnu : %s" %
                      (self.name, t2) + RESET)

        finally:
            conn.close()

    def _send_raw(self, host, port, raw):
        try:
            with socket.create_connection((host, port), timeout=5) as s:
                s.sendall(raw)
        except Exception as e:
            print(RED + "[%s] Erreur envoi vers %s:%d -> %s" %
                  (self.name, host, port, e) + RESET)
