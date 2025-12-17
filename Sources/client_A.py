import socket
import json
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from rsa_utils import rsa_encrypt_bytes, encode_cipher

ENC = "utf-8"
MASTER_IP = "127.0.0.1"
MASTER_PORT = 9000

MY_IP = "127.0.0.1"
MY_PORT = 14000      # port de réception de A

TARGET_IP = "127.0.0.1"
TARGET_PORT = 15000  # port de B


# =============== Utilitaires réseau / onion ===================

def ask_route(hops: int):
    with socket.create_connection((MASTER_IP, MASTER_PORT)) as s:
        req = {"type": "get_route", "hops": hops}
        s.sendall(json.dumps(req).encode(ENC))
        resp = json.loads(s.recv(8192).decode(ENC))
        if resp.get("type") != "route":
            raise RuntimeError(f"Erreur master : {resp}")
        return resp["path"]


def build_onion(path, message, final_ip, final_port):
    layer = {"final_ip": final_ip, "final_port": final_port, "message": message}
    for r in reversed(path):
        pubkey = tuple(r["pubkey"])
        layer_bytes = json.dumps(layer).encode(ENC)
        cipher_list = rsa_encrypt_bytes(layer_bytes, pubkey)
        cipher_str = encode_cipher(cipher_list)
        layer = {
            "next_ip": r["ip"],
            "next_port": r["port"],
            "payload": cipher_str,
        }
    return layer

# =============== Objet pour remonter les logs =================

class LogEmitter(QObject):
    log = pyqtSignal(str)


# =============== Fenêtre principale Client A ==================

class ClientAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client A - Onion Routing")
        self.resize(700, 500)

        self.emitter = LogEmitter()
        self.emitter.log.connect(self.append_log)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Ligne message + nb de sauts + bouton
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Message pour B :"))
        self.msg_edit = QLineEdit()
        hl.addWidget(self.msg_edit)

        hl.addWidget(QLabel("Sauts :"))
        self.hops_spin = QSpinBox()
        self.hops_spin.setRange(1, 5)
        self.hops_spin.setValue(2)
        hl.addWidget(self.hops_spin)

        self.send_btn = QPushButton("Envoyer à B")
        self.send_btn.clicked.connect(self.send_message)
        hl.addWidget(self.send_btn)

        layout.addLayout(hl)

        # Zone de logs
        layout.addWidget(QLabel("Logs :"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        # Thread d'écoute
        t = threading.Thread(target=self.listen_loop, daemon=True)
        t.start()
        self.log("Client A démarré, écoute sur %s:%d" % (MY_IP, MY_PORT))

    # ---------- Logs ----------
    def log(self, text: str):
        self.emitter.log.emit(text)

    def append_log(self, text: str):
        self.log_view.append(text)

    # ---------- Réception ----------
    def listen_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((MY_IP, MY_PORT))
        s.listen(5)
        self.log(f"[RECV] En écoute sur {MY_IP}:{MY_PORT}")
        while True:
            conn, addr = s.accept()
            data = conn.recv(4096)
            if data:
                msg = data.decode(ENC)
                self.log(f"[RECV] Message de {addr} : {msg}")
            conn.close()

    # ---------- Envoi ----------
    def send_message(self):
        msg = self.msg_edit.text().strip()
        if not msg:
            self.log("[WARN] Message vide, rien envoyé.")
            return

        hops = self.hops_spin.value()
        try:
            path = ask_route(hops)
        except Exception as e:
            self.log(f"[ERR] Erreur route master : {e}")
            return

        route_str = " -> ".join(f"{r['name']}({r['ip']}:{r['port']})" for r in path)
        self.log(f"[INFO] Route A → B ({hops} sauts) : {route_str}")

        onion = build_onion(path, msg, TARGET_IP, TARGET_PORT)

        first = path[0]
        try:
            with socket.create_connection((first["ip"], first["port"])) as s:
                s.sendall(json.dumps(onion).encode(ENC))
            self.log("[SEND] Oignon envoyé à B via " +
                     f"{first['name']}({first['ip']}:{first['port']})")
        except Exception as e:
            self.log(f"[ERR] Impossible d'envoyer : {e}")


def main():
    app = QApplication([])
    w = ClientAWindow()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
