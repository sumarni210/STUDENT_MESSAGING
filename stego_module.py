# ==============================================================================
# FILENAME: stego_module.py
# DESCRIPTION: MahaVault Steganography Matrix Engine
# ==============================================================================
import numpy as np
import cv2
import matplotlib.pyplot as plt

def lsb_encrypt(img, secret_string, variant="Sequential", seed=None):
    if variant == "Random" and not seed:
        return None, "Password Wajib Diisi untuk Metode Random LSB!"
        
    formatted_secret = f"SHADOW_V5_{secret_string.strip()}END_OF_SHADOW"
    binary_secret = ''.join([format(ord(char), '08b') for char in formatted_secret])
    data_len = len(binary_secret)
    
    height, width, channels = img.shape
    
    coords = []
    for row in range(height):
        for col in range(width):
            for ch in range(channels):
                coords.append((row, col, ch))
                
    if variant == "Random" and seed:
        np.random.seed(sum(ord(char) for char in seed))
        np.random.shuffle(coords)
        
    if data_len > len(coords):
        return None, "Ukuran pesan terlalu besar untuk resolusi gambar ini!"
        
    stego_img = img.copy()
    for idx in range(data_len):
        row, col, ch = coords[idx]
        stego_img[row, col, ch] = (int(stego_img[row, col, ch]) & 0xFE) | int(binary_secret[idx])
        
    return stego_img, None

def lsb_extract(img, variant="Sequential", seed=None):
    if variant == "Random" and not seed:
        return "ERROR_VALIDASI: Mode Random membutuhkan password pengunci!", False
        
    height, width, channels = img.shape
    
    coords = []
    for row in range(height):
        for col in range(width):
            for ch in range(channels):
                coords.append((row, col, ch))
                
    if variant == "Random" and seed:
        np.random.seed(sum(ord(char) for char in seed))
        np.random.shuffle(coords)
        
    extracted_bits = []
    max_bits = min(32000, len(coords))
    for i in range(max_bits):
        row, col, ch = coords[i]
        extracted_bits.append(str(img[row, col, ch] & 1))
    
    full_binary_str = "".join(extracted_bits)
    
    try:
        all_chars = []
        for i in range(0, len(full_binary_str), 8):
            byte = full_binary_str[i:i+8]
            if len(byte) < 8:
                break
            all_chars.append(chr(int(byte, 2)))
            
        full_text_string = "".join(all_chars)
        
        if "SHADOW_V5_" not in full_text_string or "END_OF_SHADOW" not in full_text_string:
            return "ERROR_VALIDASI: Struktur bit corrupt atau penanda tidak ditemukan!", False
            
        start_idx = full_text_string.find("SHADOW_V5_") + len("SHADOW_V5_")
        end_idx = full_text_string.find("END_OF_SHADOW")
        
        clean_ciphertext = full_text_string[start_idx:end_idx]
        return clean_ciphertext, True
    except Exception as e:
        return f"ERROR_VALIDASI: Gagal menerjemahkan aliran bit biner ({str(e)})", False

def plot_advanced_forensics(orig, stego, mode_name):
    plt.style.use('default')
    diff = cv2.absdiff(orig, stego)
    mutation_map = (diff[:,:,0] * 255).astype(np.uint8)
    
    fig, axs = plt.subplots(2, 2, figsize=(11, 7))
    
    axs[0, 0].imshow(orig)
    axs[0, 0].set_title("1. Original Image Preview", color='#00ffcc', weight='bold')
    axs[0, 0].axis('off')
    
    axs[0, 1].imshow(mutation_map, cmap='cool')
    axs[0, 1].set_title(f"2. Pixel Mutation Map ({mode_name})", color='#ff007f', weight='bold')
    axs[0, 1].axis('off')
    
    axs[1, 0].hist(orig.ravel(), bins=256, color='#00b3ff', alpha=0.6)
    axs[1, 0].set_title("3. Original Color Histogram")
    
    axs[1, 1].hist(stego.ravel(), bins=256, color='#ff007f', alpha=0.6)
    axs[1, 1].set_title("4. Stego Color Histogram")
    
    plt.tight_layout()
    return fig