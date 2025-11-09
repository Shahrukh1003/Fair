"""
Security Utilities Module for BiasCheck

Purpose: Anonymize data and encrypt/decrypt alert messages.

This module provides cryptographic functions for securing sensitive information:
1. Fernet symmetric encryption for alert messages
2. SHA256 hashing for pseudonymization of application IDs

How it fits: This is the SECURITY layer across the BiasCheck pipeline.
Data → Metric → Detect → Alert → [ENCRYPT] → Log → Explain → Visualize
"""

import hashlib
import os
from cryptography.fernet import Fernet
from typing import Optional, List
import pandas as pd


def init_key(key_path: str = "fairlens_backend/fernet.key") -> bytes:
    """
    Initialize or load Fernet encryption key.
    
    If the key file exists, loads and returns it. Otherwise, generates a new
    Fernet key, saves it to the specified path, and returns it.
    
    WARNING: This is DEMO-level key storage. In production environments,
    use a proper secrets management system (e.g., AWS Secrets Manager,
    Azure Key Vault, HashiCorp Vault) to store encryption keys securely.
    Never commit keys to version control.
    
    Parameters:
    -----------
    key_path : str, default="fairlens_backend/fernet.key"
        File path where the encryption key is stored.
    
    Returns:
    --------
    bytes
        The Fernet encryption key (32 URL-safe base64-encoded bytes).
    
    Examples:
    ---------
    >>> key = init_key()
    >>> print(type(key))
    <class 'bytes'>
    """
    if os.path.exists(key_path):
        # Load existing key
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    else:
        # Generate new key
        key = Fernet.generate_key()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        
        # Save key to file
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
    
    return key


def encrypt_alert(message: str, key: Optional[bytes] = None) -> str:
    """
    Encrypt an alert message using Fernet symmetric encryption.
    
    Fernet guarantees that a message encrypted using it cannot be manipulated
    or read without the key. It is based on AES in CBC mode with a 128-bit key
    for encryption and HMAC using SHA256 for authentication.
    
    Parameters:
    -----------
    message : str
        The plaintext alert message to encrypt.
    
    key : bytes, optional
        The Fernet encryption key. If None, loads/generates key using init_key().
    
    Returns:
    --------
    str
        The encrypted message as a URL-safe base64-encoded string.
    
    Examples:
    ---------
    >>> alert = "DIR = 0.64 (<0.8). Potential bias detected."
    >>> encrypted = encrypt_alert(alert)
    >>> print(encrypted[:20])  # First 20 chars of token
    gAAAAAB...
    """
    if key is None:
        key = init_key()
    
    cipher = Fernet(key)
    encrypted_bytes = cipher.encrypt(message.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')


def decrypt_alert(token: str, key: Optional[bytes] = None) -> str:
    """
    Decrypt an encrypted alert message.
    
    Parameters:
    -----------
    token : str
        The encrypted message (URL-safe base64-encoded string).
    
    key : bytes, optional
        The Fernet encryption key. If None, loads key using init_key().
    
    Returns:
    --------
    str
        The decrypted plaintext message.
    
    Raises:
    -------
    cryptography.fernet.InvalidToken
        If the token is invalid, tampered with, or encrypted with a different key.
    
    Examples:
    ---------
    >>> encrypted = encrypt_alert("Test message")
    >>> decrypted = decrypt_alert(encrypted)
    >>> print(decrypted)
    Test message
    """
    if key is None:
        key = init_key()
    
    cipher = Fernet(key)
    
    try:
        decrypted_bytes = cipher.decrypt(token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        return f"[DECRYPTION FAILED: {str(e)}]"


def anonymize_data(df: pd.DataFrame, id_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Anonymize specified columns using SHA256 hashing (pseudonymization).
    
    This function replaces identifiable values with their SHA256 hashes,
    making them non-reversible but consistent (same input = same hash).
    
    IMPORTANT: This is pseudonymization for demonstration purposes.
    - Not GDPR-compliant reversible anonymization
    - SHA256 is one-way; original IDs cannot be recovered
    - Same ID always produces same hash (allows joining datasets)
    
    For production GDPR compliance, consider:
    - Tokenization with secure vault
    - Format-preserving encryption (FPE)
    - Differential privacy techniques
    
    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing sensitive identifiers.
    
    id_columns : list, default=["application_id"]
        List of column names to anonymize.
    
    Returns:
    --------
    pd.DataFrame
        A copy of the DataFrame with anonymized ID columns.
    
    Examples:
    ---------
    >>> df = pd.DataFrame({'application_id': [1, 2, 3], 'score': [700, 650, 800]})
    >>> anon_df = anonymize_data(df, id_columns=['application_id'])
    >>> print(anon_df['application_id'][0][:16])  # First 16 chars of hash
    6b86b273ff34fce1
    """
    if id_columns is None:
        id_columns = ["application_id"]
    
    # Create a copy to avoid modifying the original
    df_anonymized = df.copy()
    
    for col in id_columns:
        if col in df_anonymized.columns:
            # Apply SHA256 hashing to each value
            df_anonymized[col] = df_anonymized[col].apply(
                lambda x: hashlib.sha256(str(x).encode('utf-8')).hexdigest()
            )
    
    return df_anonymized
