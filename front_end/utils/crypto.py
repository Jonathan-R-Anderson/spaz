
# Generate a random encryption key per session using elliptic curve
def _generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

# Serialize the public key to send it to the client
def _serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

# Encrypt the HMAC secret using the public key (ECC)
def _encrypt_secret(secret, public_key):
    encrypted_secret = public_key.encrypt(
        secret.encode(),
        ec.ECIESHKDF(salt=None, algorithm=hashes.SHA256())
    )
    return base64.b64encode(encrypted_secret).decode('utf-8')

