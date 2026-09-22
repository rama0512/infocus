

import bcrypt

# To hash a password
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')  # Store as string in DB

# To verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')  # Convert back to bytes
    is_valid = bcrypt.checkpw(password_bytes, hashed_password_bytes)
    return is_valid
