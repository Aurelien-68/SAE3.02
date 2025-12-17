import socket
import threading
import time
import sys

from rsa_utils import generate_keypair
from Sources_codesV2.router_core import RouterOnion

ENC = "utf-8"


def parse_args():
    """
    Parse :
      -n IP_MASTER:PORT_MASTER
      -p PORT_DU_ROUTEUR

    Exemple :
      python routeur.py -n 192.168.1.10:9000 -p 11000
    """
    master_ip = None
    master_port = None
    router_port = None

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
                router_port = int(args[i + 1])
            except ValueError:
                router_port = None
            i += 2
        else:
            i += 1

    if master_ip is None or master_port is None or router_port is None:
        print("Usage : python routeur.py -n IP_MASTER:PORT_MASTER -p PORT_DU_ROUTEUR")
        sys.exit(1)

    # 0.0.0.0 est OK pour bind, pas pour connect → on corrige
    if master_ip == "0.0.0.0":
        print("IP master 0.0.0.0 reçue → utilisation de 127.0.0.1 pour la connexion.")
        master_ip = "127.0.0.1"

    return master_ip, master_port, router_port


def heartbeat(master_ip, master_port, name, router_ip, router_port, pubkey):
    """
    Envoie régulièrement REGISTER au master pour signaler que le routeur est vivant.
    """
    e, n = pubkey
    line = "REGISTER|%s|%s|%d|%d|%d\n" % (
        name, router_ip, router_port, e, n
    )

    while True:
        try:
            with socket.create_connection((master_ip, master_port), timeout=2) as s:
                s.sendall(line.encode(ENC))
        except:
            # master down / inaccessible → on réessaie plus tard
            pass
        time.sleep(2)


def main():
    master_ip, master_port, router_port = parse_args()
    print("Master configuré sur %s:%d" % (master_ip, master_port))
    print("Port d'écoute du routeur : %d" % router_port)

    name = input("Nom du routeur (ex: R1) : ").strip()
    if not name:
        name = "R"

    router_ip = input("IP à annoncer au master (ex: 192.168.1.20) : ").strip()
    if not router_ip:
        router_ip = "127.0.0.1"

    print("→ Routeur %s écoute sur 0.0.0.0:%d et s'annonce comme %s:%d"
          % (name, router_port, router_ip, router_port))

    pubkey, privkey = generate_keypair()
    print("[%s] Clé publique : %r" % (name, pubkey))

    t = threading.Thread(
        target=heartbeat,
        args=(master_ip, master_port, name, router_ip, router_port, pubkey),
        daemon=True
    )
    t.start()

    BIND_IP = "0.0.0.0"
    router = RouterOnion(BIND_IP, router_port, privkey, name=name)
    router.serve_forever()


if __name__ == "__main__":
    main()
