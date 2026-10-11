# ⚡ ADB Tools GUI (Android Device Manager & Utility Suite)

<p align="center">
  <img src="data/check.png" width="64" height="64" alt="ADB Tools GUI Logo">
  <br>
  <b>All-in-One Desktop Utility for Android Management, App Audit, Debloating, and Screen Mirroring</b>
  <br>
  <i>Dibangun dengan Python & PySide6 dengan antarmuka modern, responsif, dan kaya fitur.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Framework-PySide6-41CD52?logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/ADB%20Tools-Bundled-orange" alt="ADB Bundled">
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License">
</p>

---

## 🌟 Fitur Utama

### 1. 📱 Device Overview & Hardware Diagnostics
* **Spesifikasi Lengkap:** Brand, model, serial, versi Android, SDK level, build fingerprint, security patch, arsitektur CPU (ABI), dan alamat IP Wi-Fi.
* **Monitor Baterai & Hardware:** Level baterai, status pengisian daya, suhu baterai real-time (°C), voltase, kesehatan baterai, kapasitas storage `/data`, dan RAM.
* **Remote Controller & Navigasi:** Kontrol fisik virtual (Back, Home, Recent Apps, Power / Screen Toggle, Volume +/-).
* **Text Sender & Clipboard Sync:** Ketik teks langsung dari PC ke HP atau sinkronkan clipboard dua arah.
* **Screenshot Instan:** Ambil tangkapan layar HP tanpa meninggalkan file sampah di perangkat.

### 2. 📦 App Manager, Inspector & Audit Iklan/Malware
* **Visual App List:** Menampilkan nama asli aplikasi, nama paket (*package name*), dan icon aplikasi secara otomatis dalam tata letak 2 baris yang elegan.
* **🔍 Detail App Audit (Inspector):**
  * Rincian izin lengkap (*Dangerous permissions, system alert/overlay, background service*).
  * Deteksi SDK Iklan & Pelacak (*Google AdMob, Unity Ads, AppLovin, Facebook Audience Network, IronSource, Mintegral, Pangle*).
  * Informasi signature, target SDK, tanggal pemasangan, sumber penginstal, dan ukuran cache/storage.
* **🚨 Deteksi Adware Pop-up Cerdas:**
  * Mendeteksi otomatis aplikasi nakal yang memunculkan iklan full-screen tiba-tiba saat HP idle atau di home screen (kombinasi deteksi Ad SDK + izin `SYSTEM_ALERT_WINDOW` / Tampilkan di atas aplikasi lain).
* **🛡 Pembasmi Iklan & Pengoptimal HP (Ad-Blocker Helper):**
  * Konfigurasi 1-klik Private DNS (AdGuard DNS `dns.adguard-dns.com` & NextDNS) tanpa perlu root.
  * Reset Private DNS ke setelan standar (*Automatic/Off*).
  * Bersihkan data/cache aplikasi yang dicurigai serta batasi aktivitas latar belakang (*AppOps Run-in-Background*).
* **Verifikasi 2 Langkah (Anti-Salah Hapus):** Setiap operasi penghapusan, uninstall, atau freeze dilengkapi dialog konfirmasi interaktif.
* **Operasi Tambahan:** Pasang APK (Drag & Drop), Buka aplikasi, Force stop, Hapus cache, dan Ekspor/Backup APK ke PC.

### 3. 🧹 Smart Debloater (Integrasi Database UAD 5.300+ Paket)
* **Proteksi 3 Lapis Aplikasi Pihak Ketiga (Anti-Salah Hapus):**
  * Daftar debloater secara ketat **hanya memindai partisi sistem bawaan pabrik** (`/system`, `/product`, `/vendor`, `/apex`).
  * Aplikasi user yang diunduh dari Play Store (seperti WhatsApp, Facebook, Shopee, Mobile Legends) otomatis diisolasi dan tidak akan masuk ke daftar debloat.
* **Kategori Resiko Berdasarkan Database UAD:**
  * 🟢 **Rekomendasi (Aman):** Bloatware OEM, analitik, dan pelacak pabrikan yang 100% aman dihapus/dibekukan.
  * 🟡 **Perlu Pengganti:** Browser atau galeri bawaan (peringatan untuk menginstal alternatif terlebih dahulu).
  * 🟠 **Berisiko:** Layanan yang jika dihapus dapat mematikan fitur spesifik (Bluetooth, AOD, Kamera).
  * 🔴 **BAHAYA / KRITIS:** Peringatan darurat anti-bootloop jika mencoba menghapus core sistem.
* **Batch 1-Click Debloat:** Bersihkan semua bloatware aman sekaligus dalam hitungan detik.

### 4. 🖥 Screen Mirroring (Scrcpy Multi-Version Manager)
* **Download & Switch Versi Scrcpy:** Mengambil daftar rilis resmi Scrcpy langsung dari GitHub Releases API (v5.0.1, v5.0, v4.1, v3.1, dll) dengan opsi unduh 1-klik.
* **Manajemen Proses Cerdas:** Mendeteksi otomatis penutupan jendela Scrcpy (*exit watcher*), sehingga tombol Start langsung aktif kembali tanpa *hang* atau *pipe deadlock*.
* **Sinkronisasi ADB Daemon:** Menghubungkan Scrcpy langsung ke ADB bawaan aplikasi untuk menghindari konflik *ADB server killed*.
* **Kustomisasi Tampilan:**
  * Kualitas: Resolusi hingga 2K, bitrate 2-24 Mbps, frame rate 30-120 FPS.
  * Opsi: *Turn screen off* (layar HP mati saat mirror untuk menghemat baterai), *Stay Awake*, *Always on top*, *Show touches*, dan *No audio*.
  * Perekaman video sesi mirroring langsung ke format `.mp4`.

### 5. 📁 File Explorer
* Jelajahi direktori penyimpanan Android (`/sdcard`, `/`, root).
* Bookmark cepat: SDCard, DCIM, Download, dan Root.
* Transfer file dua arah: Push (PC ke HP) dan Pull (Download HP ke PC).
* Operasi berkas: Buat folder, ganti nama, dan hapus berkas/folder.

### 6. ⚡ Fastboot & Multi-Reboot Diagnostics
* **Reboot Cepat 1-Klik:** Normal System, Recovery, Bootloader / Fastboot, FastbootD, EDL (Emergency Download Mode 9008), dan Sideload.
* **Diagnostik Fastboot Mode:** Deteksi otomatis perangkat Fastboot dan baca seluruh variabel bootloader (`fastboot getvar all`).

### 7. 💻 Shell Terminal & Live Logcat
* Terminal interaktif ADB Shell dengan riwayat perintah dan jalan pintas (*shortcuts*).
* Streaming real-time Android Logcat dengan filter log level (*Verbose, Debug, Info, Warning, Error, Fatal*), pencarian teks, dan opsi ekspor log.
* Log Audit transparan yang merekam setiap perintah ADB yang dieksekusi di balik layar.

### 8. 🌐 Wireless ADB
* Hubungkan perangkat tanpa kabel menggunakan alamat IP & Port.
* Dukungan penuh Android 11+ Wireless Debugging dengan 6-Digit Pairing Code.
* Tombol 1-klik untuk mengaktifkan port TCP/IP 5555 melalui koneksi USB awal.

---

## 🚀 Instalasi & Penggunaan

### Opsi 1: Menggunakan File Standalone EXE (Rekomendasi Pengguna)
1. Buka tab **[Releases](https://github.com/)** pada repository ini.
2. Unduh file **`ADB_Tools_GUI_Single.exe`**.
3. Jalankan langsung di Windows (tidak perlu instal Python, semua tools ADB sudah terpasang di dalamnya).

---

### Opsi 2: Menjalankan dari Source Code (Pengembang)

1. **Clone Repository:**
   ```bash
   git clone https://github.com/USERNAME_ANDA/NAMA_REPO.git
   cd adb-tools
   ```

2. **Pasang Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi:**
   Cukup klik ganda berkas `run.bat` atau jalankan via terminal:
   ```bash
   python main.py
   ```

---

## 📦 Build Sendiri Menjadi Executable (.exe)

Tersedia skrip otomatis untuk membuat berkas `.exe` menggunakan PyInstaller:

* **Build 1 File Portable (Single EXE):**
  Klik ganda `build_single_exe.bat`
  > Hasil output: `dist\ADB_Tools_GUI_Single.exe` (Hanya 1 file yang perlu dibagikan atau dimasukkan ke GitHub Releases).

* **Build Folder Berkas (Onedir EXE):**
  Klik ganda `build_exe.bat`
  > Hasil output: `dist\ADB_Tools_GUI\`

---

## 📂 Struktur Repositori

```
adb-tools/
│── main.py                   # Titik masuk utama aplikasi (PySide6)
│── run.bat                   # Launcher cepat Windows
│── build_single_exe.bat      # Script build 1 file executable (.exe)
│── build_exe.bat             # Script build folder executable
│── ADB_Tools_GUI.spec        # Konfigurasi PyInstaller Onedir
│── ADB_Tools_GUI_Single.spec # Konfigurasi PyInstaller Single File
│── requirements.txt          # Dependensi Python
│── bin/                      # Berisi binaries platform-tools (adb.exe, fastboot.exe, dll)
│── data/                     # Database UAD (uad_lists.json), rilis scrcpy, dan aset icon
│── core/                     # Layanan inti (ADB, Scrcpy, Paket, Audit, File, Device)
│── ui/                       # Tampilan antarmuka PySide6
│   ├── main_window.py        # Jendela utama & header navigasi
│   ├── style.py              # CSS / Qt Stylesheet tema modern
│   ├── modal.py              # Dialog & pop-up custom
│   ├── dialogs/              # Dialog (Ad Blocker, App Audit, Settings, Wireless, Confirm)
│   └── tabs/                 # Tab per fitur (Overview, App Manager, Scrcpy, Files, Fastboot, Terminal)
```

---

## 📄 Lisensi & Kredit

* **ADB & Fastboot:** [Android Open Source Project (AOSP)](https://android.googlesource.com/platform/packages/modules/adb) - Apache License 2.0
* **Scrcpy Integration:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy) - Apache License 2.0
* **Debloat Database:** [Universal Android Debloater (UAD)](https://github.com/0x192/universal-android-debloater) - GPL-3.0
* **Proyek ini:** Berlisensi [MIT License](LICENSE).
