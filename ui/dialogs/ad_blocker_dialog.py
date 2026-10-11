"""
Ad Blocker & Privacy Management Dialog.
Provides automated ADB solutions to eliminate or suppress ads:
- Private DNS ad-blocking (AdGuard DNS, NextDNS, ControlD) via 1-click ADB command
- App cache cleaner (removes pre-cached ad video payloads)
- AppOps background restriction (prevents ad SDKs running background daemons)
- Clear guidance for offline game mode & APK patching
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from core.adb_manager import adb_manager
from ui.style import styled_btn


class AdBlockerDialog(QDialog):
    def __init__(self, serial: str, package_name: str = "", app_name: str = "", parent=None):
        super().__init__(parent)
        self.serial = serial
        self.package_name = package_name
        self.app_name = app_name or package_name or "Aplikasi Terpilih"

        self.setWindowTitle("🛡️ Solusi & Pengaturan Pemblokir Iklan (Ad-Blocker)")
        self.resize(620, 350)
        self.setMinimumSize(540, 280)

        self.init_ui()
        self.refresh_dns_status()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header Information Banner
        header = QFrame()
        header.setStyleSheet("background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px;")
        h_box = QHBoxLayout(header)
        h_box.setContentsMargins(4, 4, 4, 4)
        lbl_icon = QLabel("🛡️")
        lbl_icon.setStyleSheet("font-size: 26px;")
        h_box.addWidget(lbl_icon)

        lbl_info = QLabel(
            f"<b>Solusi Menghilangkan Iklan untuk: {self.app_name}</b><br>"
            "<span style='color: #475569; font-size: 11px;'>"
            "Iklan dapat diblokir secara efektif menggunakan <b>Private DNS</b> (bebas root), "
            "membersihkan cache iklan lama, atau mematikan koneksi internet pada game offline.</span>"
        )
        lbl_info.setWordWrap(True)
        h_box.addWidget(lbl_info, 1)
        layout.addWidget(header)

        # 2. Section 1: Private DNS Ad-Blocking (System-Wide, No Root)
        grp_dns = QGroupBox("1. Pemblokir Iklan Private DNS (Paling Ampuh & Tanpa Root)")
        grp_dns.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
        dns_layout = QVBoxLayout(grp_dns)
        dns_layout.setSpacing(8)

        # Status row
        status_row = QHBoxLayout()
        lbl_cur = QLabel("Status Private DNS Saat Ini di HP:")
        lbl_cur.setStyleSheet("font-weight: 500; color: #334155;")
        status_row.addWidget(lbl_cur)

        self.lbl_dns_status = QLabel("Memeriksa status...")
        self.lbl_dns_status.setStyleSheet("font-weight: bold; color: #0284c7; padding: 2px 8px; background: #e0f2fe; border-radius: 4px;")
        status_row.addWidget(self.lbl_dns_status)
        status_row.addStretch()

        btn_chk = QPushButton("🔄 Cek Ulang")
        btn_chk.setFixedHeight(26)
        btn_chk.clicked.connect(self.refresh_dns_status)
        status_row.addWidget(btn_chk)
        dns_layout.addLayout(status_row)

        lbl_dns_desc = QLabel(
            "Mengaktifkan Private DNS akan memutus koneksi server iklan (Google AdMob, ironSource, AppLovin, Vungle) "
            "secara otomatis pada seluruh game dan aplikasi di Android tanpa membutuhkan root."
        )
        lbl_dns_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        lbl_dns_desc.setWordWrap(True)
        dns_layout.addWidget(lbl_dns_desc)

        # DNS Action Buttons
        btn_grid = QGridLayout()
        btn_grid.setSpacing(8)

        self.btn_adguard = styled_btn("🛡️ Aktifkan AdGuard DNS", "success")
        self.btn_adguard.setToolTip("Blokir domain iklan global: dns.adguard-dns.com")
        self.btn_adguard.clicked.connect(lambda: self.apply_dns("dns.adguard-dns.com", "AdGuard DNS"))
        btn_grid.addWidget(self.btn_adguard, 0, 0)

        self.btn_nextdns = QPushButton("🛡️ Aktifkan NextDNS")
        self.btn_nextdns.setToolTip("Blokir iklan via NextDNS: dns.nextdns.io")
        self.btn_nextdns.clicked.connect(lambda: self.apply_dns("dns.nextdns.io", "NextDNS"))
        btn_grid.addWidget(self.btn_nextdns, 0, 1)

        self.btn_disable_dns = QPushButton("⚪ Nonaktifkan DNS (Kembali Default)")
        self.btn_disable_dns.setToolTip("Kembalikan Private DNS perangkat ke mode standar")
        self.btn_disable_dns.clicked.connect(self.disable_dns)
        btn_grid.addWidget(self.btn_disable_dns, 0, 2)

        dns_layout.addLayout(btn_grid)
        layout.addWidget(grp_dns)

        # 3. Section 2: App-Specific Optimizations (Cache & Background)
        if self.package_name:
            grp_app = QGroupBox(f"2. Optimasi Khusus: {self.package_name}")
            grp_app.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; }")
            app_layout = QVBoxLayout(grp_app)
            app_layout.setSpacing(8)

            lbl_app_tip = QLabel(
                "• <b>Cache Iklan:</b> Sering kali game sudah mendownload video iklan ke penyimpanan internal sebelum pemblokir DNS aktif.<br>"
                "• <b>Background Limit:</b> Menghentikan SDK iklan agar tidak memproses analitik di latar belakang."
            )
            lbl_app_tip.setStyleSheet("color: #475569; font-size: 11px;")
            lbl_app_tip.setWordWrap(True)
            app_layout.addWidget(lbl_app_tip)

            opt_row = QHBoxLayout()
            opt_row.setSpacing(8)

            btn_clean_cache = QPushButton("🧹 Bersihkan Data / Cache Iklan")
            btn_clean_cache.setToolTip("Reset cache aplikasi agar iklan video yang tersimpan hilang (pm clear)")
            btn_clean_cache.clicked.connect(self.action_clear_data)
            opt_row.addWidget(btn_clean_cache)

            btn_limit_bg = QPushButton("🛑 Batasi Background Ad Process")
            btn_limit_bg.setToolTip("Terapkan AppOps RUN_IN_BACKGROUND ignore")
            btn_limit_bg.clicked.connect(self.action_limit_bg)
            opt_row.addWidget(btn_limit_bg)

            opt_row.addStretch()
            app_layout.addLayout(opt_row)
            layout.addWidget(grp_app)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def refresh_dns_status(self):
        if not self.serial:
            self.lbl_dns_status.setText("Tidak ada perangkat terhubung")
            self.lbl_dns_status.setStyleSheet("color: #dc2626;")
            return

        mode, spec = adb_manager.get_private_dns(self.serial)
        if mode == "hostname" and spec:
            self.lbl_dns_status.setText(f"Aktif ({spec})")
            self.lbl_dns_status.setStyleSheet("color: #15803d; font-weight: bold; background: #dcfce7; padding: 2px 8px; border-radius: 4px;")
        elif mode in ["opportunistic", "auto"]:
            self.lbl_dns_status.setText("Otomatis (Bawaan Provider)")
            self.lbl_dns_status.setStyleSheet("color: #b45309; font-weight: bold; background: #fef3c7; padding: 2px 8px; border-radius: 4px;")
        else:
            self.lbl_dns_status.setText("Nonaktif (Iklan Tidak Diblokir)")
            self.lbl_dns_status.setStyleSheet("color: #dc2626; font-weight: bold; background: #fee2e2; padding: 2px 8px; border-radius: 4px;")

    def apply_dns(self, hostname: str, provider_name: str):
        if not self.serial:
            return
        ok, out = adb_manager.set_private_dns(self.serial, hostname)
        if ok:
            QMessageBox.information(
                self, "Berhasil",
                f"✅ {provider_name} ({hostname}) berhasil diterapkan pada perangkat!\n\n"
                "Semua request iklan AdMob, ironSource, AppLovin, dan Vungle sekarang otomatis diblokir oleh sistem."
            )
            self.refresh_dns_status()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal menerapkan Private DNS:\n{out}")

    def disable_dns(self):
        if not self.serial:
            return
        ok, out = adb_manager.disable_private_dns(self.serial)
        if ok:
            QMessageBox.information(self, "Berhasil", "Private DNS telah dikembalikan ke pengaturan default.")
            self.refresh_dns_status()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal menonaktifkan Private DNS:\n{out}")

    def action_clear_data(self):
        if not self.serial or not self.package_name:
            return
        reply = QMessageBox.question(
            self, "Konfirmasi Bersihkan Cache/Data",
            f"Bersihkan data dan cache untuk <b>{self.app_name}</b>?<br><br>"
            "Semua video iklan yang tersimpan di memori perangkat akan dihapus.<br>"
            "<i>(Catatan: Progress game lokal yang tidak tersinkron cloud mungkin tereset)</i>",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, out = adb_manager.clear_package_data(self.serial, self.package_name)
            if ok:
                QMessageBox.information(self, "Berhasil", f"Cache dan data {self.package_name} berhasil dibersihkan!")
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal membersihkan data:\n{out}")

    def action_limit_bg(self):
        if not self.serial or not self.package_name:
            return
        ok, out = adb_manager.block_app_background(self.serial, self.package_name)
        if ok:
            QMessageBox.information(
                self, "Berhasil",
                f"Proses latar belakang (AppOps RUN_IN_BACKGROUND) untuk {self.package_name} berhasil dibatasi!\n"
                "Modul iklan tidak dapat berjalan diam-diam saat game ditutup."
            )
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal membatasi background:\n{out}")
