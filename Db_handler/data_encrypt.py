
"""key = Fernet.generate_key()
with open("key.key", "wb") as key_file:
    key_file.write(key)
"""
import base64
from cryptography.fernet import Fernet


with open("Db_handler/key.key", "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)

def encrypt(message: str) -> str:
    encrypted = fernet.encrypt(message.encode())
    encoded_data = base64.b64encode(encrypted).decode()
    return encoded_data

def decrypt(encoded_data: str) -> str:
    encrypted_data = base64.b64decode(encoded_data)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

import hashlib

def hash_email(email: str) -> str:

    return hashlib.sha256(email.encode()).hexdigest()

