import os
import tempfile
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QGroupBox, QFrame, QLineEdit, QMessageBox,
    QFileDialog, QProgressBar, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from core.adb_manager import adb_manager
from ui.style import styled_btn

class InfoWorker(QThread):
    finished = Signal(dict)

    def __init__(self, serial: str):
        super().__init__()
        self.serial = serial

    def run(self):
        if not self.serial:
            self.finished.emit({})
            return

        props = adb_manager.get_device_props(self.serial)
        battery = adb_manager.get_battery_info(self.serial)
        res, dens = adb_manager.get_display_info(self.serial)
        storage = adb_manager.get_storage_info(self.serial)
        ram = adb_manager.get_ram_info(self.serial)
        ip = adb_manager.get_ip_address(self.serial)

        data = {
            "model": props.get("ro.product.model", "Unknown"),
            "brand": props.get("ro.product.brand", props.get("ro.product.manufacturer", "Unknown")).capitalize(),
            "android_ver": props.get("ro.build.version.release", "Unknown"),
            "sdk": props.get("ro.build.version.sdk", "Unknown"),
            "build": props.get("ro.build.display.id", props.get("ro.build.id", "Unknown")),
            "security_patch": props.get("ro.build.version.security_patch", "Unknown"),
            "abi": props.get("ro.product.cpu.abi", "Unknown"),
            "battery": battery,
            "res": res,
            "dens": dens,
            "storage": storage,
            "ram": ram,
            "ip": ip
        }
        self.finished.emit(data)

class DeviceInfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Tab Widget separating Specs vs Controls
        self.sub_tabs = QTabWidget()

        # Sub-Tab 1: Specs & Hardware
        tab_specs = QWidget()
        self.setup_specs_tab(tab_specs)
        self.sub_tabs.addTab(tab_specs, "📱  Spesifikasi && Status")

        # Sub-Tab 2: Remote Controls & Screenshot
        tab_ctrl = QWidget()
        self.setup_controls_tab(tab_ctrl)
        self.sub_tabs.addTab(tab_ctrl, "🎮  Remote Kontrol && Layar")

        main_layout.addWidget(self.sub_tabs)

    # -------------------------------------------------------------
    # 1. SUB-TAB: SPESIFIKASI & HARDWARE
    # -------------------------------------------------------------
    def setup_specs_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header Title with Refresh Button
        top_bar = QHBoxLayout()
        title = QLabel("Ringkasan Perangkat & Spesifikasi Hardware")
        title.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b;")
        self.btn_refresh = QPushButton("🔄 Refresh Info")
        self.btn_refresh.clicked.connect(self.refresh_info)
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_refresh)
        layout.addLayout(top_bar)

        # Loading Indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)

        # Row 1: Identity Card & Hardware Card in 2 equal columns
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        # Device Identity Card
        id_box = QGroupBox("📱 Identitas Perangkat")
        id_layout = QGridLayout(id_box)
        id_layout.setContentsMargins(8, 8, 8, 8)
        id_layout.setSpacing(6)

        self.lbl_brand = QLabel("-")
        self.lbl_model = QLabel("-")
        self.lbl_serial = QLabel("-")
        self.lbl_android = QLabel("-")
        self.lbl_sdk = QLabel("-")
        self.lbl_security = QLabel("-")
        self.lbl_abi = QLabel("-")
        self.lbl_ip = QLabel("-")

        labels = [
            ("Brand / Manufaktur:", self.lbl_brand),
            ("Nama Model:", self.lbl_model),
            ("Nomor Serial:", self.lbl_serial),
            ("Versi Android:", self.lbl_android),
            ("Level API SDK:", self.lbl_sdk),
            ("Security Patch:", self.lbl_security),
            ("Arsitektur CPU (ABI):", self.lbl_abi),
            ("Alamat IP Wi-Fi:", self.lbl_ip),
        ]

        for i, (txt, widget) in enumerate(labels):
            lbl_title = QLabel(txt)
            lbl_title.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
            widget.setStyleSheet("color: #0f172a; font-weight: 600; font-size: 11px;")
            id_layout.addWidget(lbl_title, i, 0)
            id_layout.addWidget(widget, i, 1)

        row1.addWidget(id_box)

        # Hardware & Battery Card
        hw_box = QGroupBox("⚡ Baterai, Layar && Memori")
        hw_layout = QGridLayout(hw_box)
        hw_layout.setContentsMargins(8, 8, 8, 8)
        hw_layout.setSpacing(6)

        self.lbl_battery_pct = QLabel("-")
        self.lbl_battery_status = QLabel("-")
        self.lbl_battery_temp = QLabel("-")
        self.lbl_resolution = QLabel("-")
        self.lbl_density = QLabel("-")
        self.lbl_storage = QLabel("-")
        self.lbl_ram = QLabel("-")

        hw_labels = [
            ("Persentase Baterai:", self.lbl_battery_pct),
            ("Status Pengisian:", self.lbl_battery_status),
            ("Suhu / Kondisi Baterai:", self.lbl_battery_temp),
            ("Resolusi Layar:", self.lbl_resolution),
            ("Kerapatan Layar (DPI):", self.lbl_density),
            ("Penyimpanan Internal:", self.lbl_storage),
            ("Sisa RAM Tersedia:", self.lbl_ram),
        ]

        for i, (txt, widget) in enumerate(hw_labels):
            lbl_title = QLabel(txt)
            lbl_title.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
            widget.setStyleSheet("color: #0f172a; font-weight: 600; font-size: 11px;")
            hw_layout.addWidget(lbl_title, i, 0)
            hw_layout.addWidget(widget, i, 1)

        row1.addWidget(hw_box)
        layout.addLayout(row1)
        layout.addStretch()

    # -------------------------------------------------------------
    # 2. SUB-TAB: REMOTE CONTROLS & SCREENSHOT
    # -------------------------------------------------------------
    def setup_controls_tab(self, parent: QWidget):
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Left Column: Remote Keys, Text Input, Clipboard
        col_left = QVBoxLayout()
        col_left.setSpacing(6)

        # Quick Key Controls Card
        control_box = QGroupBox("🎮 Kontrol Tombol Fisik & Input")
        ctrl_layout = QVBoxLayout(control_box)
        ctrl_layout.setContentsMargins(8, 8, 8, 8)
        ctrl_layout.setSpacing(6)

        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(5)
        btn_back = QPushButton("◀ Back")
        btn_home = QPushButton("⚪ Home")
        btn_recent = QPushButton("▢ Recent Apps")
        btn_power = QPushButton("⚡ Power / Wake")
        btn_voldown = QPushButton("🔉 Vol -")
        btn_volup = QPushButton("🔊 Vol +")

        btn_back.clicked.connect(lambda: self.send_key(4))
        btn_home.clicked.connect(lambda: self.send_key(3))
        btn_recent.clicked.connect(lambda: self.send_key(187))
        btn_power.clicked.connect(lambda: self.send_key(26))
        btn_voldown.clicked.connect(lambda: self.send_key(25))
        btn_volup.clicked.connect(lambda: self.send_key(24))

        for b in [btn_back, btn_home, btn_recent, btn_power, btn_voldown, btn_volup]:
            btn_row1.addWidget(b)
        ctrl_layout.addLayout(btn_row1)

        # Quick Text Input to Device
        text_row = QHBoxLayout()
        text_row.setSpacing(6)
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Ketik teks di sini untuk dikirim langsung ke HP...")
        btn_send_txt = styled_btn("⌨ Kirim Teks", "primary")
        btn_send_txt.clicked.connect(self.send_text)
        self.txt_input.returnPressed.connect(self.send_text)
        text_row.addWidget(self.txt_input)
        text_row.addWidget(btn_send_txt)
        ctrl_layout.addLayout(text_row)

        col_left.addWidget(control_box)

        # Clipboard Card
        clip_box = QGroupBox("📋 Sinkronisasi Papan Klip (Clipboard)")
        clip_layout = QVBoxLayout(clip_box)
        clip_layout.setContentsMargins(8, 8, 8, 8)
        clip_layout.setSpacing(6)

        c_row1 = QHBoxLayout()
        c_row1.setSpacing(6)
        btn_copy_clip = QPushButton("📋 Ambil Clipboard dari HP")
        btn_copy_clip.clicked.connect(self.get_clipboard)
        btn_set_clip = styled_btn("📤 Kirim Clipboard ke HP", "primary")
        btn_set_clip.clicked.connect(self.set_clipboard)
        c_row1.addWidget(btn_copy_clip)
        c_row1.addWidget(btn_set_clip)
        clip_layout.addLayout(c_row1)

        self.txt_clip = QLineEdit()
        self.txt_clip.setPlaceholderText("Teks clipboard HP akan muncul di sini atau ketik untuk dikirim...")
        clip_layout.addWidget(self.txt_clip)

        col_left.addWidget(clip_box)
        col_left.addStretch()
        layout.addLayout(col_left, 1)

        # Right Column: Screenshot Card
        screen_box = QGroupBox("📸 Tangkapan Layar (Screenshot)")
        screen_layout = QVBoxLayout(screen_box)
        screen_layout.setContentsMargins(8, 8, 8, 8)
        screen_layout.setSpacing(6)

        btn_capture = styled_btn("📸 Ambil Tangkapan Layar", "primary")
        btn_capture.clicked.connect(self.take_screenshot)
        screen_layout.addWidget(btn_capture)

        self.lbl_preview = QLabel("Belum ada screenshot")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("border: 1px dashed #cbd5e1; border-radius: 6px; color: #64748b; background-color: #f8fafc; font-size: 11px;")
        self.lbl_preview.setFixedSize(180, 240)
        screen_layout.addWidget(self.lbl_preview, 0, Qt.AlignCenter)
        screen_layout.addStretch()

        layout.addWidget(screen_box)

    # -------------------------------------------------------------
    # DEVICE DATA & ACTIONS
    # -------------------------------------------------------------
    def set_device(self, serial: str):
        self.current_serial = serial
        self.lbl_serial.setText(serial if serial else "Tidak ada perangkat")
        if serial:
            self.refresh_info()
        else:
            self.clear_fields()

    def clear_fields(self):
        for lbl in [
            self.lbl_brand, self.lbl_model, self.lbl_android, self.lbl_sdk,
            self.lbl_security, self.lbl_abi, self.lbl_ip, self.lbl_battery_pct,
            self.lbl_battery_status, self.lbl_battery_temp, self.lbl_resolution,
            self.lbl_density, self.lbl_storage, self.lbl_ram
        ]:
            lbl.setText("-")
        self.lbl_preview.setText("Belum ada screenshot")
        self.lbl_preview.setPixmap(QPixmap())

    def refresh_info(self):
        if not self.current_serial:
            return
        self.loading_bar.setVisible(True)
        self.btn_refresh.setEnabled(False)

        self.worker = InfoWorker(self.current_serial)
        self.worker.finished.connect(self.on_info_loaded)
        self.worker.start()

    def on_info_loaded(self, data: dict):
        self.loading_bar.setVisible(False)
        self.btn_refresh.setEnabled(True)
        if not data:
            return

        self.lbl_brand.setText(data.get("brand", "-"))
        self.lbl_model.setText(data.get("model", "-"))
        self.lbl_android.setText(f"Android {data.get('android_ver', '-')}")
        self.lbl_sdk.setText(f"API {data.get('sdk', '-')}")
        self.lbl_security.setText(data.get("security_patch", "-"))
        self.lbl_abi.setText(data.get("abi", "-"))
        self.lbl_ip.setText(data.get("ip", "Terputus"))

        # Battery
        bat = data.get("battery", {})
        pct = bat.get("level", "0")
        scale = bat.get("scale", "100")
        try:
            percent_val = int((int(pct) / int(scale)) * 100)
            self.lbl_battery_pct.setText(f"{percent_val}%")
        except Exception:
            self.lbl_battery_pct.setText(f"{pct}%")

        self.lbl_battery_status.setText(bat.get("status", "Unknown"))
        temp_val = bat.get("temperature", "")
        if temp_val and temp_val.isdigit():
            celsius = int(temp_val) / 10.0
            self.lbl_battery_temp.setText(f"{celsius:.1f} °C (Kondisi: {bat.get('health', 'Baik')})")
        else:
            self.lbl_battery_temp.setText(bat.get("health", "Unknown"))

        # Display
        self.lbl_resolution.setText(data.get("res", "-"))
        self.lbl_density.setText(data.get("dens", "-"))

        # Storage
        st = data.get("storage", {})
        if st:
            self.lbl_storage.setText(f"{st.get('used', '-')} terpakai / {st.get('total', '-')} ({st.get('percent', '-')})")
        else:
            self.lbl_storage.setText("Unknown")

        # RAM
        ram = data.get("ram", {})
        if "MemTotal" in ram:
            total_kb = int(ram["MemTotal"].split()[0])
            avail_kb = int(ram.get("MemAvailable", "0 kB").split()[0]) if "MemAvailable" in ram else 0
            self.lbl_ram.setText(f"{avail_kb // 1024} MB bebas dari {total_kb // 1024} MB")
        else:
            self.lbl_ram.setText("Unknown")

    def send_key(self, code: int):
        if not self.current_serial:
            return
        adb_manager.send_key(self.current_serial, code)

    def send_text(self):
        text = self.txt_input.text().strip()
        if not text or not self.current_serial:
            return
        adb_manager.send_text(self.current_serial, text)
        self.txt_input.clear()

    def take_screenshot(self):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Silakan hubungkan perangkat terlebih dahulu.")
            return

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        success = adb_manager.take_screenshot(self.current_serial, tmp_path)
        if success and os.path.exists(tmp_path):
            pixmap = QPixmap(tmp_path)
            self.lbl_preview.setPixmap(pixmap.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            save_path, _ = QFileDialog.getSaveFileName(self, "Simpan Screenshot", f"screenshot_{self.current_serial}.png", "PNG Images (*.png)")
            if save_path:
                try:
                    pixmap.save(save_path)
                    QMessageBox.information(self, "Tersimpan", f"Screenshot berhasil disimpan ke:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Gagal menyimpan screenshot: {e}")
        else:
            QMessageBox.critical(self, "Gagal", "Tidak dapat mengambil tangkapan layar dari HP.")

    def get_clipboard(self):
        if not self.current_serial:
            return
        clip = adb_manager.get_clipboard(self.current_serial)
        if clip:
            self.txt_clip.setText(clip.strip())
            QMessageBox.information(self, "Clipboard HP", f"Isi clipboard berhasil disalin:\n{clip.strip()}")
        else:
            QMessageBox.information(self, "Clipboard HP", "Clipboard kosong atau tidak didukung pada versi Android ini.")

    def set_clipboard(self):
        text = self.txt_clip.text().strip()
        if not self.current_serial or not text:
            return
        adb_manager.set_clipboard(self.current_serial, text)
        QMessageBox.information(self, "Sukses", "Teks berhasil dikirim ke clipboard HP!")
