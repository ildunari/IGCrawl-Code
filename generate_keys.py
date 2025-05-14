import base64
import os

# Generate a proper Fernet key
encryption_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print("ENCRYPTION_KEY:", encryption_key)

# Generate a proper secret key 
secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print("SECRET_KEY:", secret_key)

# For Instagram
instagram_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
print("INSTAGRAM_ENCRYPTION_KEY:", instagram_key)