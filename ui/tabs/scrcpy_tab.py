import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox,
    QProgressBar, QLineEdit, QFrame, QGridLayout, QTabWidget
)
from PySide6.QtCore import Qt
from core.scrcpy_manager import (
    scrcpy_manager, ScrcpyReleasesWorker, ScrcpyVersionDownloadWorker,
    DEFAULT_SCRCPY_RELEASES
)
from core.settings import settings
from ui.style import styled_btn

class ScrcpyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.releases_data = list(DEFAULT_SCRCPY_RELEASES)
        self.releases_worker = None
        self.download_worker = None

        # Load cache if available
        cache_file = Path(__file__).resolve().parent.parent.parent / "data" / "scrcpy_releases.json"
        if cache_file.exists():
            try:
                import json
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached:
                        self.releases_data = cached
            except Exception:
                pass

        self.init_ui()
        self.populate_versions_dropdown()
        self.update_status()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Tab Widget separating Mirroring vs Version Management
        self.sub_tabs = QTabWidget()

        # 1. Sub-Tab: Screen Mirror Control
        tab_mirror = QWidget()
        self.setup_mirror_tab(tab_mirror)
        self.sub_tabs.addTab(tab_mirror, "🖥️  Kontrol Screen Mirror")

        # 2. Sub-Tab: Version Management
        tab_version = QWidget()
        self.setup_version_tab(tab_version)
        self.sub_tabs.addTab(tab_version, "🛠️  Manajemen Versi Scrcpy")

        main_layout.addWidget(self.sub_tabs)

        # Listen to manager signals
        scrcpy_manager.process_started.connect(self.on_mirror_started)
        scrcpy_manager.process_ended.connect(self.on_mirror_stopped)

    # -------------------------------------------------------------
    # 1. SUB-TAB: SCREEN MIRROR CONTROL
    # -------------------------------------------------------------
    def setup_mirror_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Launch & Status Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.lbl_bin_status = QLabel("Memeriksa status Scrcpy...")
        self.lbl_bin_status.setStyleSheet("font-weight: 600; font-size: 11px;")
        top_bar.addWidget(self.lbl_bin_status)

        self.lbl_active_info = QLabel("")
        self.lbl_active_info.setStyleSheet("color: #0284c7; font-size: 11px; font-weight: 600;")
        top_bar.addWidget(self.lbl_active_info)

        top_bar.addStretch()

        self.btn_start = styled_btn("🚀 Mulai Screen Mirror", "primary")
        self.btn_start.setFixedHeight(26)
        self.btn_start.clicked.connect(self.start_mirror)

        self.btn_stop = styled_btn("🛑 Hentikan Mirror", "danger")
        self.btn_stop.setFixedHeight(26)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_mirror)

        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_stop)
        layout.addLayout(top_bar)

        # Display & Streaming Quality Card
        opt_box = QGroupBox("⚙️ Kualitas Layar && Video Streaming")
        opt_layout = QHBoxLayout(opt_box)
        opt_layout.setContentsMargins(8, 8, 8, 8)
        opt_layout.setSpacing(10)

        # Resolution
        col_res = QVBoxLayout()
        col_res.setSpacing(3)
        lbl_res = QLabel("Resolusi Maksimal:")
        lbl_res.setStyleSheet("color: #64748b; font-size: 11px;")
        self.cb_res = QComboBox()
        self.cb_res.addItems(["Native (Default)", "720p (Cepat)", "1080p (FHD)", "1440p (2K)"])
        self.cb_res.setCurrentIndex(2)
        col_res.addWidget(lbl_res)
        col_res.addWidget(self.cb_res)
        opt_layout.addLayout(col_res)

        # Bitrate
        col_bit = QVBoxLayout()
        col_bit.setSpacing(3)
        lbl_bit = QLabel("Bitrate Video:")
        lbl_bit.setStyleSheet("color: #64748b; font-size: 11px;")
        self.cb_bit = QComboBox()
        self.cb_bit.addItems(["Default (8M)", "2 Mbps (Hemat Kuota)", "4 Mbps", "8 Mbps (Rekomendasi)", "16 Mbps (High Quality)", "24 Mbps"])
        self.cb_bit.setCurrentIndex(3)
        col_bit.addWidget(lbl_bit)
        col_bit.addWidget(self.cb_bit)
        opt_layout.addLayout(col_bit)

        # Framerate
        col_fps = QVBoxLayout()
        col_fps.setSpacing(3)
        lbl_fps = QLabel("Framerate Maksimal:")
        lbl_fps.setStyleSheet("color: #64748b; font-size: 11px;")
        self.cb_fps = QComboBox()
        self.cb_fps.addItems(["Default", "30 FPS", "60 FPS (Halus)", "120 FPS"])
        self.cb_fps.setCurrentIndex(2)
        col_fps.addWidget(lbl_fps)
        col_fps.addWidget(self.cb_fps)
        opt_layout.addLayout(col_fps)

        layout.addWidget(opt_box)

        # Mirror Behavior Switches Card
        beh_box = QGroupBox("🎮 Perilaku && Interaksi Perangkat")
        beh_layout = QVBoxLayout(beh_box)
        beh_layout.setContentsMargins(8, 8, 8, 8)
        beh_layout.setSpacing(6)

        chk_grid = QGridLayout()
        chk_grid.setHorizontalSpacing(16)
        chk_grid.setVerticalSpacing(5)

        self.chk_stay_awake = QCheckBox("Cegah Layar HP Mati (--stay-awake)")
        self.chk_stay_awake.setChecked(True)
        self.chk_screen_off = QCheckBox("Matikan Layar Fisik HP saat Mirroring (--turn-screen-off)")
        self.chk_no_audio = QCheckBox("Bisukan Suara HP (--no-audio)")
        self.chk_always_top = QCheckBox("Jendela Selalu di Atas (--always-on-top)")
        self.chk_fullscreen = QCheckBox("Mode Layar Penuh (--fullscreen)")
        self.chk_touches = QCheckBox("Tampilkan Titik Sentuhan (--show-touches)")
        self.chk_otg = QCheckBox("Mode OTG (Kontrol Keyboard / Mouse langsung)")

        chk_grid.addWidget(self.chk_stay_awake, 0, 0)
        chk_grid.addWidget(self.chk_screen_off, 1, 0)
        chk_grid.addWidget(self.chk_no_audio, 2, 0)
        chk_grid.addWidget(self.chk_always_top, 0, 1)
        chk_grid.addWidget(self.chk_fullscreen, 1, 1)
        chk_grid.addWidget(self.chk_touches, 2, 1)
        chk_grid.addWidget(self.chk_otg, 3, 0, 1, 2)
        beh_layout.addLayout(chk_grid)

        layout.addWidget(beh_box)

        # Recording Section Card
        rec_box = QGroupBox("🎥 Perekaman Layar (Simpan ke File .MP4)")
        rec_layout = QHBoxLayout(rec_box)
        rec_layout.setContentsMargins(8, 8, 8, 8)
        rec_layout.setSpacing(8)

        self.chk_record = QCheckBox("Rekam Sesi Mirror:")
        self.chk_record.toggled.connect(self.on_record_toggled)

        self.txt_rec_path = QLineEdit()
        self.txt_rec_path.setPlaceholderText("Lokasi file rekaman (contoh: D:\\rekaman.mp4)...")
        self.txt_rec_path.setEnabled(False)

        self.btn_rec_browse = QPushButton("📁 Pilih Lokasi...")
        self.btn_rec_browse.setEnabled(False)
        self.btn_rec_browse.clicked.connect(self.browse_record_file)

        rec_layout.addWidget(self.chk_record)
        rec_layout.addWidget(self.txt_rec_path, 1)
        rec_layout.addWidget(self.btn_rec_browse)
        layout.addWidget(rec_box)

        layout.addStretch()

    # -------------------------------------------------------------
    # 2. SUB-TAB: VERSION MANAGEMENT
    # -------------------------------------------------------------
    def setup_version_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Versions Selector Card
        ver_box = QGroupBox("📦 Pilihan Versi Scrcpy")
        ver_layout = QVBoxLayout(ver_box)
        ver_layout.setContentsMargins(8, 8, 8, 8)
        ver_layout.setSpacing(8)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        lbl_ver = QLabel("Pilih Versi:")
        lbl_ver.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        row1.addWidget(lbl_ver)

        self.cb_versions = QComboBox()
        self.cb_versions.currentIndexChanged.connect(self.on_version_selected)
        row1.addWidget(self.cb_versions, 1)

        self.btn_use_ver = styled_btn("✔ Gunakan Versi Ini", "primary")
        self.btn_use_ver.clicked.connect(self.use_selected_version)
        row1.addWidget(self.btn_use_ver)

        self.btn_download_ver = QPushButton("⬇ Unduh Versi")
        self.btn_download_ver.clicked.connect(self.download_selected_version)
        row1.addWidget(self.btn_download_ver)
        ver_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        self.btn_refresh_releases = QPushButton("🔄 Periksa Rilis GitHub Terbaru")
        self.btn_refresh_releases.clicked.connect(lambda: self.fetch_github_releases(silent=False))
        row2.addWidget(self.btn_refresh_releases)

        self.btn_browse_custom = QPushButton("📁 Pilih Custom scrcpy.exe...")
        self.btn_browse_custom.clicked.connect(self.browse_scrcpy)
        row2.addWidget(self.btn_browse_custom)
        row2.addStretch()
        ver_layout.addLayout(row2)

        # Download progress
        self.dl_progress = QProgressBar()
        self.dl_progress.setVisible(False)
        self.dl_progress.setFixedHeight(6)
        ver_layout.addWidget(self.dl_progress)

        layout.addWidget(ver_box)

        # Active Engine Information Card
        info_box = QGroupBox("ℹ️ Informasi Engine Aktif")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(4)

        self.lbl_bin_path = QLabel("")
        self.lbl_bin_path.setStyleSheet("color: #475569; font-size: 11px;")
        self.lbl_bin_path.setWordWrap(True)
        info_layout.addWidget(self.lbl_bin_path)

        layout.addWidget(info_box)
        layout.addStretch()

    # -------------------------------------------------------------
    # LOGIC & SLOTS
    # -------------------------------------------------------------
    def set_device(self, serial: str):
        self.current_serial = serial

    def fetch_github_releases(self, silent: bool = False):
        if not silent:
            self.lbl_bin_path.setText("Memeriksa rilis terbaru dari GitHub...")
        self.releases_worker = ScrcpyReleasesWorker()
        self.releases_worker.releases_loaded.connect(lambda rel, from_gh, msg: self.on_releases_loaded(rel, from_gh, msg, silent))
        self.releases_worker.start()

    def on_releases_loaded(self, releases: list, from_github: bool, message: str, silent: bool):
        if releases:
            self.releases_data = releases
            self.populate_versions_dropdown()
            self.update_status()
            if not silent:
                QMessageBox.information(self, "GitHub Releases", message)

    def populate_versions_dropdown(self):
        self.cb_versions.blockSignals(True)
        self.cb_versions.clear()

        installed = scrcpy_manager.get_installed_versions()
        active_path = settings.get("scrcpy_path") or ""
        norm_active = os.path.normpath(active_path).lower() if active_path else ""

        for rel in self.releases_data:
            tag = rel["tag"]
            name = rel.get("name", tag)
            size = rel.get("size_mb", 0)

            is_downloaded = tag in installed
            inst_path = installed.get(tag, "")
            is_active = False
            if inst_path and norm_active and os.path.normpath(inst_path).lower() == norm_active:
                is_active = True

            if is_active:
                display_text = f"⭐ {tag} ({name}) [AKTIF]"
            elif is_downloaded:
                display_text = f"✅ {tag} ({name}) [Terinstal]"
            else:
                display_text = f"⬇ {tag} ({name} - {size} MB) [Belum Diunduh]"

            self.cb_versions.addItem(display_text, {
                "tag": tag,
                "url": rel.get("url"),
                "is_downloaded": is_downloaded,
                "is_active": is_active,
                "local_path": inst_path
            })

        if "Custom" in installed:
            custom_path = installed["Custom"]
            is_active = (norm_active and os.path.normpath(custom_path).lower() == norm_active)
            prefix = "⭐" if is_active else "📁"
            self.cb_versions.addItem(f"{prefix} Custom ({custom_path})", {
                "tag": "Custom",
                "url": None,
                "is_downloaded": True,
                "is_active": is_active,
                "local_path": custom_path
            })

        selected_idx = 0
        for i in range(self.cb_versions.count()):
            data = self.cb_versions.itemData(i)
            if data and data.get("is_active"):
                selected_idx = i
                break
        self.cb_versions.setCurrentIndex(selected_idx)
        self.cb_versions.blockSignals(False)

        self.on_version_selected(selected_idx)

    def on_version_selected(self, index: int):
        data = self.cb_versions.itemData(index)
        if not data:
            return

        is_downloaded = data.get("is_downloaded", False)
        is_active = data.get("is_active", False)
        tag = data.get("tag", "")

        if is_active:
            self.btn_use_ver.setEnabled(False)
            self.btn_use_ver.setText("✔ Sedang Aktif")
            self.btn_download_ver.setEnabled(True)
            self.btn_download_ver.setText("⬇ Unduh Ulang")
        elif is_downloaded:
            self.btn_use_ver.setEnabled(True)
            self.btn_use_ver.setText("✔ Gunakan Versi Ini")
            self.btn_download_ver.setEnabled(True)
            self.btn_download_ver.setText("⬇ Unduh Ulang")
        else:
            self.btn_use_ver.setEnabled(False)
            self.btn_use_ver.setText("✔ Gunakan Versi Ini")
            self.btn_download_ver.setEnabled(True)
            self.btn_download_ver.setText(f"⬇ Unduh {tag}")

    def use_selected_version(self):
        data = self.cb_versions.currentData()
        if not data:
            return

        local_path = data.get("local_path")
        tag = data.get("tag", "")

        if local_path and os.path.isfile(local_path):
            scrcpy_manager.set_active_version_path(local_path)
            self.populate_versions_dropdown()
            self.update_status()
            QMessageBox.information(self, "Scrcpy Aktif", f"Scrcpy versi {tag} berhasil diaktifkan sebagai engine utama!")
        else:
            QMessageBox.warning(self, "File Tidak Ditemukan", f"File scrcpy.exe untuk versi {tag} tidak ditemukan.")

    def download_selected_version(self):
        data = self.cb_versions.currentData()
        if not data:
            return

        tag = data.get("tag")
        url = data.get("url")

        if not url:
            QMessageBox.warning(self, "Download Error", f"URL unduhan untuk {tag} tidak tersedia.")
            return

        self.dl_progress.setVisible(True)
        self.dl_progress.setValue(0)
        self.btn_download_ver.setEnabled(False)
        self.btn_use_ver.setEnabled(False)
        self.lbl_bin_status.setText(f"Mengunduh Scrcpy {tag} dari GitHub...")

        self.download_worker = ScrcpyVersionDownloadWorker(tag, url)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.finished_download.connect(self.on_download_finished)
        self.download_worker.start()

    def on_download_progress(self, percent: int, status_msg: str):
        self.dl_progress.setValue(percent)
        self.lbl_bin_path.setText(status_msg)

    def on_download_finished(self, success: bool, tag: str, path_or_err: str):
        self.dl_progress.setVisible(False)
        self.btn_download_ver.setEnabled(True)

        if success:
            self.populate_versions_dropdown()
            self.update_status()
            QMessageBox.information(self, "Unduhan Selesai", f"Scrcpy {tag} berhasil diunduh dan langsung diaktifkan!")
        else:
            self.update_status()
            QMessageBox.critical(self, "Unduhan Gagal", f"Gagal mengunduh Scrcpy {tag}:\n{path_or_err}")

    def update_status(self):
        installed = scrcpy_manager.is_installed()
        bin_path = scrcpy_manager.scrcpy_bin

        if installed:
            self.lbl_bin_status.setText("🟢 Scrcpy Siap")
            self.lbl_bin_status.setStyleSheet("color: #16a34a; font-weight: 600; font-size: 11px;")
            self.lbl_bin_path.setText(f"File Executable Aktif:\n{bin_path}")

            tag_name = ""
            for i in range(self.cb_versions.count()):
                d = self.cb_versions.itemData(i)
                if d and d.get("is_active"):
                    tag_name = d.get("tag", "")
                    break
            self.lbl_active_info.setText(f"Versi: {tag_name or 'Custom'}")
        else:
            self.lbl_bin_status.setText("🔴 Belum Terpasang")
            self.lbl_bin_status.setStyleSheet("color: #dc2626; font-weight: 600; font-size: 11px;")
            self.lbl_bin_path.setText("Buka tab 'Manajemen Versi Scrcpy' untuk mengunduh versi yang diinginkan.")
            self.lbl_active_info.setText("")

    def browse_scrcpy(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih scrcpy.exe", "", "Executable Files (*.exe)")
        if path:
            settings.set("scrcpy_path", path)
            self.populate_versions_dropdown()
            self.update_status()

    def on_record_toggled(self, checked: bool):
        self.txt_rec_path.setEnabled(checked)
        self.btn_rec_browse.setEnabled(checked)
        if checked and not self.txt_rec_path.text():
            default_file = os.path.join(settings.get("default_download_dir") or os.getcwd(), "scrcpy_recording.mp4")
            self.txt_rec_path.setText(default_file)

    def browse_record_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Rekaman Layar", self.txt_rec_path.text(), "MP4 Video (*.mp4)")
        if file_path:
            self.txt_rec_path.setText(file_path)

    def start_mirror(self):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Pilih perangkat aktif terlebih dahulu.")
            return

        res_map = {"Native (Default)": 0, "720p (Cepat)": 720, "1080p (FHD)": 1080, "1440p (2K)": 1440}
        max_size = res_map.get(self.cb_res.currentText(), 0)

        bit_map = {"Default (8M)": "8M", "2 Mbps (Hemat Kuota)": "2M", "4 Mbps": "4M",
                   "8 Mbps (Rekomendasi)": "8M", "16 Mbps (High Quality)": "16M", "24 Mbps": "24M"}
        bitrate = bit_map.get(self.cb_bit.currentText(), "8M")

        fps_map = {"Default": 0, "30 FPS": 30, "60 FPS (Halus)": 60, "120 FPS": 120}
        max_fps = fps_map.get(self.cb_fps.currentText(), 0)

        options = {
            "max_size": max_size,
            "bitrate": bitrate,
            "max_fps": max_fps,
            "stay_awake": self.chk_stay_awake.isChecked(),
            "turn_screen_off": self.chk_screen_off.isChecked(),
            "no_audio": self.chk_no_audio.isChecked(),
            "fullscreen": self.chk_fullscreen.isChecked(),
            "always_on_top": self.chk_always_top.isChecked(),
            "show_touches": self.chk_touches.isChecked(),
            "otg": self.chk_otg.isChecked(),
            "record_file": self.txt_rec_path.text() if self.chk_record.isChecked() else None
        }

        ok, msg = scrcpy_manager.start_mirror(self.current_serial, options)
        if not ok:
            QMessageBox.critical(self, "Gagal Memulai Scrcpy", msg)

    def stop_mirror(self):
        scrcpy_manager.stop_mirror()

    def on_mirror_started(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def on_mirror_stopped(self, exit_code: int):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
