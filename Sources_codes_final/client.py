import socket
import threading
import random
import sys
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QSpinBox, QCheckBox, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, QObject

from rsa_utils import rsa_encrypt_bytes, cipher_to_str
from onion_format import make_final_layer, make_route_layer

ENC = "utf-8"


def parse_args():
    """
    Utilisation attendue :
        python client.py -n IP_MASTER:PORT_MASTER -p PORT_CLIENT

    Exemple :
        python client.py -n 192.168.1.10:12000 -p 14100
    """
    master_ip = None
    master_port = None
    local_port = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "-n" and i + 1 < len(args):
            value = args[i + 1]
            if ":" in value:
                host, port_s = value.split(":", 1)
                master_ip = host
                try:
                    master_port = int(port_s)
                except ValueError:
                    master_port = None
            i += 2
        elif args[i] == "-p" and i + 1 < len(args):
            try:
                local_port = int(args[i + 1])
            except ValueError:
                local_port = None
            i += 2
        else:
            i += 1

    # Vérification de la validité des paramètres
    if master_ip is None or master_port is None or local_port is None:
        print("Usage : python client.py -n IP_MASTER:PORT_MASTER -p PORT_CLIENT")
        sys.exit(1)

    # Correction si le master est sur la machine locale
    if master_ip == "0.0.0.0":
        print("IP master 0.0.0.0 reçue → utilisation de 127.0.0.1 pour la connexion.")
        master_ip = "127.0.0.1"

    return master_ip, master_port, local_port

# Récupération de la liste des routeurs depuis le master
def get_router_list(master_ip, master_port):
    """
    Retourne une liste de dicts {name, ip, port, pubkey:(e,n)}
    via protocole :
        client -> "LIST\n"
        master -> "ROUTERS|name,ip,port,e,n;...\n"
    """
    with socket.create_connection((master_ip, master_port)) as s:
        s.sendall(b"LIST\n")
        resp = s.recv(8192).decode(ENC, errors="replace").strip()

    if not resp.startswith("ROUTERS|"):
        raise RuntimeError("Réponse master invalide : " + resp)

    payload = resp[len("ROUTERS|"):]
    if not payload:
        return []

    routers = []
    entries = payload.split(";")
    for entry in entries:
        if not entry:
            continue
        parts = entry.split(",")
        if len(parts) != 5:
            continue
        name, ip, port_s, e_s, n_s = parts
        try:
            port = int(port_s)
            e = int(e_s)
            n = int(n_s)
        except ValueError:
            continue

        routers.append({
            "name": name,
            "ip": ip,
            "port": port,
            "pubkey": (e, n),
        })
    return routers

# Construction du message en routage "oignon"
def build_onion_for_message(message, dest_ip, dest_port, routers_selected, hops):
    """
    Choisit au hasard 'hops' routeurs dans routers_selected,
    construit l'oignon et retourne (first_ip, first_port, onion_bytes, path)
    """
    if hops > len(routers_selected):
        raise ValueError("Pas assez de routeurs cochés pour ce nombre de sauts")

    # Sélection aléatoire du chemin
    path = random.sample(routers_selected, hops)

    # Couche finale : message + destination
    inner = make_final_layer(dest_ip, dest_port, message)

    # Construction des couches successives (en partant du dernier routeur)
    for r in reversed(path):
        # Chiffrement RSA avec la clé publique du routeur
        cipher_list = rsa_encrypt_bytes(inner.encode(ENC), r["pubkey"])
        cipher_str = cipher_to_str(cipher_list)
        # Création de la couche contenant l'adresse du prochain saut
        inner = make_route_layer(r["ip"], r["port"], cipher_str)

    first = path[0]
    return first["ip"], first["port"], inner.encode(ENC), path

# Enregistrement du client auprès du master
def register_client_to_master(master_ip, master_port, client_name, client_ip, client_port):
    """
    Envoie au master : CLIENT|name|ip|port
    """
    msg = f"CLIENT|{client_name}|{client_ip}|{client_port}\n".encode(ENC)
    with socket.create_connection((master_ip, master_port), timeout=5) as s:
        s.sendall(msg)
        try:
            _ = s.recv(64)
        except Exception:
            pass


class LogEmitter(QObject):
    log = pyqtSignal(str)


class ClientWindow(QMainWindow):
    def __init__(self, master_ip, master_port, local_port):
        super().__init__()
        self.setWindowTitle("Client Onion Routing")
        self.resize(850, 650)

        self.listen_ip = "0.0.0.0"
        self.listen_port = local_port

        self.master_ip_init = master_ip
        self.master_port_init = master_port

        self.client_name = f"C{self.listen_port}"

        self.client_ip_for_master = "127.0.0.1"

        self.router_checkboxes = []
        self.routers_data = []

        self.emitter = LogEmitter()
        self.emitter.log.connect(self.append_log)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        info_layout = QHBoxLayout()
        self.listen_label = QLabel(
            "Écoute locale : %s:%d | Nom client : %s (port -> relancer avec -p)"
            % (self.listen_ip, self.listen_port, self.client_name)
        )
        info_layout.addWidget(self.listen_label)
        main_layout.addLayout(info_layout)

        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("IP du serveur master :"))
        self.master_ip_edit = QLineEdit(self.master_ip_init)
        master_layout.addWidget(self.master_ip_edit)

        master_layout.addWidget(QLabel("Port master :"))
        self.master_port_spin = QSpinBox()
        self.master_port_spin.setRange(1, 65535)
        self.master_port_spin.setValue(self.master_port_init)
        master_layout.addWidget(self.master_port_spin)

        self.refresh_btn = QPushButton("Rafraîchir les routeurs")
        self.refresh_btn.clicked.connect(self.refresh_routers)
        master_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(master_layout)

        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("IP du client distant :"))
        self.remote_ip_edit = QLineEdit("127.0.0.1")
        dest_layout.addWidget(self.remote_ip_edit)

        dest_layout.addWidget(QLabel("Port du client distant :"))
        self.remote_port_spin = QSpinBox()
        self.remote_port_spin.setRange(1, 65535)
        self.remote_port_spin.setValue(15000)
        dest_layout.addWidget(self.remote_port_spin)

        main_layout.addLayout(dest_layout)

        main_layout.addWidget(QLabel("Routeurs disponibles :"))
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.router_list_widget = QWidget()
        self.router_list_layout = QVBoxLayout(self.router_list_widget)
        self.scroll.setWidget(self.router_list_widget)
        main_layout.addWidget(self.scroll)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Message à envoyer :"))
        self.msg_edit = QLineEdit()
        hl.addWidget(self.msg_edit)

        hl.addWidget(QLabel("Sauts :"))
        self.hops_spin = QSpinBox()
        self.hops_spin.setRange(1, 10)
        self.hops_spin.setValue(2)
        hl.addWidget(self.hops_spin)

        self.send_btn = QPushButton("Envoyer")
        self.send_btn.clicked.connect(self.send_message)
        hl.addWidget(self.send_btn)

        main_layout.addLayout(hl)

        main_layout.addWidget(QLabel("Logs :"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        main_layout.addWidget(self.log_view)

        t = threading.Thread(target=self.listen_loop, daemon=True)
        t.start()
        self.log("[INFO] Client en écoute sur %s:%d" % (self.listen_ip, self.listen_port))

        threading.Thread(target=self.register_once, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def log(self, text):
        self.emitter.log.emit(text)

    def append_log(self, text):
        self.log_view.append(text)

    def listen_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.listen_ip, self.listen_port))
        s.listen(5)
        self.log("[RECV] Socket ouvert sur %s:%d" % (self.listen_ip, self.listen_port))
        while True:
            conn, addr = s.accept()
            data = conn.recv(4096)
            if data:
                msg = data.decode(ENC, errors="replace")
                self.log("[RECV] Message de %s : %s" % (addr, msg))
            conn.close()

    def register_once(self):
        master_ip = self.master_ip_edit.text().strip()
        master_port = self.master_port_spin.value()
        try:
            register_client_to_master(
                master_ip, master_port,
                self.client_name,
                self.client_ip_for_master,
                self.listen_port
            )
            self.log("[INFO] Enregistrement client envoyé au master : %s" % self.client_name)
        except Exception as e:
            self.log("[ERR] Enregistrement client impossible : %s" % e)

    def heartbeat_loop(self):
        while True:
            time.sleep(5)
            master_ip = self.master_ip_edit.text().strip()
            master_port = self.master_port_spin.value()
            if not master_ip:
                continue
            try:
                register_client_to_master(
                    master_ip, master_port,
                    self.client_name,
                    self.client_ip_for_master,
                    self.listen_port
                )
            except Exception:
                pass

    def refresh_routers(self):
        master_ip = self.master_ip_edit.text().strip()
        master_port = self.master_port_spin.value()

        if not master_ip:
            self.log("[ERR] IP du master vide.")
            return

        try:
            routers = get_router_list(master_ip, master_port)
        except Exception as e:
            self.log("[ERR] Impossible de récupérer les routeurs : %s" % e)
            return

        self.routers_data = routers
        self.router_checkboxes = []

        while self.router_list_layout.count():
            item = self.router_list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if not routers:
            self.log("[INFO] Aucun routeur enregistré auprès du master.")
            return

        for r in routers:
            txt = "%s (%s:%d)" % (r["name"], r["ip"], r["port"])
            cb = QCheckBox(txt)
            cb.setChecked(True)
            self.router_list_layout.addWidget(cb)
            self.router_checkboxes.append((cb, r))

        self.log("[INFO] %d routeurs chargés depuis %s:%d." %
                 (len(routers), master_ip, master_port))

    def send_message(self):
        msg = self.msg_edit.text().strip()
        if not msg:
            self.log("[WARN] Message vide, rien envoyé.")
            return

        selected = []
        for cb, r in self.router_checkboxes:
            if cb.isChecked():
                selected.append(r)

        if not selected:
            self.log("[ERR] Aucun routeur sélectionné.")
            return

        hops = self.hops_spin.value()

        dest_ip = self.remote_ip_edit.text().strip()
        dest_port = self.remote_port_spin.value()

        if not dest_ip:
            self.log("[ERR] IP du client distant vide.")
            return

        try:
            first_ip, first_port, onion_bytes, path = build_onion_for_message(
                msg, dest_ip, dest_port, selected, hops
            )
        except Exception as e:
            self.log("[ERR] Erreur de construction de l'oignon : %s" % e)
            return

        route_str = " -> ".join(
            "%s(%s:%d)" % (r["name"], r["ip"], r["port"]) for r in path
        )
        self.log("[INFO] Route choisie : " + route_str)

        try:
            with socket.create_connection((first_ip, first_port)) as s:
                s.sendall(onion_bytes)
            self.log("[SEND] Oignon envoyé via %s:%d" % (first_ip, first_port))
        except Exception as e:
            self.log("[ERR] Envoi impossible : %s" % e)

def main():
    master_ip, master_port, local_port = parse_args()
    app = QApplication(sys.argv)
    w = ClientWindow(master_ip, master_port, local_port)
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()