import base64
from typing import Union

STATIC_KEY = b"P2PChatSecretKey2024!@#$"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    key_len = len(key)
    return bytes([data[i] ^ key[i % key_len] for i in range(len(data))])


def encode_message(plaintext: str) -> str:
    data = plaintext.encode('utf-8')
    encrypted = _xor_bytes(data, STATIC_KEY)
    encoded = base64.b64encode(encrypted).decode('ascii')
    return encoded


def decode_message(encoded: str) -> str:
    try:
        encrypted = base64.b64decode(encoded.encode('ascii'))
        decrypted = _xor_bytes(encrypted, STATIC_KEY)
        return decrypted.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Could not decode message: {e}")


def is_encoded(message: str) -> bool:
    try:
        decoded = base64.b64decode(message.encode('ascii'))
        re_encoded = base64.b64encode(decoded).decode('ascii')
        return re_encoded == message
    except Exception:
        return False
