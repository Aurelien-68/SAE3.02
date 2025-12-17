# rsa_utils.py
from random import choice
from math import gcd
import json
import base64

from primes import PRIME_LIST


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a) #algorithme d’Euclide étendu
    return g, y1 - (b // a) * x1, x1


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Pas d’inverse modulaire")
    return x % m


def generate_keypair():
    """
    Génère une paire de clés RSA (pub, priv) à partir de PRIME_LIST.
    """
    p = choice(PRIME_LIST)
    q = choice(PRIME_LIST)
    while q == p:
        q = choice(PRIME_LIST)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    d = modinv(e, phi)
    return (e, n), (d, n)


def rsa_encrypt_bytes(b: bytes, public_key):
    """
    Chiffre des octets, retourne une liste d'entiers.
    """
    e, n = public_key
    return [pow(byte, e, n) for byte in b]


def rsa_decrypt_bytes(lst, private_key):
    """
    Déchiffre une liste d'entiers en bytes.
    """
    d, n = private_key
    return bytes([pow(x, d, n) for x in lst])


def encode_cipher(lst):
    """
    Convertit la liste d'entiers en string base64 (pour envoi réseau).
    """
    j = json.dumps(lst).encode("utf-8")
    return base64.b64encode(j).decode("ascii")


def decode_cipher(s):
    """
    Convertit la string base64 en liste d'entiers.
    """
    j = base64.b64decode(s.encode("ascii"))
    return json.loads(j.decode("utf-8"))
