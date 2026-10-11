# ⚡ ADB Studio (GUI Tool Suite)

Aplikasi Desktop modern berbasis **Python (PySide6)** untuk mengelola, mengontrol, dan mendiagnosis perangkat Android melalui **ADB** dan **Fastboot**.

---

## ✨ Fitur Lengkap

### 1. 📱 Device Overview & Remote Control
* **Identitas Lengkap:** Brand, Nama Model, Nomor Seri, Versi Android, SDK API Level, Build Number, Security Patch, CPU Architecture (ABI), dan Alamat IP Wi-Fi.
* **Hardware & Status Baterai:** Persentase baterai, status charging, suhu baterai (°C), voltase, kesehatan baterai, resolusi layar, screen density (DPI), sisa storage (`/data`), dan pemakaian RAM.
* **Remote Key Controller:** Tombol navigasi fisik (Back, Home, Recent Apps, Power / Wake, Volume +, Volume -).
* **Text Sender:** Mengetik teks langsung dari PC ke input field yang aktif di HP.
* **Tangkapan Layar:** Screenshot langsung dari layar HP tanpa file sementara di HP, dilengkapi pratinjau dan opsi simpan PNG.
* **Sinkronisasi Clipboard:** Membaca atau mengirim teks ke clipboard HP.

### 2. 📦 App Manager & Smart Debloater (UAD Integration)
* **Integrasi Database UAD (5.300+ Aplikasi):** Terhubung dengan database resmi Universal Android Debloater (termasuk kustomisasi `org.lineageos.jelly` dan `com.cyanogenmod.filemanager`).
* **Proteksi Keamanan Berlapis (Anti-Bootloop):**
  * 🟢 **Aman Dihapus (Recommended):** Bloatware bawaan pabrik, pelacak, dan analitik yang 100% aman dihapus/dibekukan.
  * 🟡 **Perlu Aplikasi Pengganti (Advanced):** Aplikasi seperti browser atau file manager bawaan (peringatan agar pengguna memasang penggantinya dulu).
  * 🟠 **Berisiko (Expert):** Aplikasi yang bila dihapus dapat menghilangkan fitur tertentu (Bluetooth, AOD, Kamera).
  * 🔴 **BAHAYA / SISTEM KRITIS (Unsafe):** Dialog peringatan darurat jika pengguna mencoba menghapus aplikasi yang dapat menyebabkan **HP BOOTLOOP / MATI TOTAL**.
* **Panel Panduan & Deskripsi Aplikasi:** Klik pada aplikasi manapun untuk membaca penjelasan detail fungsi aplikasi tersebut langsung di dalam GUI.
* **⚡ 1-Click Batch Debloat (Rekomendasi):** Otomatis mendeteksi semua bloatware aman di HP dan membekukannya (*freeze/disable*) atau menghapusnya secara massal dengan aman.
* **🔄 Update UAD Database:** Tombol 1-klik untuk memperbarui ribuan definisi aplikasi terbaru langsung dari GitHub.
* **Drag & Drop:** Cukup tarik file `.apk` ke dalam aplikasi untuk langsung menginstal.
* **Operasi Tambahan:** Launch app, Force stop, Clear data & cache, Extract/Backup APK ke PC.

### 3. 📁 File Explorer
* **Navigasi File Android:** Jelajahi sistem file perangkat (`/sdcard`, `/`, dsb) dengan bookmark cepat (SDCard, DCIM, Download, Root).
* **Transfer Dua Arah:**
  * Push file atau folder dari PC ke HP (dengan progress bar).
  * Pull (Download) file atau folder dari HP ke PC.
* **Manajemen File:** Buat folder baru (`mkdir`), ganti nama file/folder (`rename`), dan hapus (`delete`).

### 4. 🖥 Screen Mirroring (Integrasi Multi-Versi Scrcpy)
* **Manajer Versi Otomatis dari GitHub:** Mengambil daftar rilis resmi Scrcpy langsung dari GitHub Releases API (`https://github.com/Genymobile/scrcpy/releases`).
* **Pilihan Versi Bebas & Multi-Unduhan:** Pengguna dapat memilih versi yang diinginkan (misal v5.0.1, v5.0, v4.1, v3.3.4, v3.1, v2.7, dsb), mengunduhnya dengan 1-klik, dan berganti versi aktif kapan saja tanpa perlu unduh ulang.
* **Deteksi Lokal & Custom:** Otomatis mendeteksi folder versi yang sudah terinstal di `bin/scrcpy_versions/` atau memilih file `scrcpy.exe` manual dari komputer.
* **Pengaturan Kualitas Layar:**
  * Resolusi (Native, 720p, 1080p FHD, 1440p 2K).
  * Video Bitrate (2 Mbps s/d 24 Mbps).
  * Frame Rate (30 FPS, 60 FPS, 120 FPS).
* **Opsi Mirroring:**
  * Tetap menyala (*Stay Awake*).
  * Matikan layar fisik HP saat mirroring untuk menghemat baterai (*Turn screen off*).
  * Mute / tanpa audio (*No audio*).
  * Selalu di atas (*Always on top*), Fullscreen, dan Tampilkan sentuhan (*Show touches*).
  * Mode OTG (simulasi mouse/keyboard tanpa layar).
* **Perekaman Layar:** Simpan sesi mirroring langsung ke format video `.mp4`.

### 5. 🔄 Reboot Options & Device Diagnostics
* **Menu Reboot One-Click (ADB):**
  * Reboot System Normal
  * Reboot ke Recovery (TWRP / Stock)
  * Reboot ke Bootloader / Fastboot
  * Reboot ke FastbootD (Dynamic Partitions)
  * Reboot ke EDL (Qualcomm Emergency Download Mode 9008)
  * Reboot ke Sideload
* **Fitur Fastboot Mode & Diagnostics:**
  * Deteksi perangkat Fastboot secara otomatis.
  * Baca semua variabel bootloader (`fastboot getvar all`).
  * Fastboot Reboot System & Bootloader.
  * Panduan ringkas fungsi setiap mode reboot untuk pengguna awam.

### 6. 💻 Terminal & Live Logs
* **ADB Shell Console:** Terminal interaktif dengan riwayat perintah dan tombol *preset* (info baterai, daftar app, free disk, top process, dll).
* **Live Logcat Stream:** Streaming logcat perangkat real-time dengan filter log level (*Verbose, Debug, Info, Warning, Error, Fatal*), filter teks, serta ekspor log ke file `.txt`.
* **ADB Activity Audit:** Transparansi penuh yang mencatat setiap perintah ADB/Fastboot yang dijalankan aplikasi di latar belakang beserta outputnya.

### 7. 🌐 Wi-Fi / Wireless ADB
* Hubungkan HP tanpa kabel USB melalui alamat IP dan Port (`adb connect ip:port`).
* Mendukung pairing Wireless Debugging Android 11+ (dengan 6-digit code).
* Fitur 1-klik untuk mengaktifkan port TCP/IP 5555 pada HP yang sedang dicolok USB.

---

## 🚀 Cara Menjalankan

### Persyaratan
* Python 3.10+ (Sudah terpasang di komputer Anda)
* Dependensi `PySide6` (Sudah terpasang)

### Menjalankan Langsung:
Cukup klik ganda file:
```bat
run.bat
```
atau lewat terminal PowerShell / Command Prompt:
```bash
python main.py
```

---

## 📦 Build Menjadi File Executable (.exe)

Untuk membagikan aplikasi ini kepada orang lain tanpa perlu instal Python:
Cukup klik ganda:
```bat
build_exe.bat
```
File `.exe` siap pakai akan berada di dalam folder `dist/ADB_Studio/`.

---

## 📂 Struktur Proyek Terpisah Per Fungsi
```
adb-tools/
│── main.py                   # Titik masuk utama aplikasi
│── run.bat                   # Script launcher cepat Windows
│── build_exe.bat             # Script build ke .exe standalone
│── requirements.txt          # Daftar pustaka Python
│── bin/                      # [PORTABLE] Berisi adb.exe, fastboot.exe, & file DLL
│── data/                     # Database UAD debloater (uad_lists.json)
│── core/
│   ├── cmd_runner.py         # Subprocess runner, timeout, & logging signal
│   ├── device_service.py     # Deteksi device, specs hardware, baterai, storage
│   ├── package_service.py    # Install/uninstall APK, freeze, clear data, backup
│   ├── debloater_service.py   # Database UAD debloater & evaluator risiko bootloop
│   ├── file_service.py       # Android filesystem, push/pull transfer, mkdir, rm
│   ├── control_service.py    # Remote keyevent, screen capture, typing, clipboard
│   ├── reboot_service.py     # Reboot modes (recovery, fastboot, edl, sideload)
│   ├── fastboot_service.py   # Fastboot reboot, getvar all, & deteksi device
│   ├── wireless_service.py   # Wi-Fi connect, pairing code, TCP/IP 5555
│   ├── server_service.py     # Start, kill, restart ADB daemon server
│   ├── scrcpy_manager.py     # Controller Scrcpy & auto-downloader GitHub
│   ├── settings.py           # Manajemen konfigurasi dan path eksekusi
│   └── adb_manager.py        # Unified facade / pintu gerbang akses seluruh servis
└── ui/
    ├── main_window.py        # Jendela utama, sidebar & topbar
    ├── style.py              # Tema gelap modern (QSS stylesheet)
    ├── tabs/                 # 6 Tab modul fitur UI
    └── dialogs/              # Dialog Wi-Fi ADB & Pengaturan Path
```

> **💡 Tips Debugging:** Setiap file di dalam folder `core/` dapat dijalankan langsung secara mandiri di terminal untuk menguji fungsi spesifik tanpa harus membuka GUI!  
> Contoh:
> * Debug info perangkat: `python core/device_service.py`
> * Debug daftar package: `python core/package_service.py`
> * Debug file explorer: `python core/file_service.py`
> * Debug fastboot: `python core/fastboot_service.py`

