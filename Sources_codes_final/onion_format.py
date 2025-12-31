# onion_format.py

def make_final_layer(ip, port, message):
    """
        Construit la couche finale de l'onion.

        Format :
          F|ip|port|message

        Cette couche indique la destination finale du message.
    """
    return "F|" + ip + "|" + str(port) + "|" + message


def make_route_layer(ip, port, cipher_str):
    """
        Construit une couche intermédiaire de routage.

        Format :
          N|ip|port|cipher_str

        Cette couche est destinée à un routeur intermédiaire,
        qui devra simplement relayer le message après déchiffrement.
    """
    return "N|" + ip + "|" + str(port) + "|" + cipher_str


def parse_layer(s):
    """
    Analyse une couche d'onion reçue.

    Retourne :
      (type_flag, ip, port, reste)

    - type_flag : 'N' pour un routeur intermédiaire
                  'F' pour la destination finale
    - ip: adresse IP cible
    - port: port cible
    - reste: charge utile (message ou couche suivante)
    """

    """
    Découpe la chaîne en 4 parties max :
     1. type de couche (N ou F)
    2. IP
    3. port
    4. reste du message (message final ou couche suivante)
    """
    parts = s.split("|", 3)
    if len(parts) < 4:
        raise ValueError("Layer invalide")
    type_flag = parts[0]
    ip = parts[1]
    port = int(parts[2])
    rest = parts[3]
    return type_flag, ip, port, rest
