# ==============================================================================
# FILENAME: app.py
# DESCRIPTION: Aplikasi Kriptografi & Steganografi (Fixed Blank Page Issue)
# ==============================================================================
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import crypto_module as cm
import stego_module as sm

# ==============================================================================
# 0. REFRESHED UI THEME - HIGH CONTRAST & ADEM DI MATA
# ==============================================================================
st.set_page_config(page_title="Student Messaging", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* Global Base Styling */
    html, body, [data-testid="stAppViewContainer"], [class*="stApp"] { 
        background-color: #0a0f1d !important; 
        color: #e2e8f0 !important;
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }
    
    /* Header & Label Styling */
    h1, h2, h3, h4, label, .stWidgetLabel, p {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
    }
    h1, h2, h3 {
        color: #00f0ff !important; /* Neon Cyan */
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.1);
    }
    
    /* Sidebar Segregation (Tegas & Solid) */
    [data-testid="stSidebar"] { 
        background-color: #111827 !important; 
        border-right: 2px solid #1f2937 !important; 
    }
    [data-testid="stSidebar"] * {
        color: #9ca3af !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #00f0ff !important;
    }
    
    /* Tombol Reset/Flush di Sidebar Tetap Merah Solid Menyala */
    [data-testid="stSidebar"] div.stButton > button {
        background: #ff1a53 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 2px solid #ff0055 !important;
        box-shadow: 0 0 12px rgba(255, 26, 83, 0.4) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: #ffffff !important;
        color: #ff1a53 !important;
        box-shadow: 0 0 20px rgba(255, 26, 83, 0.7) !important;
        border-color: #ffffff !important;
    }
    
    /* Card & Container Box */
    div.stBlock, .module-card, [data-testid="stExpander"] {
        background: #141b2d !important;
        border: 1px solid #1f2937 !important;
        border-left: 4px solid #00f0ff !important;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    /* Form Inputs & Text Areas */
    textarea, input, [data-baseweb="input"], [data-baseweb="textarea"], [data-testid="stSelectbox"] div {
        background-color: #070b14 !important;
        color: #ffffff !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
    }
    textarea:focus, input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.3) !important;
    }
    
    /* Tabs Component Styling */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
        font-weight: 700 !important;
    }
    
    /* Code blocks Styling */
    code, pre, [data-testid="stCodeBlock"] {
        background-color: #070b14 !important;
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px;
    }
    
    /* Action Buttons Utama di Halaman Utama (Gradient Blue/Cyan) */
    div.stAppViewContainer div.stButton > button { 
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1rem !important;
        border-radius: 8px; 
        background: linear-gradient(135deg, #00f0ff 0%, #3b82f6 100%) !important;
        color: #040814 !important; 
        border: none !important; 
        padding: 12px 24px;
        box-shadow: none !important;
    }
    div.stAppViewContainer div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.4) !important;
        color: #040814 !important;
    }
    
    /* Success Lock Box */
    .paywall-success-box {
        background: #06151b !important;
        border: 2px solid #10b981 !important;
        color: #34d399 !important;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# PERSISTENSI MEMORI SLOT
state_vars = {
    'my_private_key_pem': None,
    'my_public_key_pem': None,
    'last_ciphertext_hex': "",
    'extracted_ciphertext_hex': "",
    'final_decrypted_text': "",
    'locked_paywall_img_bytes': None,
    'paywall_license_key': "",
    'unlocked_clean_image': None,
    'inp_friend_pub': "",
    'inp_raw_msg': "",
    'inp_my_priv_key': "",
    'inp_designer_pub': "",
    'inp_license_owner': "Ahmad Ramadhan - Admin ID #9912",
    'inp_c_shift': 5,
    'inp_v_key': "CREATOR",
    'inp_buyer_priv': "",
    'inp_activation_code': ""
}
for var, default in state_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default

# ==============================================================================
# SIDEBAR - MENU UTAMA CONTRASTED
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>⚡ STUDENT MESSAGING</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #6b7280; margin-top: 0;'>UAS Kriptografi & Steganografi</p>", unsafe_allow_html=True)
    st.write("---")
    
    # 🔴 DI SINI DIUBAH MENJADI MODE SIMPLE & TO THE POINT
    menu = st.radio("PILIH MODUL OPERASIONAL:", [
        "📡 Pembuatan Kunci RSA", 
        "💬 Kirim Pesan Rahasia", 
        "🖼️ Premium Design Paywall"
    ])
    st.write("---")
    
    if st.button("🚨 System Hard Flush"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# MENU 1: GENERATE KEYPAIR RSA
# ==============================================================================
# 🔴 String di bawah ini harus sama persis dengan yang ada di st.radio atas!
if menu == "📡 Pembuatan Kunci RSA":
    st.markdown("<h2>📡 RSA Encryption</h2>", unsafe_allow_html=True)
    st.write("Inisialisasi sertifikat parameter gembok internal RSA 2048-bit Anda di sini.")
    
    if st.button("PRODUKSI ASYMMETRIC KEYPAIR"):
        priv, pub = cm.robust_generate_rsa_keys()
        if priv and pub:
            st.session_state['my_private_key_pem'] = priv
            st.session_state['my_public_key_pem'] = pub
            st.success("✔ Kunci RSA Berhasil Dibuat!")
            
    if st.session_state['my_public_key_pem']:
        col_pub, col_priv = st.columns(2)
        with col_pub:
            st.markdown("🔒 **Public Key (Gembok - Berikan ke Teman/Pembeli):**")
            st.code(st.session_state['my_public_key_pem'], language="markdown")
        with col_priv:
            st.markdown("🔑 **Private Key (Kunci Inti Rahasia - Jangan Disebar):**")
            st.code(st.session_state['my_private_key_pem'], language="markdown")

# ==============================================================================
# MENU 2: STEGANOGRAFI LSB
# ==============================================================================
# 🔴 String di bawah ini harus sama persis dengan yang ada di st.radio atas!
elif menu == "💬 Kirim Pesan Rahasia":
    st.markdown("<h2>💬 Kirim Pesan Rahasia</h2>", unsafe_allow_html=True)
    st.write("Gunakan menu ini untuk bertukar pesan teks rahasia via LSB gambar konvensional dengan laptop teman Anda.")
    
    tab_sender, tab_receiver = st.tabs(["📤 Node Pengirim (Sender)", "📥 Node Penerima (Receiver)"])
    
    with tab_sender:
        friend_pub_input = st.text_area("Masukkan Kunci Publik (Public Key) Teman Anda:", value=st.session_state['inp_friend_pub'], placeholder="-----BEGIN PUBLIC KEY-----", key="msg_friend_pub")
        st.session_state['inp_friend_pub'] = friend_pub_input
        
        raw_message_input = st.text_area("Tulis Pesan Rahasia yang Ingin Dikirim:", value=st.session_state['inp_raw_msg'], key="msg_raw")
        st.session_state['inp_raw_msg'] = raw_message_input
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            stego_variant = st.selectbox("Metode Pemindaian Koordinat Piksel:", ["Sequential", "Random"])
            random_seed_input = st.text_input("Kunci Sandi Scanner (Hanya Mode Random):", type="password") if stego_variant == "Random" else None
            carrier_file = st.file_uploader("Upload Gambar Induk Utama (.png Cover):", type=["png"], key="msg_file_uploader")
            
        with col_s2:
            if carrier_file and st.button("EMBED SECRET MESSAGE INTO IMAGE"):
                if not friend_pub_input or not raw_message_input:
                    st.error("Gagal: Parameter kunci publik dan pesan teks wajib diisi!")
                else:
                    ciphertext_hex, ok_rsa = cm.robust_rsa_encrypt(raw_message_input, friend_pub_input)
                    if not ok_rsa:
                        st.error(ciphertext_hex)
                    else:
                        st.session_state['last_ciphertext_hex'] = ciphertext_hex
                        pil_img = Image.open(carrier_file).convert("RGB")
                        img_matrix = np.array(pil_img, dtype=np.uint8)
                        
                        stego_result, err_stego = sm.lsb_encrypt(img_matrix, ciphertext_hex, variant=stego_variant, seed=random_seed_input)
                        if err_stego:
                            st.error(err_stego)
                        else:
                            st.success("🎯 Pesan terenkripsi berhasil disisipkan secara halus!")
                            fig = sm.plot_advanced_forensics(img_matrix, stego_result.astype(np.uint8), stego_variant)
                            st.pyplot(fig)
                            
                            buf = io.BytesIO()
                            Image.fromarray(stego_result.astype(np.uint8)).save(buf, format="PNG", compress_level=0)
                            st.download_button("💾 UNDUH GAMBAR STEGO (.png)", data=buf.getvalue(), file_name="stego_safe_output.png", mime="image/png")

    with tab_receiver:
        my_private_key_input = st.text_area("Masukkan Kunci Privat (Private Key) Milik Anda:", value=st.session_state['inp_my_priv_key'], key="msg_my_priv")
        st.session_state['inp_my_priv_key'] = my_private_key_input
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            stego_variant_rx = st.selectbox("Metode Pemindaian Piksel Gambar:", ["Sequential", "Random"], key="rx_scan")
            random_seed_rx = st.text_input("Kunci Sandi Scanner:", type="password", key="rx_seed") if stego_variant_rx == "Random" else None
            stego_file = st.file_uploader("Upload Gambar Hasil Ekstraksi (.png Stego):", type=["png"], key="rx_file")
            
        with col_r2:
            if stego_file and st.button("EKSTRAK DAN DEKRIPSI KONTEN"):
                if not my_private_key_input:
                    st.error("Gagal: Dekripsi membutuhkan private kunci pengaman!")
                else:
                    pil_stego = Image.open(stego_file).convert("RGB")
                    stego_matrix_rx = np.array(pil_stego, dtype=np.uint8)
                    
                    clean_ciphertext, ok_lsb = sm.lsb_extract(stego_matrix_rx, variant=stego_variant_rx, seed=random_seed_rx)
                    if not ok_lsb:
                        st.error(clean_ciphertext)
                    else:
                        st.session_state['extracted_ciphertext_hex'] = clean_ciphertext
                        decryption_result, ok_rsa = cm.robust_rsa_decrypt(clean_ciphertext, my_private_key_input)
                        
                        if not ok_rsa:
                            st.error(decryption_result)
                        else:
                            st.session_state['final_decrypted_text'] = decryption_result
                            st.balloons()
                            st.success("Proses ekstraksi berhasil diselesaikan!")
                            
        if st.session_state['final_decrypted_text']:
            st.markdown(f"<div class='paywall-success-box'>🔓 DATA HASIL DEKRIPSI UTAMA: <h2>{st.session_state['final_decrypted_text']}</h2></div>", unsafe_allow_html=True)

# ==============================================================================
# MENU 3: PREMIUM DESIGN PAYWALL
# ==============================================================================
# 🔴 String di bawah ini harus sama persis dengan yang ada di st.radio atas!
elif menu == "🖼️ Premium Design Paywall":
    st.markdown("<h2>🖼️ Premium Design Paywall</h2>", unsafe_allow_html=True)
    st.write("Studi Kasus Mandiri: Mengunci karya desain original dengan Watermark Fisik Elegan, dan hanya bisa dihapus otomatis via verifikasi Lisensi Transaksi RSA.")
    
    pay_tab1, pay_tab2 = st.tabs(["🎨 Sisi Desainer (Kunci Karya)", "💰 Sisi Pembeli/Dosen (Beli & Bersihkan)"])
    
    with pay_tab1:
        st.markdown("### 🔐 Pasang Segel Watermark Hak Cipta Komersial")
        designer_pub = st.text_area("Masukkan Kunci Publik (Public Key) Pembeli/Dosen Anda:", value=st.session_state['inp_designer_pub'], placeholder="-----BEGIN PUBLIC KEY-----", key="wt_designer_pub")
        st.session_state['inp_designer_pub'] = designer_pub
        
        license_owner = st.text_input("Nama Lisensi Pemilik Karya / Desainer:", value=st.session_state['inp_license_owner'], key="wt_license_owner")
        st.session_state['inp_license_owner'] = license_owner
        
        c_shift_pay = st.number_input("Matriks Delta Caesar (Shift Value) Lisensi:", min_value=0, max_value=25, value=st.session_state['inp_c_shift'], key="wt_c_shift")
        st.session_state['inp_c_shift'] = c_shift_pay
        
        v_key_pay = st.text_input("Kata Kunci Vigenere Lisensi:", value=st.session_state['inp_v_key'], key="wt_v_key")
        st.session_state['inp_v_key'] = v_key_pay
        
        uploaded_design = st.file_uploader("Upload File Gambar Desain Asli Anda (PNG atau JPG):", type=["png", "jpg", "jpeg"], key="wt_file_uploader")
        
        if uploaded_design and st.button("🔥 EMBED VISIBLE WATERMARK & LOCK DESIGN"):
            if not designer_pub or not license_owner:
                st.error("Gagal: Mohon cantumkan Kunci Publik dan Identitas Nama Pemilik Lisensi!")
            else:
                combined_license_text = f"LICENSE_VALID:{license_owner}:SHIFT={c_shift_pay}:KEY={v_key_pay}"
                ciphertext_license, ok_rsa = cm.robust_rsa_encrypt(combined_license_text, designer_pub)
                
                if ok_rsa:
                    st.session_state['paywall_license_key'] = ciphertext_license
                    
                    base_img = Image.open(uploaded_design).convert("RGBA")
                    width, height = base_img.size
                    
                    txt_img = Image.new("RGBA", (int(width*1.5), int(height*1.5)), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(txt_img)
                    
                    font_size = int(min(width, height) / 16)
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except IOError:
                        font = ImageFont.load_default()
                    
                    text_wm = f"🔒 PROPERTY OF {license_owner.upper()} - LICENSE REQUIRED   "
                    
                    for y in range(0, int(height * 1.5), font_size * 3):
                        for x in range(0, int(width * 1.5), len(text_wm) * 8):
                            draw.text((x, y), text_wm, fill=(255, 255, 255, 65), font=font)
                            draw.text((x+1, y+1), text_wm, fill=(255, 255, 255, 65), font=font)
                    
                    rotated_txt = txt_img.rotate(25, resample=Image.BICUBIC)
                    
                    crop_x = int((rotated_txt.width - width) / 2)
                    crop_y = int((rotated_txt.height - height) / 2)
                    final_txt_layer = rotated_txt.crop((crop_x, crop_y, crop_x + width, crop_y + height))
                    
                    locked_image = Image.alpha_composite(base_img, final_txt_layer).convert("RGB")
                    
                    img_byte_arr = io.BytesIO()
                    locked_image.save(img_byte_arr, format='PNG')
                    st.session_state['locked_paywall_img_bytes'] = img_byte_arr.getvalue()
                    st.session_state['unlocked_clean_image'] = base_img.convert("RGB")
                    
                    st.success("✔ Karya Desain Anda Berhasil Disegel dengan Watermark Fisik yang Jelas!")

        if st.session_state['locked_paywall_img_bytes'] is not None:
            col_view1, col_view2 = st.columns(2)
            with col_view1:
                st.image(st.session_state['locked_paywall_img_bytes'], caption="Visual Gambar Terkunci", use_container_width=True)
            with col_view2:
                st.markdown("🔒 **Kode Kunci Aktivasi Lisensi Transaksi (Kirim ke Pembeli):**")
                st.code(st.session_state['paywall_license_key'], language="markdown")
                st.download_button("💾 UNDUH DESAIN BER-WATERMARK (.png)", data=st.session_state['locked_paywall_img_bytes'], file_name="design_secured.png", mime="image/png")

    with pay_tab2:
        st.markdown("### 💰 Ruang Simulasi Transaksi Pembayaran Pembeli")
        st.write("Di sini, Dosen/Pembeli memasukkan Gambar Ber-Watermark tipis beserta Kunci Privat miliknya sebagai bukti 'pembayaran' lisensi.")
        
        buyer_private_key = st.text_area("Masukkan Kunci Privat (Private Key) Pembeli untuk Transaksi:", value=st.session_state['inp_buyer_priv'], key="wt_buyer_priv")
        st.session_state['inp_buyer_priv'] = buyer_private_key
        
        input_license_key = st.text_area("Masukkan Kode Kunci Aktivasi Lisensi Transaksi dari Desainer:", value=st.session_state['inp_activation_code'], key="wt_activation_code")
        st.session_state['inp_activation_code'] = input_license_key
        
        target_locked_file = st.file_uploader("Upload Gambar Desain yang Ber-Watermark (.png atau .jpg):", type=["png", "jpg", "jpeg"], key="wt_verify_uploader")
        
        if target_locked_file and st.button("🔓 VERIFIKASI PEMBAYARAN & BERSIHKAN WATERMARK"):
            if not buyer_private_key or not input_license_key:
                st.error("Gagal: Isian kunci privat pembeli dan kode aktivasi wajib diisi untuk verifikasi!")
            else:
                decrypted_license, ok_dec = cm.robust_rsa_decrypt(input_license_key, buyer_private_key)
                
                if ok_dec and "LICENSE_VALID" in decrypted_license:
                    parts = decrypted_license.split(":")
                    license_name = parts[1]
                    
                    st.balloons()
                    st.success("🟢 VERIFIKASI SUKSES: Hak cipta tervalidasi penuh.")
                    st.session_state['verify_success'] = True
                    st.session_state['verify_name'] = license_name
                else:
                    st.error("🔴 TRANSAKSI GAGAL: Kunci Lisensi Salah atau Private Key Anda tidak cocok untuk membeli karya ini!")
                    st.session_state['verify_success'] = False

        if st.session_state.get('verify_success', False):
            st.markdown(f"""
                <div class="paywall-success-box">
                    <h3 style='margin:0;'>🟢 LISENSI DIGITAL BERHASIL DITEBUS</h3>
                    <p style='color: #e2e8f0; margin:5px 0 0 0;'>Pemilik Lisensi Resmi: <b>{st.session_state['verify_name']}</b></p>
                    <p style='font-size:0.85rem; margin:0;'>Sistem membersihkan proteksi fisik secara real-time.</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.session_state['unlocked_clean_image'] is not None:
                st.image(st.session_state['unlocked_clean_image'], caption="✔ GAMBAR ORIGINAL TANPA WATERMARK SELESAI DIPULIHKAN!", use_container_width=True)
                
                clean_buf = io.BytesIO()
                st.session_state['unlocked_clean_image'].save(clean_buf, format="PNG")
                st.download_button("💾 UNDUH FILE GAMBAR BERSIH (.png)", data=clean_buf.getvalue(), file_name="design_master_clean.png", mime="image/png", key="download_clean_btn")