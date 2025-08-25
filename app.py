import streamlit as st
from datetime import datetime
from PIL import Image
import base64
import os

# === CSS background gradasi biru-pink dan hilangkan sidebar ===
page_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to right, #87CEFA, #FFB6C1);
    }
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# === Baca file logo dari folder project (pakai relative path) ===
with open("logo2.png", "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

# === Header di pojok kiri atas (tanpa container, transparan) ===
st.markdown(
    f"""
    <style>
        .header-left {{
            position: fixed;
            top: 5px;
            left: 10px;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 999;
        }}
        .header-left img {{
            height: 60px;     /* <– ukuran logo diperbesar */
        }}
        .header-left .title {{
            font-size: 15px;
            font-weight: bold;
            color: black;
            margin: 0;
            padding: 0;
        }}
        .header-left .subtitle {{
            font-size: 10px;
            color: black;
            margin: 0;
            padding: 0;
        }}
    </style>

    <div class="header-left">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo" />
        <div>
            <p class="title">Sistem Informasi Validasi Data Permohonan Bantuan</p>
            <p class="subtitle">Dinas Kelautan dan Perikanan Provinsi NTB 🐬</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    
    <h3 style='text-align: center; color: Black;'>
        🐳Dinas Kelautan dan Perikanan Provinsi NTB🐳
    </h3>
    """,
    unsafe_allow_html=True
)

# === Inisialisasi session_state untuk halaman ===
if "page" not in st.session_state:
    st.session_state.page = "Halaman Utama"

# === Dropdown navigasi ===
menu = st.selectbox(
    "Pilih Halaman Sistem Informasi 🦑:",
    ["Halaman Utama", "Input Pemohon Baru", "Validasi Data Penerima Bantuan"],
    index=["Halaman Utama", "Input Pemohon Baru", "Validasi Data Penerima Bantuan"].index(st.session_state.page)
)

# Update halaman aktif sesuai pilihan user
st.session_state.page = menu

# === Konten Halaman Utama ===
if st.session_state.page == "Halaman Utama":
    st.markdown(
        """
        <div style='text-align: center; color: #0B1D51; font-size: 15px;'>
        Selamat datang di Sistem Informasi Validasi Data Penerima Bantuan<br>
        Gunakan menu di atas untuk memilih halaman yang diinginkan
        </div>
        """,
        unsafe_allow_html=True
    )

    # === Footer hanya untuk Halaman Utama ===
    tanggal_sekarang = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
    footer = f"""
        <style>
            .footer {{
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background: rgba(255, 255, 255, 0.95);
                color: #1B263B;
                padding: 8px 20px;
                font-size: 14px;
                border-top: 2px solid #ccc;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: Arial, sans-serif;
            }}
            .footer img {{
                height: 36px;
                vertical-align: middle;
                margin: 0 5px;
            }}
            .footer span {{
                font-weight: bold;
                color: #1B263B;
            }}
            .footer .date {{
                font-weight: bold;
                color: #1B263B;
            }}
        </style>
        <div class="footer">
            <div class="left date">{tanggal_sekarang}</div>
            <div class="right">
                <img src="https://logodix.com/logo/1227700.png" alt="Logo Provinsi NTB">
                <span> | Dinas Kelautan dan Perikanan Provinsi NTB</span>
            </div>
        </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

# === Konten Halaman Input Pemohon Baru ===
elif st.session_state.page == "Input Pemohon Baru":
    try:
        import pages.inputpemohonbaru as ipb
        if hasattr(ipb, "main"):
            ipb.main()
        else:
            st.warning("Fungsi main() belum dibuat di inputpemohonbaru.py")
    except Exception as e:
        st.error(f"Halaman Input Pemohon Baru error: {type(e).__name__} - {e}")

# === Konten Halaman Validasi Data Penerima Bantuan ===
elif st.session_state.page == "Validasi Data Penerima Bantuan":
    try:
        import pages.validasidata as vd
        if hasattr(vd, "main"):
            vd.main()
        else:
            st.warning("Fungsi main() belum dibuat di validasidata.py")
    except Exception as e:
        st.error(f"Halaman Validasi Data error: {type(e).__name__} - {e}")


