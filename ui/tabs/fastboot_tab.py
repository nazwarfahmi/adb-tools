import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QTextEdit, QGridLayout, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from core.adb_manager import adb_manager
from ui.style import styled_btn

class FastbootTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.fastboot_serial = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Tab Widget separating ADB Reboot vs Fastboot Mode
        self.sub_tabs = QTabWidget()

        # 1. Sub-Tab: ADB Reboot Options
        tab_reboot = QWidget()
        self.setup_reboot_tab(tab_reboot)
        self.sub_tabs.addTab(tab_reboot, "🔄  Mode Reboot (ADB)")

        # 2. Sub-Tab: Fastboot Diagnostics
        tab_fastboot = QWidget()
        self.setup_fastboot_tab(tab_fastboot)
        self.sub_tabs.addTab(tab_fastboot, "⚡  Mode Fastboot && Diagnostik")

        main_layout.addWidget(self.sub_tabs)

    # -------------------------------------------------------------
    # 1. SUB-TAB: ADB REBOOT OPTIONS
    # -------------------------------------------------------------
    def setup_reboot_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Reboot Actions Card
        adb_box = QGroupBox("🔄 Pilih Mode Reboot untuk Perangkat yang Terhubung")
        adb_layout = QVBoxLayout(adb_box)
        adb_layout.setContentsMargins(8, 8, 8, 8)
        adb_layout.setSpacing(6)

        grid_btn = QGridLayout()
        grid_btn.setHorizontalSpacing(8)
        grid_btn.setVerticalSpacing(6)

        btn_rb_sys = styled_btn("🔄 Reboot System (Normal)", "primary")
        btn_rb_rec = QPushButton("🛡 Reboot to Recovery")
        btn_rb_bl = QPushButton("⚡ Reboot to Bootloader")
        btn_rb_fbd = QPushButton("📦 Reboot to FastbootD")
        btn_rb_edl = styled_btn("🚨 Reboot to EDL (9008)", "danger")
        btn_rb_side = QPushButton("📥 Reboot to Sideload")

        for b in [btn_rb_sys, btn_rb_rec, btn_rb_bl, btn_rb_fbd, btn_rb_edl, btn_rb_side]:
            b.setFixedHeight(28)

        btn_rb_sys.clicked.connect(lambda: self.do_adb_reboot("system"))
        btn_rb_rec.clicked.connect(lambda: self.do_adb_reboot("recovery"))
        btn_rb_bl.clicked.connect(lambda: self.do_adb_reboot("bootloader"))
        btn_rb_fbd.clicked.connect(lambda: self.do_adb_reboot("fastboot"))
        btn_rb_edl.clicked.connect(lambda: self.do_adb_reboot("edl"))
        btn_rb_side.clicked.connect(lambda: self.do_adb_reboot("sideload"))

        grid_btn.addWidget(btn_rb_sys, 0, 0)
        grid_btn.addWidget(btn_rb_rec, 0, 1)
        grid_btn.addWidget(btn_rb_bl, 0, 2)
        grid_btn.addWidget(btn_rb_fbd, 1, 0)
        grid_btn.addWidget(btn_rb_edl, 1, 1)
        grid_btn.addWidget(btn_rb_side, 1, 2)

        adb_layout.addLayout(grid_btn)
        layout.addWidget(adb_box)

        # Guide Card
        guide_box = QGroupBox("ℹ️ Panduan Singkat Fungsi Mode Reboot")
        guide_layout = QGridLayout(guide_box)
        guide_layout.setContentsMargins(8, 8, 8, 8)
        guide_layout.setSpacing(5)

        guides = [
            ("🔄 System:", "Menyalakan ulang HP kembali ke sistem Android normal seperti biasa."),
            ("🛡 Recovery:", "Masuk ke mode TWRP / Stock Recovery untuk wipe data, cache, atau flash zip."),
            ("⚡ Bootloader:", "Masuk ke mode Fastboot untuk diagnosis bootloader atau flashing resmi."),
            ("📦 FastbootD:", "Mode Fastboot dinamis khusus untuk perangkat Android 10+ (Dynamic Partition)."),
            ("🚨 EDL (9008):", "Emergency Download Mode khusus chipset Qualcomm untuk unbrick darurat."),
            ("📥 Sideload:", "Mode transfer pembaruan paket OTA atau ROM langsung dari PC via Recovery."),
        ]

        for i, (mode_title, desc) in enumerate(guides):
            lbl_title = QLabel(mode_title)
            lbl_title.setStyleSheet("color: #0284c7; font-weight: 600; font-size: 11px;")
            lbl_desc = QLabel(desc)
            lbl_desc.setStyleSheet("color: #475569; font-size: 11px;")
            guide_layout.addWidget(lbl_title, i, 0)
            guide_layout.addWidget(lbl_desc, i, 1)

        layout.addWidget(guide_box)
        layout.addStretch()

    # -------------------------------------------------------------
    # 2. SUB-TAB: FASTBOOT MODE & DIAGNOSTICS
    # -------------------------------------------------------------
    def setup_fastboot_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Detection Bar Card
        fb_box = QGroupBox("⚡ Deteksi Perangkat Mode Fastboot")
        fb_layout = QVBoxLayout(fb_box)
        fb_layout.setContentsMargins(8, 8, 8, 8)
        fb_layout.setSpacing(6)

        row_fb_dev = QHBoxLayout()
        row_fb_dev.setSpacing(8)

        self.lbl_fb_dev = QLabel("Fastboot Device: Tidak terdeteksi")
        self.lbl_fb_dev.setStyleSheet("font-weight: 600; color: #d97706; font-size: 11px;")
        row_fb_dev.addWidget(self.lbl_fb_dev)
        row_fb_dev.addStretch()

        btn_refresh_fb = QPushButton("🔍 Pindai Perangkat Fastboot")
        btn_refresh_fb.setFixedHeight(26)
        btn_refresh_fb.clicked.connect(self.scan_fastboot)
        row_fb_dev.addWidget(btn_refresh_fb)
        fb_layout.addLayout(row_fb_dev)

        # Actions Row
        row_fb_actions = QHBoxLayout()
        row_fb_actions.setSpacing(6)

        btn_getvar = QPushButton("📋 Baca Variabel Perangkat (getvar all)")
        btn_getvar.setFixedHeight(26)
        btn_getvar.clicked.connect(self.fastboot_getvar)

        btn_fb_reboot_sys = styled_btn("🔄 Fastboot Reboot System", "primary")
        btn_fb_reboot_sys.setFixedHeight(26)
        btn_fb_reboot_sys.clicked.connect(lambda: self.do_fastboot_reboot("system"))

        btn_fb_reboot_bl = QPushButton("⚡ Fastboot Reboot Bootloader")
        btn_fb_reboot_bl.setFixedHeight(26)
        btn_fb_reboot_bl.clicked.connect(lambda: self.do_fastboot_reboot("bootloader"))

        row_fb_actions.addWidget(btn_getvar)
        row_fb_actions.addWidget(btn_fb_reboot_sys)
        row_fb_actions.addWidget(btn_fb_reboot_bl)
        fb_layout.addLayout(row_fb_actions)

        layout.addWidget(fb_box)

        # Console Output Card
        log_box = QGroupBox("📋 Output / Log Diagnostik Fastboot")
        log_layout = QVBoxLayout(log_box)
        log_layout.setContentsMargins(8, 8, 8, 8)
        log_layout.setSpacing(4)

        self.txt_fb_log = QTextEdit()
        self.txt_fb_log.setPlaceholderText("Output respon dari Fastboot akan ditampilkan di sini...")
        self.txt_fb_log.setStyleSheet("background-color: #0f172a; color: #38bdf8; font-family: Consolas, monospace; font-size: 11px;")
        log_layout.addWidget(self.txt_fb_log)

        layout.addWidget(log_box)

    # -------------------------------------------------------------
    # LOGIC & ACTIONS
    # -------------------------------------------------------------
    def set_device(self, serial: str):
        self.current_serial = serial

    def do_adb_reboot(self, mode: str):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Pilih perangkat ADB aktif terlebih dahulu.")
            return

        reply = QMessageBox.question(self, "Konfirmasi Reboot",
                                     f"Reboot perangkat '{self.current_serial}' ke mode '{mode}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, out = adb_manager.reboot(self.current_serial, mode)
            if ok:
                self.txt_fb_log.append(f"[ADB] Perintah reboot ({mode}) berhasil dikirim.")
                QMessageBox.information(self, "Reboot", f"Perintah reboot ({mode}) terkirim.")
            else:
                self.txt_fb_log.append(f"[ADB Error] {out}")
                QMessageBox.critical(self, "Reboot Error", out)

    def scan_fastboot(self):
        devices = adb_manager.get_fastboot_devices()
        if devices:
            self.fastboot_serial = devices[0]["serial"]
            self.lbl_fb_dev.setText(f"Fastboot Device: {self.fastboot_serial}")
            self.lbl_fb_dev.setStyleSheet("color: #16a34a; font-weight: 600; font-size: 11px;")
            self.txt_fb_log.append(f"[Fastboot] Terdeteksi {len(devices)} perangkat Fastboot: {self.fastboot_serial}")
        else:
            self.fastboot_serial = ""
            self.lbl_fb_dev.setText("Fastboot Device: Tidak terdeteksi")
            self.lbl_fb_dev.setStyleSheet("color: #d97706; font-weight: 600; font-size: 11px;")
            self.txt_fb_log.append("[Fastboot] Tidak ada perangkat dalam mode Fastboot yang ditemukan.")

    def do_fastboot_reboot(self, mode: str):
        self.txt_fb_log.append(f"[Fastboot] Mengirim perintah reboot: {mode}...")
        ok, out = adb_manager.fastboot_reboot(self.fastboot_serial, mode)
        self.txt_fb_log.append(out)
        if ok:
            QMessageBox.information(self, "Fastboot", f"Perintah reboot ({mode}) berhasil dikirim!")
        else:
            QMessageBox.critical(self, "Fastboot Error", out)

    def fastboot_getvar(self):
        self.txt_fb_log.append("[Fastboot] Membaca semua variabel bootloader (getvar all)...")
        ok, out = adb_manager.fastboot_getvar_all(self.fastboot_serial)
        self.txt_fb_log.append(out)
