"""
MÓDULO DE CRIPTOGRAFÍA - Seguridad de Software
Técnicas implementadas:
1. AES-256 (Cifrado Simétrico)
2. RSA-2048 (Cifrado Asimétrico)
3. SHA-256 con Salt (Hashing seguro)
"""

import hashlib
import secrets
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64


class CryptoManager:
    """Gestor centralizado de operaciones criptográficas"""
    
    def __init__(self):
        self.backend = default_backend()
    
    # ============ 1. HASH SEGURO CON SALT (SHA-256) ============
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple:
        """
        Hash SHA-256 con salt para contraseñas
        Retorna: (hash_hex, salt_hex)
        """
        if salt is None:
            salt = secrets.token_bytes(32)  # 32 bytes = 256 bits de salt
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations=100000  # PBKDF2 con 100k iteraciones
        )
        
        return (
            pwd_hash.hex(),
            salt.hex()
        )
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verifica contraseña contra hash almacenado"""
        salt_bytes = bytes.fromhex(salt)
        new_hash, _ = CryptoManager.hash_password(password, salt_bytes)
        return new_hash == stored_hash
    
    # ============ 2. CIFRADO SIMÉTRICO (AES-256 con Fernet) ============
    @staticmethod
    def generate_symmetric_key() -> str:
        """Genera clave AES-256 codificada en base64"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def encrypt_aes(plaintext: str, key: str) -> str:
        """
        Cifra texto con AES-256 (Fernet)
        Retorna: ciphertext en base64
        """
        try:
            f = Fernet(key.encode())
            ciphertext = f.encrypt(plaintext.encode())
            return ciphertext.decode()
        except Exception as e:
            raise ValueError(f"Error en cifrado AES: {str(e)}")
    
    @staticmethod
    def decrypt_aes(ciphertext: str, key: str) -> str:
        """
        Descifra texto con AES-256
        Retorna: plaintext original
        """
        try:
            f = Fernet(key.encode())
            plaintext = f.decrypt(ciphertext.encode())
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Error en descifrado AES: {str(e)}")
    
    # ============ 3. CIFRADO ASIMÉTRICO (RSA-2048) ============
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> tuple:
        """
        Genera par de claves RSA
        Retorna: (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Serializar a PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_rsa(plaintext: str, public_key_pem: str) -> str:
        """Cifra con RSA usando clave pública"""
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        ciphertext = public_key.encrypt(
            plaintext.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(ciphertext).decode()
    
    @staticmethod
    def decrypt_rsa(ciphertext_b64: str, private_key_pem: str) -> str:
        """Descifra con RSA usando clave privada"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode()
    
    # ============ 4. CIFRADO CLÁSICO (CÉSAR) ============
    @staticmethod
    def caesar_encrypt(plaintext: str, shift: int = 3) -> str:
        """Cifrado César simple"""
        result = []
        for char in plaintext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base + shift) % 26
                result.append(chr(base + shifted))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def caesar_decrypt(ciphertext: str, shift: int = 3) -> str:
        """Descifrado César"""
        return CryptoManager.caesar_encrypt(ciphertext, -shift)
    
    # ============ UTILIDADES ============
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Genera token seguro aleatorio"""
        return secrets.token_urlsafe(length)


# Pruebas rápidas
if __name__ == "__main__":
    crypto = CryptoManager()
    
    print("=" * 50)
    print("TEST: MÓDULO DE CRIPTOGRAFÍA")
    print("=" * 50)
    
    # Test 1: Hash SHA-256
    print("\n[1] HASH SHA-256 CON SALT")
    pwd = "MiContraseña123"
    hash_pwd, salt = crypto.hash_password(pwd)
    print(f"Contraseña: {pwd}")
    print(f"Hash: {hash_pwd[:32]}...")
    print(f"Salt: {salt[:32]}...")
    print(f"Verificación: {crypto.verify_password(pwd, hash_pwd, salt)}")
    
    # Test 2: AES
    print("\n[2] AES-256 (Simétrico)")
    key = crypto.generate_symmetric_key()
    plaintext = "Datos sensibles 🔐"
    ciphertext = crypto.encrypt_aes(plaintext, key)
    decrypted = crypto.decrypt_aes(ciphertext, key)
    print(f"Original: {plaintext}")
    print(f"Cifrado: {ciphertext[:50]}...")
    print(f"Descifrado: {decrypted}")
    
    # Test 3: RSA
    print("\n[3] RSA-2048 (Asimétrico)")
    priv, pub = crypto.generate_rsa_keypair()
    message = "Mensaje confidencial"
    encrypted = crypto.encrypt_rsa(message, pub)
    decrypted_rsa = crypto.decrypt_rsa(encrypted, priv)
    print(f"Original: {message}")
    print(f"Cifrado: {encrypted[:50]}...")
    print(f"Descifrado: {decrypted_rsa}")
    
    # Test 4: César
    print("\n[4] CIFRADO CÉSAR")
    plain = "CRIPTOGRAFIA"
    cesar_enc = crypto.caesar_encrypt(plain, 5)
    cesar_dec = crypto.caesar_decrypt(cesar_enc, 5)
    print(f"Original: {plain}")
    print(f"Cifrado (shift=5): {cesar_enc}")
    print(f"Descifrado: {cesar_dec}")
    
    print("\n" + "=" * 50)
