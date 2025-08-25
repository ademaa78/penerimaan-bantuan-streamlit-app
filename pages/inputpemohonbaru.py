import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

def main():
    st.title("📝 Form Input Pemohon Baru")
    
    SHEET_NAME = "1Q8rDR0o50K7uH4peO_W49UKoHeL1VgGgKxUwGauV3CY"
    WORKSHEET_NAME = "Sheet2"
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_NAME).worksheet(WORKSHEET_NAME)

    # Load data Sheet2
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame(columns=[
            "Tgl Entry", "NIK pemohon", "No KK", "Nama pemohon", "Alamat",
            "Kab/Kota", "Pekerjaan", "Status Kelompok", "Jabatan dalam Kelompok", "Nama Kelompok",
            "Jenis Bantuan", "Jumlah Bantuan", "Satuan", "Nilai Bantuan Berupa Rupiah", "Sumber Dana", "Program/Kegiatan/Sub Kegiatan",
            "Tahun Pengajuan", "Keterangan", "Status Pemohon"
        ])
        
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    if "row_index" not in st.session_state:
        st.session_state.row_index = None
    
    def to_str(val):
        return val.strftime("%Y-%m-%d") if isinstance(val, (datetime, date)) else val

    def safe_int_from_state(key, default):
        val = st.session_state.form_data.get(key, "")
        try:
            return int(val)
        except:
            return default

    # Baru panggil fungsi safe_int_from_state
    default_year = safe_int_from_state("Tahun Pengajuan", datetime.today().year)
    default_jumlah = safe_int_from_state("Jumlah Bantuan", 0)
    default_rupiah = safe_int_from_state("Nilai Bantuan Berupa Rupiah", 0)



    # --- Form Input ---
    with st.form("form_pemohon_baru", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            default_tgl_entry = st.session_state.form_data.get("tgl_entry", date.today())
            tgl_entry = st.date_input("Tgl Entry", value=default_tgl_entry)
            tgl_entry_str = tgl_entry.strftime("%Y-%m-%d")
            
            nik = st.text_input("NIK Pemohon", value=st.session_state.form_data.get("nik", ""))
            no_kk = st.text_input("No KK Pemohon", value=st.session_state.form_data.get("no_kk", ""))
            nama = st.text_input("Nama Pemohon", value=st.session_state.form_data.get("nama", ""))
            alamat = st.text_area("Alamat Pemohon", value=st.session_state.form_data.get("alamat", ""), height=40)
            kab_kota = st.text_input("Kab/Kota Pemohon", value=st.session_state.form_data.get("kab_kota", ""))
            pekerjaan = st.text_input("Pekerjaan", value=st.session_state.form_data.get("pekerjaan", ""))
            status_kelompok = st.selectbox("Status Kelompok", ["Individu", "Berkelompok"], 
                                index=0 if st.session_state.form_data.get("status_kelompok") is None else
                                ["Individu","Berkelompok"].index(st.session_state.form_data["status_kelompok"]))
            jabatan_dalam_kelompok = st.selectbox("Jabatan dalam Kelompok", ["Anggota", "Ketua Kelompok", "Wakil Ketua", "Sekretaris", "Bendahara"], 
                                index=0 if st.session_state.form_data.get("jabatan") is None else
                                ["Anggota", "Ketua Kelompok", "Wakil Ketua", "Sekretaris", "Bendahara"].index(st.session_state.form_data["jabatan"]))

        with col2:
            nama_kelompok = st.text_input("Nama Kelompok", value=st.session_state.form_data.get("nama_kelompok", ""))
            jenis_bantuan = st.text_input("Jenis Bantuan", value=st.session_state.form_data.get("jenis_bantuan", ""))
            jumlah_bantuan = st.number_input("Jumlah Bantuan", min_value=0, value=int(st.session_state.form_data.get("jumlah", 0)))
            satuan = st.text_input("Satuan", value=st.session_state.form_data.get("satuan", ""))
            default_rupiah = int(st.session_state.form_data.get("rupiah", 0))
            rupiah = st.number_input("Nilai Bantuan Berupa Rupiah", min_value=0, value=default_rupiah, step=1000)
            
            sumber_options = ["APBN", "POKIR", "DPA Prov. NTB"]
            sumber_dana = st.selectbox("Sumber Dana",options=sumber_options,
                                index=sumber_options.index(st.session_state.form_data.get("Sumber Dana", "APBN"))
                                if st.session_state.form_data.get("Sumber Dana", "APBN") in sumber_options else 0
            )
            bidang_pemberi = st.text_input("Program/Kegiatan/Sub Kegiatan", value=st.session_state.form_data.get("Program/Kegiatan/Sub Kegiatan", ""))
            tahun = st.number_input(
                "Tahun Pengajuan",
                step=1,
                value=int(st.session_state.form_data.get("tahun", datetime.now().year))
            )
            keterangan = st.text_input("Keterangan", value=st.session_state.form_data.get("keterangan", ""))
            status_pemohon = st.selectbox("Status Pemohon", ["Disetujui", "Ditolak", "Proses"],
                                    index=0 if st.session_state.form_data.get("status_pemohon") is None else
                                    ["Disetujui", "Ditolak", "Proses"].index(st.session_state.form_data["status_pemohon"]))

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            simpan = st.form_submit_button("💾 Simpan")
        with col_btn2:
            edit = st.form_submit_button("✏ Cari & Edit")
        with col_btn3:
            hapus = st.form_submit_button("🗑 Hapus")

    pilihan_tampil = st.radio("Pilih Data yang Ingin Ditampilkan:", ["📋 Data Permohonan Bantuan", "✅ Data Pemohon Bantuan yang Disetujui"])


    # --- Simpan Data ---
    if simpan:
        next_no = len(df) + 1
        row_data = [
            next_no, tgl_entry_str, nik, no_kk, nama, alamat, kab_kota, pekerjaan,
            status_kelompok, jabatan_dalam_kelompok, nama_kelompok, jenis_bantuan, jumlah_bantuan, satuan,
            rupiah, sumber_dana, bidang_pemberi, tahun, keterangan, status_pemohon
        ]

        
        row_data = [to_str(v) for v in row_data]
        sheet.append_row(row_data)
        st.success("✅ Data berhasil disimpan!")
        st.session_state.form_data = {}

    # --- Edit Data ---
    if edit:
        if not nik:
            st.warning("⚠ Masukkan NIK untuk edit!")
        else:
            try:
                cell = sheet.find(nik)
                if cell:
                    row_index = cell.row
                    data_lama = sheet.row_values(row_index)
                    st.session_state.form_data = {
                        "row_index": row_index,
                        "tgl_entry": data_lama[1],
                        "nik": data_lama[2],
                        "no_kk": data_lama[3],
                        "nama": data_lama[4],
                        "alamat": data_lama[5],
                        "kab_kota": data_lama[6],
                        "pekerjaan": data_lama[7],
                        "status_kelompok": data_lama[8],
                        "jabatan": data_lama[9],
                        "nama_kelompok": data_lama[10],
                        "jenis_bantuan": data_lama[11],
                        "jumlah": int(data_lama[12]) if data_lama[12].isdigit() else 0,
                        "satuan": data_lama[13],
                        "rupiah": int(data_lama[14]) if data_lama[14].isdigit() else 0,
                        "sumber": data_lama[15],
                        "bidang": data_lama[16],
                        "tahun": int(data_lama[17]) if data_lama[17].isdigit() else datetime.datetime.now().year,
                        "keterangan": data_lama[18],
                        "status_pemohon": data_lama[19],
                    }
                    st.success(f"✏ Data NIK {nik} ditemukan, form sudah terisi. Ubah lalu klik Simpan/Update.")
                    st.rerun()
                else:
                    st.error("❌ NIK tidak ditemukan.")
            except Exception as e:
                st.error(f"Gagal mencari data: {e}")

    # --- Hapus Data ---
    if hapus:
        if not nik:
            st.warning("⚠ Masukkan NIK yang ingin dihapus!")
        else:
            try:
                cell = sheet.find(nik)
                if cell:
                    sheet.delete_rows(cell.row)
                    st.success(f"🗑 Data dengan NIK {nik} berhasil dihapus!")
                else:
                    st.error("❌ NIK tidak ditemukan.")
            except Exception as e:
                st.error(f"Gagal hapus data: {e}")

    # --- Tampilkan Data ---
    if pilihan_tampil == "📋 Data Permohonan Bantuan":
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("⚠ Tidak ada data permohonan bantuan.")

    elif pilihan_tampil == "✅ Data Pemohon Bantuan yang Disetujui":
        try:
            # Ambil data dari Sheet2
            sheet2 = client.open_by_key(SHEET_NAME).worksheet("Sheet2")
            data2 = sheet2.get_all_records()
            df2 = pd.DataFrame(data2)

            if not df2.empty:
                # Filter hanya yang disetujui
                df_disetujui = df2[df2["Status Pemohon"] == "Disetujui"].copy()

                # === Mapping kolom Sheet2 -> Sheet1 ===
                df_disetujui = df_disetujui.rename(columns={
                    "Tgl entry": "Tgl Entry",
                    "NIK Pemohon": "NIK",
                    "KK Pemohon": "No KK",
                    "Nama Pemohon": "Nama",
                    "Alamat Pemohon": "Alamat",
                    "Kab/Kota Pemohon": "Kab/Kota Penerima",
                    "Pekerjaan": "Pekerjaan",
                    "Status Kelompok": "Status Kelompok",
                    "Jabatan dalam Kelompok": "Jabatan dalam Kelompok",
                    "Nama Kelompok": "Nama Kelompok",
                    "Jenis Bantuan": "Jenis Bantuan",
                    "Jumlah Bantuan": "Jumlah Bantuan",
                    "Satuan": "Satuan",
                    "Bantuan Berupa Rupiah": "Bantuan Berupa Rupiah",
                    "Sumber Dana": "Sumber Dana",
                    "Bidang Pemberi Bantuan": "Bidang Pemberi Bantuan",
                    "Tahun Penerimaan": "Tahun Penerimaan",
                    "Tahun Pengajuan": "Tahun Pengajuan",
                    "Keterangan": "Keterangan",
                    "Status Pemohon": "Status Pemohon",
                    "Status": "Status",
                    "Status Duplicate": "Status Duplicate"
                })
                
                df_disetujui["Jabatan"] = df_disetujui["Jabatan dalam Kelompok"]
                df_disetujui["Tahun Penerimaan"] = df_disetujui["Tahun Pengajuan"]
                df_disetujui["Status"] = df_disetujui["Status Pemohon"]
                
                # === Definisi struktur kolom di Sheet1 ===
                kolom_sheet1 = [
                    "No", "Tgl Entry", "NIK", "No KK", "Nama", "Alamat",
                    "Kab/Kota Penerima", "Pekerjaan", "Status Kelompok", "Jabatan",
                    "Nama Kelompok", "Jenis Bantuan", "Jumlah Bantuan", "Satuan",
                    "Bantuan Berupa Rupiah", "Sumber Dana", "Bidang Pemberi Bantuan",
                    "Tahun Pengajuan", "Tahun Penerimaan", "Keterangan",
                    "Status Pemohon", "Status", "Status Duplicate"
                ]
                for col in kolom_sheet1:
                    if col not in df_disetujui.columns and col != "No":
                        df_disetujui[col] = ""
                
                
                # Tambah kolom default jika diperlukan
                if "Pekerjaan" not in df_disetujui.columns:
                    df_disetujui["Pekerjaan"] = "Nelayan"
                if "Status Kelompok" not in df_disetujui.columns:
                    df_disetujui["Status Kelompok"] = "Berkelompok"
                
                # Susun sesuai urutan Sheet1 (kecuali "No" karena nanti diisi otomatis)
                df_disetujui = df_disetujui[[c for c in kolom_sheet1 if c != "No"]]
                
                # Ambil data lama dari Sheet1
                sheet1 = client.open_by_key(SHEET_NAME).worksheet("Sheet1")
                data1 = sheet1.get_all_records()
                df1 = pd.DataFrame(data1)

                # Gabungkan data
                df_gabung = pd.concat([df1, df_disetujui], ignore_index=True)

                # Update nomor urut otomatis
                df_gabung["No"] = range(1, len(df_gabung) + 1)

                # 🔥 FIX: ganti NaN jadi string kosong
                df_gabung = df_gabung.fillna("")

                # Simpan kembali ke Sheet1
                sheet1.update([df_gabung.columns.values.tolist()] + df_gabung.values.tolist())

                st.success("✅ Data yang Disetujui berhasil disimpan ke Sheet1")
                st.dataframe(df_disetujui)

            else:
                st.warning("⚠ Tidak ada data di Sheet2")

        except Exception as e:
            st.error(f"Gagal mengambil data dari Sheet2: {e}")


if _name_ == "_main_":

    main()
