import base64
from cryptography.fernet import Fernet, InvalidToken
import os
import logging

logger = logging.getLogger(__name__)

key_path = "Db_handler/key.key"
try:
    with open(key_path, "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    logger.warning(f"Encryption key file '{key_path}' not found. Generating new key.")
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    logger.warning("New key generated. Existing encrypted data may be invalid.")

fernet = Fernet(key)

def encrypt(message: str) -> str:
    try:
        if not message or not isinstance(message, str):
            return ""
        encrypted = fernet.encrypt(message.encode())
        encoded_data = base64.b64encode(encrypted).decode()
        return encoded_data
    except Exception as e:
        logger.error(f"Encryption error: {type(e).__name__}: {str(e)}")
        return ""

def decrypt(encoded_data: str) -> str:
    try:
        if not encoded_data or not isinstance(encoded_data, str):
            return ""
        encrypted_data = base64.b64decode(encoded_data)
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data
    except (base64.binascii.Error, InvalidToken) as e:
        logger.error(f"Decryption error for data '{encoded_data[:10]}...': {type(e).__name__}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected decryption error for data '{encoded_data[:10]}...': {type(e).__name__}: {str(e)}")
        return ""

import hashlib

def hash_email(email: str) -> str:
    try:
        if not email or not isinstance(email, str):
            return ""
        return hashlib.sha256(email.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Hashing error for email: {type(e).__name__}: {str(e)}")
        return ""