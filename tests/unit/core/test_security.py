import pytest
from app.core.config import settings

def test_encryption_decryption():
    """
    Test that sensitive data can be encrypted and decrypted correctly.
    """
    try:
        from app.core.security import encrypt_token, decrypt_token
    except ImportError:
        pytest.fail("app.core.security module not found")

    original_token = "my-secret-refresh-token"
    
    # 1. Encrypt
    encrypted = encrypt_token(original_token)
    assert encrypted != original_token
    assert isinstance(encrypted, str)
    
    # 2. Decrypt
    decrypted = decrypt_token(encrypted)
    assert decrypted == original_token

def test_encryption_same_value_different_output():
    """
    Fernet encryption should produce different ciphertexts for the same plaintext 
    (due to random IV).
    """
    try:
        from app.core.security import encrypt_token
    except ImportError:
        pytest.fail("app.core.security module not found")
        
    token = "stable-token"
    enc1 = encrypt_token(token)
    enc2 = encrypt_token(token)
    
    assert enc1 != enc2
