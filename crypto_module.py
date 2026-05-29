# ==============================================================================
# FILENAME: crypto_module.py
# DESCRIPTION: MahaVault Ultimate Engine Layer (2 Klasik + 2 Modern)
# ==============================================================================
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ------------------------------------------------------------------------------
# LAYER KLASIK 1 & 2: CAESAR & VIGENERE
# ------------------------------------------------------------------------------
def _caesar_cipher(text, shift, encrypt=True):
    result = ""
    actual_shift = shift if encrypt else -shift
    for char in text:
        if char.isupper():
            result += chr((ord(char) - 65 + actual_shift) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) - 97 + actual_shift) % 26 + 97)
        elif char.isdigit():
            result += chr((ord(char) - 48 + actual_shift) % 10 + 48)
        else:
            result += char
    return result

def _vigenere_cipher(text, key, encrypt=True):
    if not key:
        return text
    result = ""
    key = key.lower()
    key_idx = 0
    for char in text:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - 97
            actual_shift = shift if encrypt else -shift
            if char.isupper():
                result += chr((ord(char) - 65 + actual_shift) % 26 + 65)
            else:
                result += chr((ord(char) - 97 + actual_shift) % 26 + 97)
            key_idx += 1
        else:
            result += char
    return result

# ------------------------------------------------------------------------------
# LAYER MODERN 1: RSA ASYMMETRIC KEY GENERATOR
# ------------------------------------------------------------------------------
def robust_generate_rsa_keys():
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        return priv_pem, pub_pem
    except Exception:
        return None, None

# ------------------------------------------------------------------------------
# ENGINE CORE ENKRIPSI UTAMA
# ------------------------------------------------------------------------------
def robust_rsa_encrypt(plaintext, public_key_pem, multi_layer=False, caesar_shift=3, vigenere_key="PAWN"):
    try:
        # Load Public Key Terlebih Dahulu untuk memastikan validitas gembok
        pub_key = serialization.load_pem_public_key(
            public_key_pem.strip().encode('utf-8'),
            backend=default_backend()
        )
        
        if not multi_layer:
            # MODE COMPATIBLE (KIRIM TEMAN): Hanya Murni RSA OAEP SHA256
            ciphertext = pub_key.encrypt(
                plaintext.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return ciphertext.hex(), True
        else:
            # MODE MULTI-LAYER (DEMO DOSEN): 2 Klasik + 2 Modern
            # 1. Klasik 1: Caesar Cipher
            c1_out = _caesar_cipher(plaintext, caesar_shift, encrypt=True)
            # 2. Klasik 2: Vigenere Cipher
            c2_out = _vigenere_cipher(c1_out, vigenere_key, encrypt=True)
            
            # 3. Modern 1: AES-256 GCM (Bikin Session Key 32 Byte)
            aes_key = os.urandom(32)
            iv = os.urandom(12)
            encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend()).encryptor()
            aes_ciphertext = encryptor.update(c2_out.encode('utf-8')) + encryptor.finalize()
            tag = encryptor.tag
            
            # Gabungkan payload AES: IV(12B) + TAG(16B) + CIPHERTEXT
            full_aes_payload = iv + tag + aes_ciphertext
            
            # 4. Modern 2: Amankan Kunci AES menggunakan Kunci Publik RSA (Enkripsi Amplop)
            encrypted_aes_key = pub_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Output akhir dalam bentuk Hex gabungan yang aman
            final_hex = encrypted_aes_key.hex() + ":" + full_aes_payload.hex()
            return final_hex, True
            
    except Exception as e:
        return f"ERROR_ENCRYPT: {str(e)}", False

# ------------------------------------------------------------------------------
# ENGINE CORE DEKRIPSI UTAMA
# ------------------------------------------------------------------------------
def robust_rsa_decrypt(ciphertext_hex, private_key_pem, multi_layer=False, caesar_shift=3, vigenere_key="PAWN"):
    try:
        priv_key = serialization.load_pem_private_key(
            private_key_pem.strip().encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        if not multi_layer:
            # MODE COMPATIBLE (BONGKAR PESAN TEMAN)
            ciphertext = bytes.fromhex(ciphertext_hex.strip())
            decrypted = priv_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode('utf-8'), True
        else:
            # MODE MULTI-LAYER (DEMO DOSEN)
            if ":" not in ciphertext_hex:
                return "ERROR: Format data stego bukan data Multi-Layer!", False
                
            enc_rsa_part, enc_aes_part = ciphertext_hex.strip().split(":")
            
            # 1. Dekripsi Modern 2: Ambil Kunci AES lewat RSA Private Key
            aes_key = priv_key.decrypt(
                bytes.fromhex(enc_rsa_part),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Pecah berkas AES payload
            aes_bytes = bytes.fromhex(enc_aes_part)
            iv = aes_bytes[:12]
            tag = aes_bytes[12:28]
            actual_ciphertext = aes_bytes[28:]
            
            # 2. Dekripsi Modern 1: Bongkar isi pesan via AES-256 GCM
            decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
            vigenere_out = (decryptor.update(actual_ciphertext) + decryptor.finalize()).decode('utf-8')
            
            # 3. Dekripsi Klasik 2: Balikkan Vigenere Cipher
            caesar_out = _vigenere_cipher(vigenere_out, vigenere_key, encrypt=False)
            # 4. Dekripsi Klasik 1: Balikkan Caesar Cipher
            plaintext_asli = _caesar_cipher(caesar_out, caesar_shift, encrypt=False)
            
            return plaintext_asli, True
            
    except Exception as e:
        return f"ERROR_DECRYPT: Gagal memproses struktur kunci ({str(e)})", False