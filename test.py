from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()

# Print the key in base64-encoded format
print(key.decode())
