

def make_final_layer(ip, port, message):
    # F|ip|port|message
    return "F|" + ip + "|" + str(port) + "|" + message


def make_route_layer(ip, port, cipher_str):
    # N|ip|port|cipher_str
    return "N|" + ip + "|" + str(port) + "|" + cipher_str


def parse_layer(s):
    """
    Retourne (type_flag, ip, port, reste)
    type_flag : 'N' (routeur) ou 'F' (final)
    """
    parts = s.split("|", 3)  # 4 morceaux max, le dernier peut contenir des '|'
    if len(parts) < 4:
        raise ValueError("Layer invalide")
    type_flag = parts[0]
    ip = parts[1]
    port = int(parts[2])
    rest = parts[3]
    return type_flag, ip, port, rest
