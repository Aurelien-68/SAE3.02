import sys
import socket
import threading

import mysql.connector

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QListWidget
)
from PyQt5.QtCore import pyqtSignal, QObject

ENC = "utf-8"
BUF = 8192

def parse_cli(argv):
    """
    Supporte:
      -p 12000
      --db-host 127.0.0.1
      --db-port 3306
      --db-name DBSAE302
      --db-user sae
      --db-pass sae123

    Retourne un dict config.
    """
    cfg = {
        "port": 9000,
        "db_host": "127.0.0.1",
        "db_port": 3306,
        "db_name": "DBSAE302",
        "db_user": None,
        "db_pass": None,
    }

    i = 1
    while i < len(argv):
        a = argv[i]

        def need_value(flag):
            if i + 1 >= len(argv):
                raise ValueError(f"Argument manquant après {flag}")
            return argv[i + 1]

        if a in ("-p", "--port"):
            cfg["port"] = int(need_value(a))
            i += 2
        elif a == "--db-host":
            cfg["db_host"] = need_value(a)
            i += 2
        elif a == "--db-port":
            cfg["db_port"] = int(need_value(a))
            i += 2
        elif a == "--db-name":
            cfg["db_name"] = need_value(a)
            i += 2
        elif a == "--db-user":
            cfg["db_user"] = need_value(a)
            i += 2
        elif a == "--db-pass":
            cfg["db_pass"] = need_value(a)
            i += 2
        elif a in ("-h", "--help"):
            print_usage_and_exit()
        else:
            raise ValueError(f"Argument inconnu: {a}")

    if not cfg["db_user"] or cfg["db_pass"] is None:
        raise ValueError("Tu dois fournir --db-user et --db-pass")

    return cfg

def print_usage_and_exit():
    print("Usage:")
    print("  python master.py -p 12000 --db-user sae --db-pass sae123")
    print("")
    print("Options:")
    print("  -p / --port       Port du Master (défaut: 9000)")
    print("  --db-host         Host DB (défaut: 127.0.0.1)")
    print("  --db-port         Port DB (défaut: 3306)")
    print("  --db-name         Nom DB  (défaut: DBSAE302)")
    print("  --db-user         Utilisateur DB (obligatoire)")
    print("  --db-pass         Mot de passe DB (obligatoire)")
    sys.exit(0)

def db_connect(cfg, with_db):
    params = {
        "host": cfg["db_host"],
        "port": cfg["db_port"],
        "user": cfg["db_user"],
        "password": cfg["db_pass"],
        "autocommit": True,
        "connection_timeout": 5,
    }
    if with_db:
        params["database"] = cfg["db_name"]
    return mysql.connector.connect(**params)

def db_ensure_ready(cfg):
    """
    Crée la base + la table nodes si besoin.
    NOTE: l'utilisateur DB doit avoir les droits CREATE DATABASE et CREATE TABLE.
    """
    conn = db_connect(cfg, with_db=False)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {cfg['db_name']}")
    cur.close()
    conn.close()
    
    conn = db_connect(cfg, with_db=True)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      node_type VARCHAR(16) NOT NULL,      -- 'ROUTEUR' ou 'CLIENT'
      node_name VARCHAR(64) NOT NULL,
      ip VARCHAR(64) NOT NULL,
      port INT UNSIGNED NOT NULL,
      pub_e BIGINT UNSIGNED NULL,
      pub_n BIGINT UNSIGNED NULL,
      last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

      UNIQUE KEY uk_node_identity (node_type, node_name),
      UNIQUE KEY uk_ip_port_type  (node_type, ip, port),
      KEY idx_last_seen (last_seen)
    )
    """)
    cur.close()
    conn.close()

def db_upsert_router(cfg, name, ip, port, e, n):
    conn = db_connect(cfg, with_db=True)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nodes (node_type, node_name, ip, port, pub_e, pub_n, last_seen)
        VALUES ('ROUTEUR', %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
          ip=VALUES(ip),
          port=VALUES(port),
          pub_e=VALUES(pub_e),
          pub_n=VALUES(pub_n),
          last_seen=NOW()
    """, (name, ip, port, e, n))
    cur.close()
    conn.close()

def db_upsert_client(cfg, name, ip, port):
    conn = db_connect(cfg, with_db=True)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nodes (node_type, node_name, ip, port, last_seen)
        VALUES ('CLIENT', %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
          ip=VALUES(ip),
          port=VALUES(port),
          last_seen=NOW()
    """, (name, ip, port))
    cur.close()
    conn.close()

def db_list_active_routers(cfg, seconds=30):
    conn = db_connect(cfg, with_db=True)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT node_name, ip, port, pub_e, pub_n
        FROM nodes
        WHERE node_type='ROUTEUR'
          AND last_seen > DATE_SUB(NOW(), INTERVAL {int(seconds)} SECOND)
        ORDER BY last_seen DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

class Emitter(QObject):
    log = pyqtSignal(str)
    routers_updated = pyqtSignal(list)

class MasterServer(threading.Thread):
    def __init__(self, host, port, cfg, emitter):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.cfg = cfg
        self.emitter = emitter
        self.running = True
        self.sock = None

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(50)
            self.emitter.log.emit(f"[MASTER] Écoute sur {self.host}:{self.port}")

            while self.running:
                try:
                    conn, addr = self.sock.accept()
                    threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
                except Exception:
                    break

        except Exception as e:
            self.emitter.log.emit(f"[MASTER] ERREUR serveur : {e}")
        finally:
            self.emitter.log.emit("[MASTER] Serveur arrêté.")

    def handle_client(self, conn, addr):
        try:
            raw = conn.recv(BUF)
            if not raw:
                return
            msg = raw.decode(ENC, errors="replace").strip()

            if msg.startswith("REGISTER|"):
                self.handle_register(conn, msg)
            elif msg.startswith("CLIENT|"):
                self.handle_client_hello(conn, msg)
            elif msg == "LIST":
                self.handle_list(conn)
            else:
                self.emitter.log.emit(f"[MASTER] Requête inconnue {addr}: {msg[:120]}")

        except Exception as e:
            self.emitter.log.emit(f"[MASTER] ERREUR client {addr}: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def handle_register(self, conn, msg):
        parts = msg.split("|")
        if len(parts) != 6:
            return
        _, name, ip, port_s, e_s, n_s = parts
        try:
            port = int(port_s)
            e = int(e_s)
            n = int(n_s)
        except ValueError:
            return

        try:
            db_upsert_router(self.cfg, name, ip, port, e, n)
        except Exception as e:
            self.emitter.log.emit(f"[MASTER] ERREUR DB router: {e}")
            return

        try:
            conn.sendall(b"OK\n")
        except Exception:
            pass

        self.emitter.log.emit(f"[MASTER] REGISTER → {name} ({ip}:{port})")
        self.update_router_list()

    def handle_client_hello(self, conn, msg):
        parts = msg.split("|")
        if len(parts) != 4:
            return
        _, name, ip, port_s = parts
        try:
            port = int(port_s)
        except ValueError:
            return

        try:
            db_upsert_client(self.cfg, name, ip, port)
        except Exception as e:
            self.emitter.log.emit(f"[MASTER] ERREUR DB client: {e}")
            return

        try:
            conn.sendall(b"OK\n")
        except Exception:
            pass

        self.emitter.log.emit(f"[MASTER] CLIENT → {name} ({ip}:{port})")

    def handle_list(self, conn):
        try:
            rows = db_list_active_routers(self.cfg, seconds=5)
        except Exception as e:
            self.emitter.log.emit(f"[MASTER] ERREUR DB list: {e}")
            try:
                conn.sendall(b"ROUTERS|\n")
            except Exception:
                pass
            return

        entries = []
        for (name, ip, port, e, n) in rows:
            entries.append(f"{name},{ip},{int(port)},{int(e or 0)},{int(n or 0)}")

        out = "ROUTERS|" + ";".join(entries) + "\n"
        try:
            conn.sendall(out.encode(ENC))
        except Exception:
            pass

    def update_router_list(self):
        try:
            rows = db_list_active_routers(self.cfg, seconds=30)
        except Exception:
            rows = []

        data = [
            f"{name} - {ip}:{int(port)} (e={int(e or 0)}, n={int(n or 0)})"
            for (name, ip, port, e, n) in rows
        ]
        self.emitter.routers_updated.emit(data)

class MasterGUI(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.setWindowTitle("MASTER")
        self.resize(760, 560)

        self.cfg = cfg
        self.server = None

        self.emitter = Emitter()
        self.emitter.log.connect(self.add_log)
        self.emitter.routers_updated.connect(self.refresh_routers)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        self.status = QLabel("Serveur: arrêté")
        lay.addWidget(self.status)

        self.router_list = QListWidget()
        lay.addWidget(self.router_list)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        lay.addWidget(self.logs)

        self.btn_start = QPushButton("Démarrer le Master")
        self.btn_start.clicked.connect(self.toggle_master)
        lay.addWidget(self.btn_start)

        self.btn_refresh = QPushButton("Rafraîchir routeurs")
        self.btn_refresh.clicked.connect(self.manual_refresh)
        lay.addWidget(self.btn_refresh)

        try:
            db_ensure_ready(self.cfg)
            self.add_log(f"[MASTER] DB prête: {self.cfg['db_name']} + table nodes.")
        except Exception as e:
            self.add_log(f"[MASTER] ERREUR DB init: {e}")
            self.add_log("[MASTER] -> Ton user DB doit avoir CREATE DATABASE + CREATE TABLE.")

    def add_log(self, s):
        self.logs.append(s)

    def refresh_routers(self, data):
        self.router_list.clear()
        for item in data:
            self.router_list.addItem(item)

    def toggle_master(self):
        if self.server:
            self.server.stop()
            self.server = None
            self.btn_start.setText("Démarrer le Master")
            self.status.setText("Serveur: arrêté")
            self.add_log("[MASTER] Arrêt demandé.")
            return

        try:
            db_ensure_ready(self.cfg)
        except Exception as e:
            self.add_log(f"[MASTER] ERREUR DB init: {e}")
            return

        self.server = MasterServer("0.0.0.0", self.cfg["port"], self.cfg, self.emitter)
        self.server.start()

        self.btn_start.setText("Arrêter le Master")
        self.status.setText(f"Serveur: actif (port {self.cfg['port']})")
        self.add_log("[MASTER] Master démarré.")
        self.server.update_router_list()

    def manual_refresh(self):
        if self.server:
            self.server.update_router_list()

def main():
    try:
        cfg = parse_cli(sys.argv)
    except Exception as e:
        print("[ERREUR]", e)
        print_usage_and_exit()
        return

    app = QApplication(sys.argv)
    gui = MasterGUI(cfg)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
