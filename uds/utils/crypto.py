#crypto.py
from Crypto.Cipher import AES
import secrets

def random_bytes(x: int) -> bytes:
    'Generate x random bytes.'
    return secrets.token_bytes(x)

def random_hex_list(x: int) -> list[int]:
    'Generate a list of random hex bytes of length x.'
    return list(random_bytes(x))

def aes128_encrypt(data: bytes, key: bytes) -> list[int]:
    'AES128 encrypt data with key and return as list of ints.'
    if len(data) != 16 or len(key) != 16:
        raise ValueError("AES128 requires 16-byte key and 16-byte data")
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(data)

def aes128_encrypt_hex_list(hex_list: list[int], key_list: list[int]) -> list[int]:
    'AES128 encrypt a list of 16 hex bytes with a list of 16 hex bytes key.'
    data_bytes = bytes(hex_list)
    key_bytes = bytes(key_list)
    encrypted = aes128_encrypt(data_bytes, key_bytes)
    return list(encrypted)