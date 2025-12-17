from random import choice
from math import gcd
from Sources_codesV2.primes import PRIME_LIST


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
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
    e, n = public_key
    return [pow(byte, e, n) for byte in b]


def rsa_decrypt_bytes(lst, private_key):
    d, n = private_key
    return bytes([pow(x, d, n) for x in lst])


def cipher_to_str(lst):
    """
    Encode la liste d'entiers en string "12,45,789,..."
    """
    return ",".join(str(x) for x in lst)


def cipher_from_str(s):
    """
    Decode la string "12,45,789,..." en liste d'entiers.
    """
    if not s:
        return []
    parts = s.split(",")
    res = []
    for p in parts:
        p = p.strip()
        if p:
            res.append(int(p))
    return res
