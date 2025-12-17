import socket
import threading
import time
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QListWidget
)
from PyQt5.QtCore import pyqtSignal, QObject

ENC = "utf-8"
BUF = 4096



def parse_master_port():
    """
    Lecture des arguments :
        -p PORT
        --port PORT

    Exemple :
        python master.py -p 10000
    """
    port = 9000 

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("-p", "--port") and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                port = 9000
            i += 2
        else:
            i += 1

    return port



class LogEmitter(QObject):
    log = pyqtSignal(str)
    update_list = pyqtSignal(list)



class MasterServerThread(threading.Thread):
    def __init__(self, emitter, host="0.0.0.0", port=9000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.emitter = emitter

        self.running = False
        self.server_socket = None

        self.routers = {}  

    def run(self):
        self.running = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(50)
        except Exception as e:
            self.emitter.log.emit("[MASTER] ERREUR : Impossible de bind sur %s:%d" %
                                  (self.host, self.port))
            self.running = False
            return

        self.emitter.log.emit("[MASTER] Démarré sur %s:%d" % (self.host, self.port))

        cleaner = threading.Thread(target=self.cleaner_loop, daemon=True)
        cleaner.start()

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client, args=(conn, addr), daemon=True
                ).start()
            except:
                break

        self.emitter.log.emit("[MASTER] Serveur arrêté.")

    def cleaner_loop(self):
        while self.running:
            time.sleep(2)
            now = time.time()

            removed = []
            for name, r in list(self.routers.items()):
                if now - r["last_seen"] > 5:
                    removed.append(name)
                    del self.routers[name]

            if removed:
                self.emitter.log.emit("[MASTER] Routeurs inactifs retirés : " +
                                       ", ".join(removed))
                self.update_clients_list()

    def update_clients_list(self):
        lst = []
        for name, r in self.routers.items():
            lst.append("%s (%s:%d)" % (name, r["ip"], r["port"]))
        self.emitter.update_list.emit(lst)

    def handle_client(self, conn, addr):
        try:
            line = conn.recv(BUF).decode(ENC).strip()
            if not line:
                return

            if line.startswith("REGISTER|"):
                self.process_register(conn, line)
            elif line == "LIST":
                self.process_list(conn)

        finally:
            conn.close()

    def process_register(self, conn, line):
        parts = line.split("|")
        if len(parts) != 6:
            return

        _, name, ip, port_s, e_s, n_s = parts

        try:
            port = int(port_s)
            e = int(e_s)
            n = int(n_s)
        except ValueError:
            return

        self.routers[name] = {
            "ip": ip,
            "port": port,
            "pubkey": (e, n),
            "last_seen": time.time()
        }

        self.emitter.log.emit("[MASTER] REGISTER → %s (%s:%d)" %
                              (name, ip, port))

        conn.sendall(b"OK\n")
        self.update_clients_list()

    def process_list(self, conn):
        if not self.routers:
            conn.sendall(b"ROUTERS|\n")
            self.emitter.log.emit("[MASTER] LIST → aucun routeur")
            return

        entries = []
        for name, r in self.routers.items():
            e, n = r["pubkey"]
            txt = "%s,%s,%d,%d,%d" % (name, r["ip"], r["port"], e, n)
            entries.append(txt)

        msg = "ROUTERS|" + ";".join(entries) + "\n"
        conn.sendall(msg.encode(ENC))

        self.emitter.log.emit("[MASTER] LIST → %d routeurs" %
                              len(self.routers))


class MasterGUI(QMainWindow):
    def __init__(self, port):
        super().__init__()
        self.setWindowTitle("Master Server - Onion Routing")
        self.resize(650, 550)

        self.port = port

        self.emitter = LogEmitter()
        self.emitter.log.connect(self.add_log)
        self.emitter.update_list.connect(self.update_router_list)

        self.server_thread = None

        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        self.start_button = QPushButton(f"Démarrer le Master (port {self.port})")
        self.start_button.clicked.connect(self.toggle_master)
        layout.addWidget(self.start_button)

        layout.addWidget(QLabel("Routeurs actifs :"))
        self.router_list = QListWidget()
        layout.addWidget(self.router_list)

        layout.addWidget(QLabel("Logs :"))
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

    def toggle_master(self):
        if self.server_thread and self.server_thread.running:
            self.server_thread.running = False
            self.start_button.setText(f"Démarrer le Master (port {self.port})")
        else:
            self.server_thread = MasterServerThread(self.emitter, "0.0.0.0", self.port)
            self.server_thread.start()
            self.start_button.setText("Arrêter le Master")

    def add_log(self, text):
        self.logs.append(text)

    def update_router_list(self, data):
        self.router_list.clear()
        for item in data:
            self.router_list.addItem(item)


def main():
    port = parse_master_port()

    app = QApplication([])
    gui = MasterGUI(port)
    gui.show()
    app.exec_()


if __name__ == "__main__":
    main()
