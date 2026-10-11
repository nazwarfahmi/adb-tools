"""
App Audit & Detail Dialog module.
Provides an offcanvas-style comprehensive inspection of an Android app:
- Complete application metadata & technical specs
- Adware & Tracker SDK detection (AdMob, Unity, AppLovin, ironSource, etc.)
- Granular permissions audit with danger-level categorization and explanations
- Quick actions (Launch, Freeze/Enable, Backup APK, Clear Data, Uninstall)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QWidget, QMessageBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFrame, QFileDialog, QApplication, QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QFont, QPixmap

from core.app_audit_service import audit_package
from core.adb_manager import adb_manager
from core.icon_service import icon_service
from ui.dialogs.confirm_dialog import confirm_two_step
from ui.dialogs.ad_blocker_dialog import AdBlockerDialog
from ui.style import styled_btn


class AuditLoadWorker(QThread):
    finished = Signal(dict)

    def __init__(self, serial: str, package_name: str):
        super().__init__()
        self.serial = serial
        self.package_name = package_name

    def run(self):
        result = audit_package(self.serial, self.package_name)
        self.finished.emit(result)


class AppAuditDialog(QDialog):
    def __init__(self, serial: str, package_name: str, app_name: str = "", parent=None):
        super().__init__(parent)
        self.serial = serial
        self.package_name = package_name
        self.app_name = app_name or package_name
        self.audit_data = {}
        self.all_perms = []

        self.setWindowTitle(f"Detail & Audit Aplikasi: {self.app_name}")
        self.resize(860, 620)
        self.setMinimumSize(740, 520)

        self.init_ui()
        self.load_audit_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(10)

        # -------------------------------------------------------------
        # 1. HEADER CARD (App Icon + Titles + Quick Badges)
        # -------------------------------------------------------------
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_card.setStyleSheet(
            "QFrame#headerCard { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; }"
        )
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(4, 4, 4, 4)
        h_layout.setSpacing(12)

        # 48x48 Icon Badge
        self.lbl_icon = QLabel()
        self.lbl_icon.setFixedSize(48, 48)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        icon_pm = icon_service.get_icon(self.package_name, self.app_name)
        if not icon_pm.isNull():
            scaled = icon_pm.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_icon.setPixmap(scaled)
        h_layout.addWidget(self.lbl_icon)

        # App Name & Package
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_app_title = QLabel(self.app_name)
        self.lbl_app_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        title_box.addWidget(self.lbl_app_title)

        self.lbl_pkg_name = QLabel(self.package_name)
        self.lbl_pkg_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_pkg_name.setStyleSheet("font-size: 11px; color: #64748b; font-family: monospace;")
        title_box.addWidget(self.lbl_pkg_name)

        # Quick Badges Row
        self.badge_box = QHBoxLayout()
        self.badge_box.setSpacing(6)
        self.lbl_badge_ver = self._create_badge("Memuat versi...", "#f1f5f9", "#475569")
        self.lbl_badge_type = self._create_badge("Tipe...", "#f1f5f9", "#475569")
        self.lbl_badge_state = self._create_badge("Status...", "#f1f5f9", "#475569")
        self.lbl_badge_size = self._create_badge("Ukuran...", "#f1f5f9", "#475569")

        self.badge_box.addWidget(self.lbl_badge_ver)
        self.badge_box.addWidget(self.lbl_badge_type)
        self.badge_box.addWidget(self.lbl_badge_state)
        self.badge_box.addWidget(self.lbl_badge_size)
        self.badge_box.addStretch()
        title_box.addLayout(self.badge_box)

        h_layout.addLayout(title_box, 1)
        main_layout.addWidget(header_card)

        # Progress bar during initial load
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setVisible(True)
        main_layout.addWidget(self.progress_bar)

        # -------------------------------------------------------------
        # 2. TABS: (Ad & Tracker Audit, Permissions Audit, Technical Details)
        # -------------------------------------------------------------
        self.tabs = QTabWidget()

        # Tab 1: Adware & Tracker Audit
        self.tab_ads = QWidget()
        self.setup_ads_tab(self.tab_ads)
        self.tabs.addTab(self.tab_ads, "🛡️  Deteksi Iklan & Pelacak")

        # Tab 2: Permissions Audit
        self.tab_perms = QWidget()
        self.setup_perms_tab(self.tab_perms)
        self.tabs.addTab(self.tab_perms, "🔑  Audit Izin Aplikasi")

        # Tab 3: Technical Details
        self.tab_tech = QWidget()
        self.setup_tech_tab(self.tab_tech)
        self.tabs.addTab(self.tab_tech, "📋  Informasi Teknis Lengkap")

        main_layout.addWidget(self.tabs, 1)

        # -------------------------------------------------------------
        # 3. ACTION BUTTONS (BOTTOM FOOTER)
        # -------------------------------------------------------------
        footer_row = QHBoxLayout()
        footer_row.setSpacing(6)

        btn_launch = QPushButton("🚀 Buka")
        btn_launch.setToolTip("Jalankan aplikasi di layar HP")
        btn_launch.clicked.connect(self.action_launch)
        footer_row.addWidget(btn_launch)

        self.btn_freeze = QPushButton("❄ Bekukan")
        self.btn_freeze.clicked.connect(self.action_toggle_freeze)
        footer_row.addWidget(self.btn_freeze)

        btn_backup = QPushButton("📂 Backup APK")
        btn_backup.setToolTip("Tarik dan simpan file .apk aplikasi ke komputer")
        btn_backup.clicked.connect(self.action_backup)
        footer_row.addWidget(btn_backup)

        btn_clear = QPushButton("🧹 Hapus Data")
        btn_clear.setToolTip("Bersihkan cache dan reset data user aplikasi")
        btn_clear.clicked.connect(self.action_clear_data)
        footer_row.addWidget(btn_clear)

        btn_uninstall = styled_btn("🗑 Uninstall", "danger")
        btn_uninstall.setToolTip("Copot pemasangan aplikasi dari user 0")
        btn_uninstall.clicked.connect(self.action_uninstall)
        footer_row.addWidget(btn_uninstall)

        footer_row.addStretch()

        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        footer_row.addWidget(btn_close)

        main_layout.addLayout(footer_row)

    def _create_badge(self, text: str, bg: str, fg: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"background-color: {bg}; color: {fg}; font-size: 10px; font-weight: 600; "
            f"padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.06);"
        )
        return lbl

    # -------------------------------------------------------------
    # SETUP TAB 1: ADWARE & TRACKERS
    # -------------------------------------------------------------
    def setup_ads_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Prominent Result Banner
        self.banner_ads = QFrame()
        self.banner_ads.setObjectName("bannerAds")
        self.banner_ads.setStyleSheet(
            "QFrame#bannerAds { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; }"
        )
        ban_layout = QHBoxLayout(self.banner_ads)
        ban_layout.setContentsMargins(4, 4, 4, 4)

        self.lbl_ad_icon = QLabel("🔍")
        self.lbl_ad_icon.setStyleSheet("font-size: 24px;")
        ban_layout.addWidget(self.lbl_ad_icon)

        self.lbl_ad_summary = QLabel("Sedang memindai komponen aplikasi untuk mendeteksi modul iklan dan pelacak...")
        self.lbl_ad_summary.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        self.lbl_ad_summary.setWordWrap(True)
        ban_layout.addWidget(self.lbl_ad_summary, 1)

        self.btn_open_adblock = styled_btn("🛡️ Solusi Hilangkan Iklan", "primary")
        self.btn_open_adblock.setToolTip("Buka solusi praktis & pemblokir iklan (Private DNS, Cache Reset, Mode Offline)")
        self.btn_open_adblock.clicked.connect(self.open_ad_blocker_dialog)
        ban_layout.addWidget(self.btn_open_adblock)

        layout.addWidget(self.banner_ads)

        # Table of Detected Ad Networks & Trackers
        self.table_ads = QTableWidget()
        self.table_ads.setColumnCount(4)
        self.table_ads.setHorizontalHeaderLabels(["Nama SDK / Jaringan", "Kategori", "Deskripsi", "Komponen Terdeteksi"])
        self.table_ads.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_ads.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_ads.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table_ads.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_ads.setColumnWidth(2, 220)
        self.table_ads.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_ads.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_ads)

    def open_ad_blocker_dialog(self):
        dlg = AdBlockerDialog(self.serial, self.package_name, self.app_name, self)
        dlg.exec()

    # -------------------------------------------------------------
    # SETUP TAB 2: PERMISSIONS AUDIT
    # -------------------------------------------------------------
    def setup_perms_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Summary Bar (Counts)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        self.lbl_stat_dang = self._create_badge("0 Izin Berbahaya", "#fef2f2", "#b91c1c")
        self.lbl_stat_spec = self._create_badge("0 Akses Khusus", "#fffbeb", "#b45309")
        self.lbl_stat_norm = self._create_badge("0 Izin Normal", "#f0fdf4", "#15803d")
        self.lbl_stat_grant = self._create_badge("0 Diberikan", "#eff6ff", "#1d4ed8")

        stats_row.addWidget(self.lbl_stat_dang)
        stats_row.addWidget(self.lbl_stat_spec)
        stats_row.addWidget(self.lbl_stat_norm)
        stats_row.addWidget(self.lbl_stat_grant)
        stats_row.addStretch()

        self.txt_perm_search = QLineEdit()
        self.txt_perm_search.setPlaceholderText("🔍 Cari nama izin...")
        self.txt_perm_search.setFixedWidth(180)
        self.txt_perm_search.textChanged.connect(self.filter_perms_table)
        stats_row.addWidget(self.txt_perm_search)

        layout.addLayout(stats_row)

        # Permissions Table
        self.table_perms = QTableWidget()
        self.table_perms.setColumnCount(4)
        self.table_perms.setHorizontalHeaderLabels(["Status", "Nama Izin", "Tingkat Risiko", "Fungsi & Penjelasan"])
        self.table_perms.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_perms.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table_perms.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_perms.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_perms.setColumnWidth(1, 200)
        self.table_perms.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_perms.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_perms)

    # -------------------------------------------------------------
    # SETUP TAB 3: TECHNICAL DETAILS
    # -------------------------------------------------------------
    def setup_tech_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.table_tech = QTableWidget()
        self.table_tech.setColumnCount(2)
        self.table_tech.setHorizontalHeaderLabels(["Parameter Sistem", "Nilai / Informasi"])
        self.table_tech.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table_tech.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_tech.setColumnWidth(0, 220)
        self.table_tech.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_tech.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_tech)

    # -------------------------------------------------------------
    # LOAD AUDIT DATA ASYNCHRONOUSLY
    # -------------------------------------------------------------
    def load_audit_data(self):
        worker = AuditLoadWorker(self.serial, self.package_name)
        worker.finished.connect(self.on_audit_finished)
        worker.start()
        self._worker = worker

    def on_audit_finished(self, data: dict):
        self.progress_bar.setVisible(False)
        self.audit_data = data

        if "error" in data:
            QMessageBox.warning(self, "Audit Gagal", data["error"])
            return

        # 1. Update Header Badges
        v_name = data.get("version_name", "-")
        v_code = data.get("version_code", "-")
        self.lbl_badge_ver.setText(f"📦 v{v_name} ({v_code})")
        self.lbl_badge_ver.setStyleSheet("background-color: #eff6ff; color: #1d4ed8; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")

        is_sys = data.get("is_system", False)
        self.lbl_badge_type.setText("Sistem" if is_sys else "Pengguna (3rd-party)")
        self.lbl_badge_type.setStyleSheet("background-color: #f1f5f9; color: #475569; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")

        is_dis = data.get("is_disabled", False)
        if is_dis:
            self.lbl_badge_state.setText("❄️ Dibekukan")
            self.lbl_badge_state.setStyleSheet("background-color: #e0f2fe; color: #0284c7; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")
            self.btn_freeze.setText("⚡ Aktifkan")
        else:
            self.lbl_badge_state.setText("✅ Aktif")
            self.lbl_badge_state.setStyleSheet("background-color: #f0fdf4; color: #15803d; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")
            self.btn_freeze.setText("❄ Bekukan")

        apk_sz = data.get("apk_size", "-")
        self.lbl_badge_size.setText(f"💾 {apk_sz}")
        self.lbl_badge_size.setStyleSheet("background-color: #faf5ff; color: #7e22ce; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")

        # 2. Populate Tab 1: Adware & Trackers
        ads = data.get("ad_networks", [])
        trackers = data.get("trackers", [])
        total_threats = len(ads) + len(trackers)
        has_overlay = any(p.get("name") == "android.permission.SYSTEM_ALERT_WINDOW" for p in data.get("permissions_list", []))

        if total_threats > 0:
            self.lbl_ad_icon.setText("🚨" if (has_overlay and ads) else "⚠️")
            ad_text = f"Terdeteksi {len(ads)} Jaringan Iklan" if ads else ""
            tr_text = f"{len(trackers)} Pelacak Aktif" if trackers else ""
            sep = " dan " if ads and trackers else ""
            if has_overlay and ads:
                warning_extra = "\n🚨 INDIKASI ADWARE POP-UP: Aplikasi ini memiliki modul iklan DAN izin 'Tampilkan di atas aplikasi lain' (Overlay)! Ini adalah penyebab paling umum iklan pop-up tiba-tiba muncul satu layar penuh saat pengguna sedang membuka aplikasi lain atau berada di layar utama."
                bg_col = "#fef2f2"
                border_col = "#fca5a5"
                text_col = "#991b1b"
            else:
                warning_extra = "\nModul komersial ini dapat memuat banner/iklan pop-up dan mengumpulkan data penggunaan."
                bg_col = "#fffbeb"
                border_col = "#fcd34d"
                text_col = "#b45309"

            self.lbl_ad_summary.setText(f"Perhatian: {ad_text}{sep}{tr_text} di dalam aplikasi ini!{warning_extra}")
            self.banner_ads.setStyleSheet(f"QFrame#bannerAds {{ background-color: {bg_col}; border: 1px solid {border_col}; border-radius: 6px; padding: 10px; }}")
            self.lbl_ad_summary.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {text_col};")
        else:
            self.lbl_ad_icon.setText("✅")
            self.lbl_ad_summary.setText("Aplikasi Bersih: Bebas Iklan & Pelacak!\nTidak ditemukan SDK iklan pihak ketiga (AdMob, Unity, AppLovin, dll) maupun pelacak analitik.")
            self.banner_ads.setStyleSheet("QFrame#bannerAds { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px; }")
            self.lbl_ad_summary.setStyleSheet("font-size: 12px; font-weight: 600; color: #15803d;")

        all_threats = ads + trackers
        self.table_ads.setRowCount(len(all_threats))
        for row, item in enumerate(all_threats):
            self.table_ads.setItem(row, 0, QTableWidgetItem(f"🎯 {item['name']}"))
            self.table_ads.setItem(row, 1, QTableWidgetItem(item["category"]))
            self.table_ads.setItem(row, 2, QTableWidgetItem(item["description"]))
            ev_item = QTableWidgetItem(item["evidence"])
            ev_item.setToolTip(item["evidence"])
            self.table_ads.setItem(row, 3, ev_item)

        # 3. Populate Tab 2: Permissions
        self.all_perms = data.get("permissions_list", [])
        summary = data.get("permissions_summary", {})
        self.lbl_stat_dang.setText(f"🔴 {summary.get('dangerous_count', 0)} Izin Berbahaya")
        self.lbl_stat_spec.setText(f"🟡 {summary.get('special_count', 0)} Akses Khusus")
        self.lbl_stat_norm.setText(f"🟢 {summary.get('normal_count', 0)} Izin Normal")
        self.lbl_stat_grant.setText(f"✓ {summary.get('granted_count', 0)} Diberikan")

        self.filter_perms_table()

        # 4. Populate Tab 3: Technical Details
        comp = data.get("components_count", {})
        tech_rows = [
            ("Nama Package", data.get("package_name", "-")),
            ("Nama Aplikasi", self.app_name),
            ("Versi Aplikasi (Version Name)", f"{data.get('version_name', '-')} (Version Code: {data.get('version_code', '-')})"),
            ("Target SDK Android", f"API {data.get('target_sdk', '-')} (Min SDK: API {data.get('min_sdk', '-')})"),
            ("Waktu Pemasangan Pertama", data.get("first_install_time", "-")),
            ("Waktu Pembaruan Terakhir", data.get("last_update_time", "-")),
            ("Sumber Penginstalan (Installer)", data.get("installer", "-")),
            ("Lokasi Berkas APK", data.get("code_path", "-")),
            ("Ukuran File APK", data.get("apk_size", "-")),
            ("Direktori Data Pengguna", data.get("data_dir", "-")),
            ("User ID (UID)", data.get("uid", "-")),
            ("Status Sistem", "Aplikasi Sistem (Pre-installed)" if is_sys else "Aplikasi Pengguna (3rd-party)"),
            ("Status Aktivitas", "Dibekukan (Disabled)" if is_dis else "Aktif Berjalan (Enabled)"),
            ("Jumlah Komponen", f"{comp.get('activities', 0)} Activities, {comp.get('services', 0)} Services, {comp.get('receivers', 0)} Receivers, {comp.get('providers', 0)} Providers"),
        ]
        self.table_tech.setRowCount(len(tech_rows))
        for r, (param, val) in enumerate(tech_rows):
            p_item = QTableWidgetItem(param)
            p_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            v_item = QTableWidgetItem(str(val))
            v_item.setToolTip(str(val))
            self.table_tech.setItem(r, 0, p_item)
            self.table_tech.setItem(r, 1, v_item)

    def filter_perms_table(self):
        query = self.txt_perm_search.text().strip().lower()
        filtered = [
            p for p in self.all_perms
            if query in p["name"].lower() or query in p["permission"].lower() or query in p["description"].lower()
        ]

        self.table_perms.setRowCount(len(filtered))
        for row, p in enumerate(filtered):
            # Status: Granted or Denied
            is_grant = p["granted"]
            status_text = "✅ Diberikan" if is_grant else "❌ Ditolak"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#15803d" if is_grant else "#94a3b8"))

            name_item = QTableWidgetItem(p["name"])
            name_item.setToolTip(p["permission"])

            risk_item = QTableWidgetItem(p["danger_level"])
            desc_item = QTableWidgetItem(p["description"])
            desc_item.setToolTip(f"Izin teknis: {p['permission']}\n{p['description']}")

            self.table_perms.setItem(row, 0, status_item)
            self.table_perms.setItem(row, 1, name_item)
            self.table_perms.setItem(row, 2, risk_item)
            self.table_perms.setItem(row, 3, desc_item)

    # -------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------
    def action_launch(self):
        ok, out = adb_manager.launch_app(self.serial, self.package_name)
        if ok:
            QMessageBox.information(self, "Aplikasi Dibuka", f"Membuka {self.app_name} di layar HP.")
        else:
            QMessageBox.warning(self, "Gagal Membuka", f"Gagal membuka aplikasi:\n{out}")

    def action_toggle_freeze(self):
        is_dis = self.audit_data.get("is_disabled", False)
        if is_dis:
            reply = QMessageBox.question(
                self, "Konfirmasi Aktifkan",
                f"Aktifkan kembali aplikasi <b>{self.app_name}</b>?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            if reply != QMessageBox.Yes:
                return
            ok, out = adb_manager.enable_package(self.serial, self.package_name)
            action_name = "diaktifkan"
        else:
            is_sys = self.audit_data.get("is_system", False)
            if not confirm_two_step(self, "freeze", self.app_name, self.package_name, is_critical_system=is_sys):
                return
            ok, out = adb_manager.disable_package(self.serial, self.package_name)
            action_name = "dibekukan"

        if ok:
            QMessageBox.information(self, "Berhasil", f"Aplikasi berhasil {action_name}.")
            self.load_audit_data()
        else:
            QMessageBox.warning(self, "Gagal", f"Gagal memproses:\n{out}")

    def action_backup(self):
        code_path = self.audit_data.get("code_path", "")
        if not code_path or code_path == "-":
            ok, out = adb_manager.run_adb(["shell", "pm", "path", self.package_name], serial=self.serial)
            if ok and "package:" in out:
                code_path = out.split("package:", 1)[1].strip().splitlines()[0].strip()
        if code_path and not code_path.endswith(".apk"):
            code_path = f"{code_path}/base.apk"

        if not code_path:
            QMessageBox.warning(self, "Backup Gagal", "Jalur file APK tidak ditemukan pada perangkat.")
            return

        default_name = f"{self.package_name}.apk"
        dest_path, _ = QFileDialog.getSaveFileName(self, "Simpan File APK", default_name, "Android Package (*.apk)")
        if not dest_path:
            return

        ok, out = adb_manager.pull_apk(self.serial, code_path, dest_path)
        if ok:
            QMessageBox.information(self, "Backup Selesai", f"File APK berhasil disimpan ke:\n{dest_path}")
        else:
            QMessageBox.warning(self, "Backup Gagal", f"Gagal backup APK:\n{out}")

    def action_clear_data(self):
        if not confirm_two_step(self, "clear_data", self.app_name, self.package_name):
            return
        ok, out = adb_manager.clear_package_data(self.serial, self.package_name)
        if ok:
            QMessageBox.information(self, "Berhasil", "Data aplikasi berhasil dibersihkan.")
        else:
            QMessageBox.warning(self, "Gagal", f"Gagal menghapus data:\n{out}")

    def action_uninstall(self):
        is_sys = self.audit_data.get("is_system", False)
        if not confirm_two_step(self, "uninstall", self.app_name, self.package_name, is_critical_system=is_sys):
            return
        ok, out = adb_manager.uninstall_package(self.serial, self.package_name)
        if ok:
            QMessageBox.information(self, "Uninstall Selesai", f"{self.app_name} berhasil dicopot.")
            self.accept()
        else:
            QMessageBox.warning(self, "Uninstall Gagal", f"Gagal mencopot aplikasi:\n{out}")
