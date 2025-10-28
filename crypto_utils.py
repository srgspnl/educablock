# crypto_utils.py
"""
Módulo com funções de criptografia RSA
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64


class RSACrypto:
    """Classe para operações de criptografia RSA"""
    
    @staticmethod
    def generate_keys():
        """
        Gera um par de chaves RSA (privada e pública)
        
        Returns:
            tuple: (chave_privada_pem, chave_publica_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Serializar chave privada
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Serializar chave pública
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_file(content, public_key_pem):
        """
        Criptografa conteúdo usando chave pública RSA
        
        Args:
            content (bytes): Conteúdo a ser criptografado
            public_key_pem (str): Chave pública em formato PEM
            
        Returns:
            str: Conteúdo criptografado em base64
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        # RSA pode criptografar apenas dados pequenos, então dividimos em chunks
        max_chunk_size = 190  # Para chave de 2048 bits
        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        
        encrypted_chunks = []
        for chunk in chunks:
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode('utf-8'))
        
        return '\n'.join(encrypted_chunks)
    
    @staticmethod
    def decrypt_file(encrypted_content, private_key_pem):
        """
        Descriptografa conteúdo usando chave privada RSA
        
        Args:
            encrypted_content (str): Conteúdo criptografado em base64
            private_key_pem (str): Chave privada em formato PEM
            
        Returns:
            bytes: Conteúdo descriptografado
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        encrypted_chunks = encrypted_content.strip().split('\n')
        decrypted_chunks = []
        
        for chunk in encrypted_chunks:
            encrypted_data = base64.b64decode(chunk)
            decrypted_chunk = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
        
        return b''.join(decrypted_chunks)
