import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from core.settings import settings, get_default_adb_path, get_default_fastboot_path, get_default_scrcpy_path
from core.adb_manager import CREATE_NO_WINDOW
from ui.style import styled_btn

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pengaturan & Lokasi Tool (Settings)")
        self.resize(560, 430)
        self.setMinimumSize(500, 360)
        self.init_ui()
        self.load_current_values()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # 1. Binaries Group
        bin_box = QGroupBox("Lokasi Executable Tool")
        grid = QGridLayout(bin_box)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(6)

        # ADB Path
        lbl_adb = QLabel("Executable ADB (adb.exe):")
        lbl_adb.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        self.txt_adb = QLineEdit()
        self.txt_adb.setPlaceholderText("Lokasi adb.exe...")
        btn_adb_browse = QPushButton("Pilih...")
        btn_adb_browse.setFixedWidth(75)
        btn_adb_browse.clicked.connect(self.browse_adb)

        grid.addWidget(lbl_adb, 0, 0, 1, 2)
        grid.addWidget(self.txt_adb, 1, 0)
        grid.addWidget(btn_adb_browse, 1, 1)

        # Fastboot Path
        lbl_fb = QLabel("Executable Fastboot (fastboot.exe):")
        lbl_fb.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        self.txt_fastboot = QLineEdit()
        self.txt_fastboot.setPlaceholderText("Lokasi fastboot.exe...")
        btn_fb_browse = QPushButton("Pilih...")
        btn_fb_browse.setFixedWidth(75)
        btn_fb_browse.clicked.connect(self.browse_fastboot)

        grid.addWidget(lbl_fb, 2, 0, 1, 2)
        grid.addWidget(self.txt_fastboot, 3, 0)
        grid.addWidget(btn_fb_browse, 3, 1)

        # Scrcpy Path
        lbl_sc = QLabel("Executable Scrcpy (scrcpy.exe):")
        lbl_sc.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        self.txt_scrcpy = QLineEdit()
        self.txt_scrcpy.setPlaceholderText("Lokasi scrcpy.exe...")
        btn_sc_browse = QPushButton("Pilih...")
        btn_sc_browse.setFixedWidth(75)
        btn_sc_browse.clicked.connect(self.browse_scrcpy)

        grid.addWidget(lbl_sc, 4, 0, 1, 2)
        grid.addWidget(self.txt_scrcpy, 5, 0)
        grid.addWidget(btn_sc_browse, 5, 1)

        # Auto-Detect Button
        btn_autodetect = QPushButton("🔍 Deteksi Otomatis Semua Lokasi Path")
        btn_autodetect.setFixedHeight(26)
        btn_autodetect.clicked.connect(self.autodetect_paths)
        grid.addWidget(btn_autodetect, 6, 0, 1, 2)

        main_layout.addWidget(bin_box)

        # 2. General Preferences
        pref_box = QGroupBox("Preferensi Penyimpanan")
        grid_pref = QGridLayout(pref_box)
        grid_pref.setContentsMargins(8, 8, 8, 8)
        grid_pref.setVerticalSpacing(5)
        grid_pref.setHorizontalSpacing(6)

        lbl_dl = QLabel("Folder Unduhan & Backup APK Default:")
        lbl_dl.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        self.txt_download = QLineEdit()
        btn_dl_browse = QPushButton("Pilih...")
        btn_dl_browse.setFixedWidth(75)
        btn_dl_browse.clicked.connect(self.browse_download_dir)

        grid_pref.addWidget(lbl_dl, 0, 0, 1, 2)
        grid_pref.addWidget(self.txt_download, 1, 0)
        grid_pref.addWidget(btn_dl_browse, 1, 1)

        main_layout.addWidget(pref_box)

        # Bottom Buttons
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 4, 0, 0)
        bottom_bar.setSpacing(6)

        btn_test = QPushButton("⚡ Uji Semua Path")
        btn_test.setFixedHeight(26)
        btn_test.clicked.connect(self.test_paths)
        bottom_bar.addWidget(btn_test)
        bottom_bar.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.setFixedHeight(26)
        btn_cancel.clicked.connect(self.reject)
        btn_save = styled_btn("Simpan Pengaturan", "primary")
        btn_save.setFixedHeight(26)
        btn_save.clicked.connect(self.save_settings)
        bottom_bar.addWidget(btn_cancel)
        bottom_bar.addWidget(btn_save)

        main_layout.addLayout(bottom_bar)

    def load_current_values(self):
        self.txt_adb.setText(settings.get("adb_path") or "")
        self.txt_fastboot.setText(settings.get("fastboot_path") or "")
        self.txt_scrcpy.setText(settings.get("scrcpy_path") or "")
        self.txt_download.setText(settings.get("default_download_dir") or "")

    def browse_adb(self):
        p, _ = QFileDialog.getOpenFileName(self, "Pilih adb.exe", "", "Executable (adb.exe);;All Files (*.*)")
        if p:
            self.txt_adb.setText(p)

    def browse_fastboot(self):
        p, _ = QFileDialog.getOpenFileName(self, "Pilih fastboot.exe", "", "Executable (fastboot.exe);;All Files (*.*)")
        if p:
            self.txt_fastboot.setText(p)

    def browse_scrcpy(self):
        p, _ = QFileDialog.getOpenFileName(self, "Pilih scrcpy.exe", "", "Executable (scrcpy.exe);;All Files (*.*)")
        if p:
            self.txt_scrcpy.setText(p)

    def browse_download_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Pilih Folder Unduhan", self.txt_download.text())
        if d:
            self.txt_download.setText(d)

    def autodetect_paths(self):
        self.txt_adb.setText(get_default_adb_path())
        self.txt_fastboot.setText(get_default_fastboot_path())
        self.txt_scrcpy.setText(get_default_scrcpy_path())
        QMessageBox.information(self, "Auto-Detect", "Semua lokasi tool berhasil dideteksi otomatis!")

    def test_paths(self):
        results = []
        for name, path, flag in [
            ("ADB", self.txt_adb.text().strip(), "version"),
            ("Fastboot", self.txt_fastboot.text().strip(), "--version"),
            ("Scrcpy", self.txt_scrcpy.text().strip(), "--version"),
        ]:
            if not path:
                results.append(f"❌ {name}: Path belum ditentukan")
                continue
            if not os.path.exists(path):
                results.append(f"❌ {name}: File tidak ditemukan ({path})")
                continue
            try:
                out = subprocess.check_output([path, flag], stderr=subprocess.STDOUT, text=True, creationflags=CREATE_NO_WINDOW)
                first_line = out.strip().splitlines()[0] if out else "OK"
                results.append(f"✅ {name}: {first_line}")
            except Exception as e:
                results.append(f"⚠️ {name}: Eksekusi gagal ({e})")

        QMessageBox.information(self, "Hasil Verifikasi Tool", "\n\n".join(results))

    def save_settings(self):
        settings.set("adb_path", self.txt_adb.text().strip())
        settings.set("fastboot_path", self.txt_fastboot.text().strip())
        settings.set("scrcpy_path", self.txt_scrcpy.text().strip())
        settings.set("default_download_dir", self.txt_download.text().strip())
        QMessageBox.information(self, "Tersimpan", "Pengaturan berhasil disimpan!")
        self.accept()
