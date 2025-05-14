from cryptography.fernet import Fernet
from typing import Optional
import os
import base64

# Generate or load encryption key
ENCRYPTION_KEY = os.getenv("INSTAGRAM_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"Generated new encryption key: {ENCRYPTION_KEY}")
    print("Please save this in your .env file as INSTAGRAM_ENCRYPTION_KEY")
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

cipher_suite = Fernet(ENCRYPTION_KEY)


def encrypt_credential(credential: str) -> str:
    """Encrypt a credential using AES-256"""
    if not credential:
        return ""
    encrypted = cipher_suite.encrypt(credential.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_credential(encrypted_credential: str) -> str:
    """Decrypt a credential"""
    if not encrypted_credential:
        return ""
    try:
        encrypted_bytes = base64.b64decode(encrypted_credential.encode())
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting credential: {e}")
        return ""