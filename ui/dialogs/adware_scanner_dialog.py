"""
Adware Scanner Dialog module.
Scans all applications on the connected device for rogue full-screen popup adware,
screen hijackers (REORDER_TASKS, SYSTEM_ALERT_WINDOW), keyboard monetizers, and OEM ad daemons.
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFrame, QMessageBox, QAbstractItemView, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont

from core.adb_manager import adb_manager
from core.app_audit_service import scan_adware_on_device
from ui.style import styled_btn
from ui.dialogs.app_audit_dialog import AppAuditDialog
from ui.dialogs.ad_blocker_dialog import AdBlockerDialog
from ui.dialogs.confirm_dialog import confirm_two_step


class AdwareScanThread(QThread):
    progress = Signal(int, int, str)
    finished_scan = Signal(list)

    def __init__(self, serial: str):
        super().__init__()
        self.serial = serial

    def run(self):
        def on_prog(cur, tot, pkg):
            self.progress.emit(cur, tot, pkg)

        results = scan_adware_on_device(self.serial, progress_cb=on_prog)
        self.finished_scan.emit(results)


class AdwareScannerDialog(QDialog):
    def __init__(self, serial: str, parent=None):
        super().__init__(parent)
        self.serial = serial
        self.scan_results: List[Dict[str, Any]] = []

        self.setWindowTitle("🚨 Pemindai Adware Layar Penuh & Iklan Pop-up (Adware Hunter)")
        self.resize(980, 620)
        self.setMinimumSize(850, 500)

        self.init_ui()
        self.start_scan()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header Banner
        header = QFrame()
        header.setStyleSheet("background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px;")
        h_box = QHBoxLayout(header)
        h_box.setContentsMargins(4, 4, 4, 4)
        h_box.setSpacing(12)

        lbl_icon = QLabel("🚨")
        lbl_icon.setStyleSheet("font-size: 32px;")
        h_box.addWidget(lbl_icon)

        lbl_desc = QLabel(
            "<b style='font-size: 13px; color: #991b1b;'>Deteksi Iklan Pop-up Selayar Penuh & Pembajak Layar</b><br>"
            "<span style='color: #475569; font-size: 11px;'>"
            "Alat ini mendeteksi aplikasi yang memiliki izin <b>REORDER_TASKS</b> (bisa membajak layar depan saat membuka WhatsApp), "
            "izin <b>Overlay</b>, Keyboard yang disusupi monetisasi iklan, serta bloatware iklan sistem bawaan.</span>"
        )
        lbl_desc.setWordWrap(True)
        h_box.addWidget(lbl_desc, 1)

        # Quick Actions in Header
        btn_box = QVBoxLayout()
        btn_box.setSpacing(6)

        btn_dns = styled_btn("🛡️ Solusi Private DNS", "success")
        btn_dns.setToolTip("Blokir seluruh server iklan tanpa root via Private DNS")
        btn_dns.clicked.connect(self.open_dns_dialog)
        btn_box.addWidget(btn_dns)

        btn_gboard = QPushButton("⌨ Alihkan ke Gboard")
        btn_gboard.setToolTip("Ganti keyboard default ke Google Gboard yang bersih & bebas iklan")
        btn_gboard.clicked.connect(self.switch_to_gboard)
        btn_box.addWidget(btn_gboard)

        h_box.addLayout(btn_box)
        layout.addWidget(header)

        # 2. Control & Progress Bar
        ctrl_row = QHBoxLayout()
        self.btn_rescan = styled_btn("🔄 Pindai Ulang HP", "primary")
        self.btn_rescan.clicked.connect(self.start_scan)
        ctrl_row.addWidget(self.btn_rescan)

        self.lbl_status = QLabel("Menyiapkan pemindaian...")
        self.lbl_status.setStyleSheet("color: #475569; font-size: 11px; font-weight: 500;")
        ctrl_row.addWidget(self.lbl_status, 1)

        layout.addLayout(ctrl_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background: #e2e8f0; border-radius: 4px; text-align: center; }
            QProgressBar::chunk { background: #ef4444; border-radius: 4px; }
        """)
        layout.addWidget(self.progress_bar)

        # 3. Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Aplikasi & Package", "Tingkat Ancaman", "Vektor Pembajakan", "Modul Iklan Terdeteksi", "Aksi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(2, 230)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(44)
        layout.addWidget(self.table)

        # 4. Footer
        footer = QHBoxLayout()
        self.lbl_summary = QLabel("Total terdeteksi: 0 aplikasi")
        self.lbl_summary.setStyleSheet("font-weight: bold; color: #1e293b;")
        footer.addWidget(self.lbl_summary)
        footer.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def start_scan(self):
        if not self.serial:
            self.lbl_status.setText("Tidak ada perangkat terhubung!")
            return

        self.btn_rescan.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Sedang memindai aplikasi pada perangkat...")
        self.table.setRowCount(0)

        self.scan_thread = AdwareScanThread(self.serial)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished_scan.connect(self.on_scan_finished)
        self.scan_thread.start()

    def on_scan_progress(self, cur: int, total: int, pkg: str):
        if total > 0:
            self.progress_bar.setValue(int((cur / total) * 100))
        self.lbl_status.setText(f"Memeriksa ({cur}/{total}): {pkg}")

    def on_scan_finished(self, results: List[Dict[str, Any]]):
        self.btn_rescan.setEnabled(True)
        self.scan_results = results
        self.progress_bar.setValue(100)
        self.lbl_status.setText("Pemindaian selesai!")

        crit_count = sum(1 for r in results if r.get("threat_assessment", {}).get("threat_level") == "CRITICAL")
        self.lbl_summary.setText(f"Ditemukan {len(results)} aplikasi beriklan ({crit_count} Ancaman Kritis Pop-up Layar Penuh)")

        self.table.setRowCount(len(results))
        for row, data in enumerate(results):
            pkg = data.get("package_name", "")
            threat = data.get("threat_assessment", {})
            lvl = threat.get("threat_level", "CLEAN")
            ads = data.get("ad_networks", [])
            ad_names = [a["name"] for a in ads]

            # 0. App Name & Package
            item_pkg = QTableWidgetItem(f"📦 {pkg}")
            item_pkg.setToolTip(f"Versi: {data.get('version_name', '-')} | Lokasi: {data.get('code_path', '-')}")
            self.table.setItem(row, 0, item_pkg)

            # 1. Threat Level
            item_lvl = QTableWidgetItem()
            if lvl == "CRITICAL":
                item_lvl.setText("🚨 KRITIS (Pop-up)")
                item_lvl.setForeground(QColor("#dc2626"))
                font = item_lvl.font()
                font.setBold(True)
                item_lvl.setFont(font)
            elif lvl == "HIGH":
                item_lvl.setText("⚠️ TINGGI")
                item_lvl.setForeground(QColor("#ea580c"))
            else:
                item_lvl.setText("🟡 SEDANG")
                item_lvl.setForeground(QColor("#ca8a04"))
            self.table.setItem(row, 1, item_lvl)

            # 2. Hijack Vector / Reason
            vectors = []
            if threat.get("has_reorder_tasks"):
                vectors.append("🔴 Bajak Layar (REORDER_TASKS)")
            if threat.get("has_overlay"):
                vectors.append("🟡 Overlay (SYSTEM_ALERT_WINDOW)")
            if threat.get("has_ime"):
                vectors.append("⌨ Keyboard Aktif")
            if threat.get("is_oem_adware"):
                vectors.append("🏢 Adware Sistem OEM")
            if threat.get("has_fgs"):
                vectors.append("⚡ Layanan Latar Belakang")

            vec_text = ", ".join(vectors) if vectors else "Iklan Biasa"
            item_vec = QTableWidgetItem(vec_text)
            verdicts_full = "\n".join(threat.get("verdicts", []))
            item_vec.setToolTip(verdicts_full or vec_text)
            self.table.setItem(row, 2, item_vec)

            # 3. Ad Networks
            ad_str = ", ".join(ad_names) if ad_names else "-"
            item_ads = QTableWidgetItem(ad_str)
            item_ads.setToolTip(ad_str)
            self.table.setItem(row, 3, item_ads)

            # 4. Actions Cell (Buttons)
            act_widget = QWidget()
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(4)

            btn_freeze = QPushButton("❄ Bekukan")
            btn_freeze.setStyleSheet("padding: 2px 6px; font-size: 10px;")
            btn_freeze.setToolTip("Nonaktifkan / bekukan aplikasi agar berhenti berjalan")
            btn_freeze.clicked.connect(lambda _, p=pkg: self.action_freeze(p))
            act_layout.addWidget(btn_freeze)

            btn_uninst = QPushButton("🗑️ Copot")
            btn_uninst.setStyleSheet("padding: 2px 6px; font-size: 10px; color: #dc2626;")
            btn_uninst.setToolTip("Copot pemasangan aplikasi (Uninstall)")
            btn_uninst.clicked.connect(lambda _, p=pkg: self.action_uninstall(p))
            act_layout.addWidget(btn_uninst)

            btn_det = QPushButton("🔍 Detail")
            btn_det.setStyleSheet("padding: 2px 6px; font-size: 10px;")
            btn_det.clicked.connect(lambda _, p=pkg: self.action_audit(p))
            act_layout.addWidget(btn_det)

            self.table.setCellWidget(row, 4, act_widget)

    def action_freeze(self, pkg: str):
        if not self.serial or not pkg:
            return
        if not confirm_two_step(self, "freeze", pkg, pkg, "Aplikasi akan dinonaktifkan sehingga tidak bisa memuat iklan."):
            return
        ok, out = adb_manager.disable_package(self.serial, pkg)
        if ok:
            QMessageBox.information(self, "Berhasil", f"Aplikasi {pkg} berhasil dibekukan/dinonaktifkan!")
            self.start_scan()
        else:
            # Fallback to user 0 uninstall if disable is rejected
            if "cannot disable" in out.lower():
                reply = QMessageBox.question(
                    self, "Gunakan Debloat User 0",
                    f"Sistem menolak penonaktifan standar ({out}).\n\nCopot aplikasi untuk User 0 (Debloat)?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.action_uninstall(pkg)
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal membekukan:\n{out}")

    def action_uninstall(self, pkg: str):
        if not self.serial or not pkg:
            return
        if not confirm_two_step(self, "uninstall", pkg, pkg, "Aplikasi adware ini akan dicopot secara permanen dari perangkat."):
            return
        # Try regular uninstall first
        ok, out = adb_manager.uninstall_package(self.serial, pkg)
        if not ok or "failure" in out.lower():
            # Try pm uninstall --user 0 for system/pre-installed apps
            from core.cmd_runner import cmd_runner
            ok, out = cmd_runner.run_adb(["shell", "pm", "uninstall", "--user", "0", pkg], serial=self.serial)

        if ok and ("success" in out.lower() or not out.strip()):
            QMessageBox.information(self, "Berhasil", f"Aplikasi {pkg} berhasil dicopot/dibersihkan dari perangkat!")
            self.start_scan()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal mencopot:\n{out}")

    def action_audit(self, pkg: str):
        if not self.serial or not pkg:
            return
        dlg = AppAuditDialog(self.serial, pkg, pkg, self)
        dlg.exec()

    def open_dns_dialog(self):
        dlg = AdBlockerDialog(self.serial, parent=self)
        dlg.exec()

    def switch_to_gboard(self):
        if not self.serial:
            return
        from core.cmd_runner import cmd_runner
        # Check if Gboard is available
        ok_en, out_en = cmd_runner.run_adb([
            "shell", "ime", "enable", "com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME"
        ], serial=self.serial)
        ok_set, out_set = cmd_runner.run_adb([
            "shell", "ime", "set", "com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME"
        ], serial=self.serial)

        if ok_set and "selected" in out_set.lower():
            # Disable facemoji keyboard if present
            cmd_runner.run_adb(["shell", "ime", "disable", "com.preff.kb.xm/com.preff.kb.LatinIME"], serial=self.serial)
            cmd_runner.run_adb(["shell", "am", "force-stop", "com.preff.kb.xm"], serial=self.serial)
            cmd_runner.run_adb(["shell", "cmd", "appops", "set", "com.preff.kb.xm", "RUN_IN_BACKGROUND", "ignore"], serial=self.serial)
            QMessageBox.information(
                self, "Berhasil",
                "✅ Keyboard default berhasil dialihkan ke Google Gboard!\n\n"
                "Keyboard Facemoji (penyebab iklan saat membuka chat/mengetik) telah dinonaktifkan."
            )
            self.start_scan()
        else:
            QMessageBox.warning(
                self, "Perhatian",
                f"Gboard tidak ditemukan atau gagal dialihkan:\n{out_set}\n\n"
                "Pastikan aplikasi Google Keyboard (Gboard) sudah terpasang di HP Anda."
            )
