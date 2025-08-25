import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === KONFIGURASI GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)

SHEET_ID = "1Q8rDR0o50K7uH4peO_W49UKoHeL1VgGgKxUwGauV3CY"
sheet = client.open_by_key(SHEET_ID).sheet1

columns_order = [
    "No", "Tgl Entry", "NIK", "No KK", "Nama", "Alamat", "Kab/Kota Penerima",
    "Pekerjaan", "Status Kelompok", "Jabatan dalam Kelompok", "Nama Kelompok",
    "Jenis Bantuan", "Jumlah Bantuan", "Satuan", "Nilai Bantuan Berupa Rupiah",
    "Sumber Dana", "Program/Kegiatan/Sub Kegiatan", "Tahun Penerimaan", "Keterangan",
    "Status", "Status Duplicate"
]

def save_data(df):
    for col in columns_order:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("").astype(str)
    df = df[columns_order]
    try:
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")

def load_data():
    try:
        data_sheet = sheet.get_all_records()
        df_sheet = pd.DataFrame(data_sheet)
        if df_sheet.empty:
            df_sheet = pd.DataFrame(columns=columns_order)
    except Exception as e:
        st.warning(f"Gagal membaca Google Sheets: {e}")
        df_sheet = pd.DataFrame(columns=columns_order)

    df_sheet.rename(columns=lambda x: x.strip(), inplace=True)
    for col in columns_order:
        if col not in df_sheet.columns:
            df_sheet[col] = ""

    df_clean = df_sheet.drop_duplicates(subset=["NIK", "Nama"], keep="first").reset_index(drop=True)

    if not df_clean.equals(df_sheet):
        save_data(df_clean)

    return df_clean

def prediksi_status(tahun_input):
    try:
        tahun_input = int(tahun_input)
    except:
        tahun_input = datetime.now().year
    tahun_sekarang = datetime.now().year
    selisih = tahun_sekarang - tahun_input
    if selisih >= 2:
        return ("Layak", f"Sudah lebih dari {selisih} tahun sejak {tahun_input}")
    else:
        return ("Tidak Layak", f"Baru {selisih} tahun sejak {tahun_input}")

def main():
    df = load_data()

    if "form_data" not in st.session_state:
        st.session_state.form_data = {col: "" for col in columns_order}
    if "show_data" not in st.session_state:
        st.session_state.show_data = False
    if "has_predicted" not in st.session_state:
        st.session_state.has_predicted = False

    def safe_int_from_state(key, default):
        val = st.session_state.form_data.get(key, "")
        try:
            return int(val)
        except:
            return default

    default_year = safe_int_from_state("Tahun Penerimaan", datetime.today().year)
    default_jumlah = safe_int_from_state("Jumlah Bantuan", 0)
    default_rupiah = safe_int_from_state("Bantuan Berupa Rupiah", 0)
    default_nik = safe_int_from_state("NIK", 0)
    default_kk = safe_int_from_state("No KK", 0)

    with st.form("form_validasi_data"):
        st.markdown("### 📝 Form Data Penerima Bantuan")

        try:
            tgl_entry = st.date_input(
                "Tanggal Entry",
                value=datetime.strptime(
                    st.session_state.form_data.get("Tgl Entry", datetime.today().strftime("%Y-%m-%d")),
                    "%Y-%m-%d"
                )
                if st.session_state.form_data.get("Tgl Entry") else datetime.today()
            )
        except:
            tgl_entry = datetime.today()

        col1, col2 = st.columns(2)
        with col1:

            # NIK dan No KK sebagai teks, tetap bisa input angka panjang
            nik = st.text_input("NIK", value=str(st.session_state.form_data.get("NIK", "")))
            no_kk = st.text_input("No KK", value=str(st.session_state.form_data.get("No KK", "")))


            nama = st.text_input("Nama", value=st.session_state.form_data.get("Nama", ""))
            alamat = st.text_input("Alamat", value=st.session_state.form_data.get("Alamat", ""))
            pekerjaan = st.text_input("Pekerjaan", value=st.session_state.form_data.get("Pekerjaan", ""))
            status_kelompok = st.selectbox("Status Kelompok", ["Individu", "Kelompok"],
                                    index=0 if st.session_state.form_data.get("Status Kelompok") != "Kelompok" else 1)
            nama_kelompok = st.text_input("Nama Kelompok", value=st.session_state.form_data.get("Nama Kelompok", ""))
            jabatan_dalam_kelompok = st.selectbox(
                                "Jabatan dalam Kelompok",
                                ["Ketua Kelompok", "Wakil", "Bendahara", "Sekretaris", "Anggota"],
                                index=0 if st.session_state.form_data.get("Jabatan dalam Kelompok", "") == "" else
                                ["Ketua Kelompok", "Wakil", "Bendahara", "Sekretaris", "Anggota"].index(
                                    st.session_state.form_data.get("Jabatan dalam Kelompok", "Ketua Kelompok")))

        with col2:
            jenis_bantuan = st.text_input("Jenis Bantuan", value=st.session_state.form_data.get("Jenis Bantuan", ""))
            jumlah_bantuan = st.number_input("Jumlah Bantuan", min_value=0, value=default_jumlah, step=1)
            satuan = st.text_input("Satuan", value=st.session_state.form_data.get("Satuan", ""))
            rupiah = st.number_input("Nilai Bantuan Berupa Rupiah", min_value=0, value=default_rupiah, step=1000)
            sumber_options = ["APBN", "POKIR", "DPA Prov. NTB"]
            sumber_dana = st.selectbox("Sumber Dana",options=sumber_options,
                                index=sumber_options.index(st.session_state.form_data.get("Sumber Dana", "APBN"))
                                if st.session_state.form_data.get("Sumber Dana", "APBN") in sumber_options else 0
            )
            bidang_pemberi = st.text_input("Program/Kegiatan/Sub Kegiatan", value=st.session_state.form_data.get("Program/Kegiatan/Sub Kegiatan", ""))
            tahun = st.number_input("Tahun Penerimaan", min_value=2000, max_value=2100, value=default_year, step=1)
            keterangan = st.text_input("Keterangan", value=st.session_state.form_data.get("Keterangan", ""))
            kabkota = st.text_input("Kab/Kota Penerima", value=st.session_state.form_data.get("Kab/Kota Penerima", ""))

        colA, colB, colC, colD = st.columns(4)
        simpan = colA.form_submit_button("📂 Simpan")
        prediksi = colB.form_submit_button("🔍 Prediksi")
        edit = colC.form_submit_button("✏ Edit")
        tampil = colD.form_submit_button("📊 Tampilkan Data")

    # ====== AKSI TOMBOL ======
    if prediksi:
        if df.empty:
            st.warning("⚠ Data Google Sheets kosong. Tidak ada yang bisa diprediksi.")
        else:
            df_safe = df.fillna("").astype(str).copy()
            for c in ["NIK", "Nama", "Tahun Penerimaan"]:
                if c not in df_safe.columns:
                    df_safe[c] = ""
        mask = (
                (df_safe["NIK"].str.strip() == nik.strip()) |
                (df_safe["Nama"].str.strip().str.lower() == nama.strip().lower())
            )
        data_ada = df_safe[mask]
        if not data_ada.empty:
            status = data_ada.iloc[0].get("Status", "")
            ket = data_ada.iloc[0].get("Keterangan", "")
            st.success(f"*Status:* {status}\n\n*Keterangan:* {ket}")
            
            st.markdown("### 📄 Data Lengkap dari Google Sheets")
            cols_show = [c for c in columns_order if c in data_ada.columns]
            st.dataframe(data_ada[cols_show])
            
            for col in columns_order:
                    if col in data_ada.columns:
                        st.session_state.form_data[col] = str(data_ada.iloc[0][col])
        else:
            st.warning("⚠ NIK tidak ditemukan.")


    if simpan:
        existing_niks = df['NIK'].astype(str).str.strip().values
        if str(nik).strip() in existing_niks:
            st.warning("⚠ NIK sudah ada di data. Gunakan tombol Edit untuk memperbarui.")
        else:
            nomor_berikutnya = len(df) + 1
            status, ket = prediksi_status(tahun)
            new_row = {
                "No": nomor_berikutnya,
                "Tgl Entry": tgl_entry.strftime('%Y-%m-%d'),
                "NIK": str(nik),
                "No KK": str(no_kk),
                "Nama": nama.strip(),
                "Alamat": alamat,
                "Kab/Kota Penerima": kabkota,
                "Pekerjaan": pekerjaan,
                "Status Kelompok": status_kelompok,
                "Jabatan dalam Kelompok": jabatan_dalam_kelompok,
                "Nama Kelompok": nama_kelompok,
                "Jenis Bantuan": jenis_bantuan,
                "Jumlah Bantuan": int(jumlah_bantuan),
                "Satuan": satuan,
                "Bantuan Berupa Rupiah": int(rupiah),
                "Sumber Dana": sumber_dana,
                "Bidang Pemberi Bantuan": bidang_pemberi,
                "Tahun Penerimaan": int(tahun),
                "Keterangan": keterangan or ket,
                "Status": status,
                "Status Duplicate": "Tidak Duplicate"
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.session_state.form_data = {col: "" for col in columns_order}
            st.success("✅ Data berhasil disimpan ke Google Sheets!")
            st.rerun()

    if edit:
        mask_edit = df['NIK'].astype(str).str.strip() == str(nik).strip()
        existing_niks = df['NIK'].astype(str).str.strip().values
        if mask_edit.any():
            idx = df[mask_edit].index[0]
            df.at[idx, "Tgl Entry"] = tgl_entry.strftime('%Y-%m-%d')
            df.at[idx, "NIK"] = str(nik)
            df.at[idx, "No KK"] = str(no_kk)
            df.at[idx, "Nama"] = nama
            df.at[idx, "Alamat"] = alamat
            df.at[idx, "Kab/Kota Penerima"] = kabkota
            df.at[idx, "Pekerjaan"] = pekerjaan
            df.at[idx, "Status Kelompok"] = status_kelompok
            df.at[idx, "Jabatan dalam Kelompok"] = jabatan_dalam_kelompok
            df.at[idx, "Nama Kelompok"] = nama_kelompok
            df.at[idx, "Jenis Bantuan"] = jenis_bantuan
            df.at[idx, "Jumlah Bantuan"] = int(jumlah_bantuan)
            df.at[idx, "Satuan"] = satuan
            df.at[idx, "Bantuan Berupa Rupiah"] = int(rupiah)
            df.at[idx, "Sumber Dana"] = sumber_dana
            df.at[idx, "Bidang Pemberi Bantuan"] = bidang_pemberi
            df.at[idx, "Tahun Penerimaan"] = int(tahun)
            df.at[idx, "Keterangan"] = keterangan
            status, ket = prediksi_status(tahun)
            df.at[idx, "Status"] = status
            df.at[idx, "Status Duplicate"] = "Duplicate" if str(nik).strip() in df['NIK'].astype(str).str.strip().values else "Tidak Duplicate"
            save_data(df)
            st.session_state.form_data = {col: "" for col in columns_order}
            st.success("✏ Data berhasil diperbarui!")
            st.rerun()
        else:
            st.warning("⚠ NIK tidak ditemukan.")

    if tampil:
        df_sheet = load_data()
        st.markdown("### 📋 Data Monitoring Penerima Bantuan")
        st.dataframe(df_sheet)

if __name__ == "__main__":
    main()


