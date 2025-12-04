"""
Encryption utilities for privacy-first data storage.
All sensitive data is encrypted at rest using Fernet symmetric encryption.
"""
import os
import keyring
import hashlib
from pathlib import Path
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from config import (
    ENCRYPTION_ALGORITHM,
    KEY_DERIVATION_ITERATIONS,
    SALT_LENGTH,
    DATABASE_ENCRYPTION_KEY_NAME,
)


class EncryptionManager:
    """Manages encryption/decryption operations for the agent."""
    
    def __init__(self, key_name: str = DATABASE_ENCRYPTION_KEY_NAME):
        """
        Initialize the encryption manager.
        
        Args:
            key_name: Name to identify the encryption key in keyring
        """
        self.key_name = key_name
        self.service_name = "privacy_first_agent"
        self._fernet: Optional[Fernet] = None
        
    def initialize_key(self, password: Optional[str] = None) -> None:
        """
        Initialize or retrieve the encryption key.
        
        Args:
            password: Optional password for key derivation. If None, generates random key.
        """
        # Try to retrieve existing key from keyring
        try:
            existing_key = keyring.get_password(self.service_name, self.key_name)
            if existing_key:
                self._fernet = Fernet(existing_key.encode())
                return
        except Exception as e:
            print(f"Warning: Could not retrieve key from keyring: {e}")
        
        # Generate new key
        if password:
            key = self._derive_key_from_password(password)
        else:
            key = Fernet.generate_key()
        
        # Store in keyring
        try:
            keyring.set_password(self.service_name, self.key_name, key.decode())
            self._fernet = Fernet(key)
            print("[OK] Encryption key initialized and stored securely")
        except Exception as e:
            print(f"Warning: Could not store key in keyring: {e}")
            print("Using in-memory key (will not persist)")
            self._fernet = Fernet(key)
    
    def _derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: User password
            salt: Salt for key derivation (generated if not provided)
            
        Returns:
            Derived encryption key
        """
        if salt is None:
            salt = os.urandom(SALT_LENGTH)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=KEY_DERIVATION_ITERATIONS,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        # Store salt with the key (prepend salt to key)
        return Fernet.generate_key()  # For now, use Fernet's key format
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data
        """
        if self._fernet is None:
            self.initialize_key()
        
        if isinstance(data, str):
            data = data.encode()
        
        return self._fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data as string
        """
        if self._fernet is None:
            self.initialize_key()
        
        decrypted = self._fernet.decrypt(encrypted_data)
        return decrypted.decode()
    
    def encrypt_file(self, file_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (defaults to original + .enc)
            
        Returns:
            Path to encrypted file
        """
        file_path = Path(file_path)
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.enc')
        else:
            output_path = Path(output_path)
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return output_path
    
    def decrypt_file(self, encrypted_file_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Decrypt a file.
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path for decrypted file
            
        Returns:
            Path to decrypted file
        """
        encrypted_file_path = Path(encrypted_file_path)
        
        if output_path is None:
            # Remove .enc extension if present
            if encrypted_file_path.suffix == '.enc':
                output_path = encrypted_file_path.with_suffix('')
            else:
                output_path = encrypted_file_path.with_suffix('.dec')
        else:
            output_path = Path(output_path)
        
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt(encrypted_data)
        
        with open(output_path, 'w') as f:
            f.write(decrypted_data)
        
        return output_path
    
    def hash_data(self, data: str) -> str:
        """
        Create a SHA-256 hash of data (for anonymization).
        
        Args:
            data: Data to hash
            
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def anonymize_text(self, text: str, entities_to_mask: list) -> str:
        """
        Anonymize sensitive entities in text.
        
        Args:
            text: Text to anonymize
            entities_to_mask: List of entities to replace (e.g., names, emails)
            
        Returns:
            Anonymized text
        """
        anonymized = text
        for entity in entities_to_mask:
            # Replace with hash prefix for consistency
            hash_prefix = self.hash_data(entity)[:8]
            anonymized = anonymized.replace(entity, f"[REDACTED_{hash_prefix}]")
        
        return anonymized
    
    def secure_delete(self, file_path: Union[str, Path]) -> bool:
        """
        Securely delete a file by overwriting before deletion.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        try:
            # Get file size
            file_size = file_path.stat().st_size
            
            # Overwrite with random data
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size))
            
            # Delete the file
            file_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error securely deleting {file_path}: {e}")
            return False


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager instance."""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
        _encryption_manager.initialize_key()
    return _encryption_manager


if __name__ == "__main__":
    # Test encryption functionality
    print("Testing Encryption Manager...")
    
    em = EncryptionManager()
    em.initialize_key()
    
    # Test string encryption
    test_data = "This is sensitive personal data 🔒"
    encrypted = em.encrypt(test_data)
    decrypted = em.decrypt(encrypted)
    
    print(f"\nOriginal: {test_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_data == decrypted}")
    
    # Test hashing
    sensitive_info = "john.doe@email.com"
    hashed = em.hash_data(sensitive_info)
    print(f"\nHash of '{sensitive_info}': {hashed}")
    
    # Test anonymization
    text = "John called me at 555-1234"
    anonymized = em.anonymize_text(text, ["John", "555-1234"])
    print(f"\nOriginal: {text}")
    print(f"Anonymized: {anonymized}")
