# ==============================================================================
# FILENAME: crypto_module.py
# DESCRIPTION: MahaVault Engine Layer - 100% Dual-Way Synchronized with Modulo 256
# ==============================================================================
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# --- FIX SINKRONISASI: Menggunakan Modulo 256 utuh agar sama dengan kodingan teman lu ---
def _caesar_cipher(text, shift, encrypt=True):
    result = ""
    for char in text:
        orig_ascii = ord(char)
        if encrypt:
            new_ascii = (orig_ascii + shift) % 256
        else:
            new_ascii = (orig_ascii - shift) % 256
        result += chr(new_ascii)
    return result

# --- FIX SINKRONISASI: Menggunakan Modulo 256 utuh agar sama dengan kodingan teman lu ---
def _vigenere_cipher(text, key, encrypt=True):
    if not key:
        return text
    result = ""
    key_ints = [ord(k) for k in key]
    key_len = len(key_ints)
    
    for i, char in enumerate(text):
        orig_ascii = ord(char)
        shift = key_ints[i % key_len]
        if encrypt:
            new_ascii = (orig_ascii + shift) % 256
        else:
            new_ascii = (orig_ascii - shift) % 256
        result += chr(new_ascii)
    return result

def robust_generate_rsa_keys():
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    except Exception as e:
        return None, None

def robust_rsa_encrypt(plaintext, public_key_pem, multi_layer=False, caesar_shift=0, vigenere_key=""):
    try:
        pub_bytes = public_key_pem.encode('utf-8')
        pub_key = serialization.load_pem_public_key(pub_bytes, backend=default_backend())
        
        if multi_layer:
            caesar_out = _caesar_cipher(plaintext, caesar_shift, encrypt=True)
            classic_cipher = _vigenere_cipher(caesar_out, vigenere_key, encrypt=True)
        else:
            classic_cipher = plaintext
            
        encrypted_bytes = pub_key.encrypt(
            classic_cipher.encode('latin-1'),
            rsa_padding.PKCS1v15()
        )
        return base64.b64encode(encrypted_bytes).decode(), True
    except Exception as e:
        return f"ERROR_SYSTEM: Gagal memproses enkripsi hybrid ({str(e)})", False

def robust_rsa_decrypt(ciphertext_base64, private_key_pem, multi_layer=False, caesar_shift=0, vigenere_key=""):
    try:
        priv_bytes = private_key_pem.encode('utf-8')
        priv_key = serialization.load_pem_private_key(priv_bytes, password=None, backend=default_backend())
        
        raw_encrypted_bytes = base64.b64decode(ciphertext_base64.strip())
        decrypted_bytes = priv_key.decrypt(
            raw_encrypted_bytes,
            rsa_padding.PKCS1v15()
        )
        rsa_decoded = decrypted_bytes.decode('latin-1')
        
        if multi_layer:
            vigenere_decoded = _vigenere_cipher(rsa_decoded, vigenere_key, encrypt=False)
            plaintext_asli = _caesar_cipher(vigenere_decoded, caesar_shift, encrypt=False)
        else:
            plaintext_asli = rsa_decoded
            
        return plaintext_asli, True
    except Exception as e:
        return f"ERROR_SYSTEM: Gagal memproses dekripsi hybrid ({str(e)})", False