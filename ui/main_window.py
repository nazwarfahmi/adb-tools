from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QStackedWidget, QStatusBar,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from core.adb_manager import adb_manager
from core.settings import settings

from ui.tabs.device_info_tab import DeviceInfoTab
from ui.tabs.app_manager_tab import AppManagerTab
from ui.tabs.file_explorer_tab import FileExplorerTab
from ui.tabs.scrcpy_tab import ScrcpyTab
from ui.tabs.fastboot_tab import FastbootTab
from ui.tabs.terminal_tab import TerminalTab
from ui.dialogs.wireless_dialog import WirelessDialog
from ui.dialogs.settings_dialog import SettingsDialog

class DeviceScanWorker(QThread):
    devices_found = Signal(list)

    def run(self):
        devices = adb_manager.get_devices()
        self.devices_found.emit(devices)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADB Studio - Device Manager & Tools")
        self.resize(1020, 640)
        self.setMinimumSize(880, 540)

        self.current_serial = ""
        self.current_state = ""
        self.known_devices = []
        self.scan_worker = None

        self.init_ui()
        self.setup_device_scanner()
        self.refresh_devices()

    def init_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Header Bar (Compact)
        top_header = QWidget()
        top_header.setObjectName("topHeader")
        th_layout = QHBoxLayout(top_header)
        th_layout.setContentsMargins(10, 5, 10, 5)
        th_layout.setSpacing(8)

        # App Logo & Name
        lbl_app = QLabel("⚡ ADB Studio")
        lbl_app.setStyleSheet("font-size: 13px; font-weight: bold; color: #0284c7;")
        th_layout.addWidget(lbl_app)

        th_layout.addSpacing(12)

        # Device Selector
        lbl_dev = QLabel("Active Device:")
        lbl_dev.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        th_layout.addWidget(lbl_dev)

        self.cb_devices = QComboBox()
        self.cb_devices.setMinimumWidth(220)
        self.cb_devices.currentIndexChanged.connect(self.on_device_selected)
        th_layout.addWidget(self.cb_devices)

        # Status Badge
        self.lbl_status_badge = QLabel("Offline")
        self.lbl_status_badge.setAlignment(Qt.AlignCenter)
        self.lbl_status_badge.setProperty("badge", "offline")
        th_layout.addWidget(self.lbl_status_badge)

        # Device Action Buttons
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh_devices)
        th_layout.addWidget(self.btn_refresh)

        btn_wifi = QPushButton("🌐 Wi-Fi Connect")
        btn_wifi.clicked.connect(self.open_wireless_dialog)
        th_layout.addWidget(btn_wifi)

        btn_restart_adb = QPushButton("💀 Restart Server")
        btn_restart_adb.clicked.connect(self.restart_adb_server)
        th_layout.addWidget(btn_restart_adb)

        th_layout.addStretch()

        btn_settings = QPushButton("⚙ Settings")
        btn_settings.clicked.connect(self.open_settings_dialog)
        th_layout.addWidget(btn_settings)

        main_layout.addWidget(top_header)

        # 2. Body: Sidebar + Tab Stack
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar (Compact)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(6, 8, 6, 8)
        sb_layout.setSpacing(3)

        self.nav_buttons = []
        nav_items = [
            ("📱  Device Overview", 0),
            ("📦  App Manager", 1),
            ("📁  File Explorer", 2),
            ("🖥  Screen Mirror (Scrcpy)", 3),
            ("🔄  Reboot Options", 4),
            ("💻  Terminal && Logs", 5),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, idx=index: self.switch_tab(idx))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # Version & helper in sidebar bottom
        lbl_v = QLabel("ADB Tools v1.0.0")
        lbl_v.setStyleSheet("color: #94a3b8; font-size: 10px; padding: 4px 6px;")
        sb_layout.addWidget(lbl_v)

        body_layout.addWidget(self.sidebar)

        # Content Stack
        self.stack = QStackedWidget()

        self.tab_info = DeviceInfoTab()
        self.tab_apps = AppManagerTab()
        self.tab_files = FileExplorerTab()
        self.tab_scrcpy = ScrcpyTab()
        self.tab_fastboot = FastbootTab()
        self.tab_terminal = TerminalTab()

        self.stack.addWidget(self.tab_info)
        self.stack.addWidget(self.tab_apps)
        self.stack.addWidget(self.tab_files)
        self.stack.addWidget(self.tab_scrcpy)
        self.stack.addWidget(self.tab_fastboot)
        self.stack.addWidget(self.tab_terminal)

        body_layout.addWidget(self.stack, 1)
        main_layout.addWidget(body, 1)

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready | ADB: {adb_manager.adb_bin}")

        # Default select first tab
        self.switch_tab(0)

    def switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def setup_device_scanner(self):
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(4000)  # Check devices every 4 seconds
        self.poll_timer.timeout.connect(self.background_device_scan)
        self.poll_timer.start()

    def background_device_scan(self):
        if self.scan_worker and self.scan_worker.isRunning():
            return
        self.scan_worker = DeviceScanWorker()
        self.scan_worker.devices_found.connect(self.on_devices_scanned)
        self.scan_worker.start()

    def refresh_devices(self):
        self.background_device_scan()

    def on_devices_scanned(self, devices: list):
        current_selection = self.current_serial

        # Compare devices list with known devices
        devices_changed = (len(devices) != len(self.known_devices) or
                           any(d["serial"] != kd["serial"] or d["state"] != kd["state"]
                               for d, kd in zip(devices, self.known_devices)))

        if not devices_changed and self.cb_devices.count() > 0:
            return

        self.known_devices = devices
        self.cb_devices.blockSignals(True)
        self.cb_devices.clear()

        if not devices:
            self.cb_devices.addItem("⚠️ No device connected", "")
            self.set_active_serial("", force=True)
        else:
            selected_idx = 0
            for i, dev in enumerate(devices):
                serial = dev["serial"]
                state = dev["state"]
                model = dev.get("model", "")
                text = f"{serial} ({model})" if model else serial
                self.cb_devices.addItem(f"{text} [{state}]", serial)
                if serial == current_selection:
                    selected_idx = i

            self.cb_devices.setCurrentIndex(selected_idx)
            chosen_serial = self.cb_devices.currentData()
            self.set_active_serial(chosen_serial, force=devices_changed)

        self.cb_devices.blockSignals(False)

    def on_device_selected(self, index: int):
        serial = self.cb_devices.itemData(index)
        self.set_active_serial(serial or "")

    def set_active_serial(self, serial: str, force: bool = False):
        # Find status of this serial
        state = "offline"
        for d in self.known_devices:
            if d["serial"] == serial:
                state = d.get("state", "offline")
                break

        if not force and self.current_serial == serial and self.current_state == state and serial:
            return

        state_changed = (self.current_state != state)
        serial_changed = (self.current_serial != serial)

        self.current_serial = serial
        self.current_state = state

        if serial:
            if state == "device":
                self.lbl_status_badge.setText("Online")
                self.lbl_status_badge.setProperty("badge", "online")
                self.lbl_status_badge.setToolTip("Perangkat terhubung dan siap digunakan.")
            elif state == "unauthorized":
                self.lbl_status_badge.setText("Unauthorized")
                self.lbl_status_badge.setProperty("badge", "unauthorized")
                self.lbl_status_badge.setToolTip("Perangkat belum diizinkan. Harap periksa layar HP Anda dan pilih 'Izinkan USB Debugging'.")
            elif state in ["recovery", "sideload"]:
                self.lbl_status_badge.setText(state.capitalize())
                self.lbl_status_badge.setProperty("badge", "fastboot")
                self.lbl_status_badge.setToolTip(f"Perangkat berada dalam mode {state}.")
            else:
                self.lbl_status_badge.setText(state.capitalize())
                self.lbl_status_badge.setProperty("badge", state)
                self.lbl_status_badge.setToolTip(f"Status perangkat: {state}")

            self.status_bar.showMessage(f"Connected: {serial} | State: {state}")
        else:
            self.lbl_status_badge.setText("Disconnected")
            self.lbl_status_badge.setProperty("badge", "offline")
            self.lbl_status_badge.setToolTip("Tidak ada perangkat yang terhubung.")
            self.status_bar.showMessage("No device connected. Connect via USB or Wi-Fi.")

        self.lbl_status_badge.style().unpolish(self.lbl_status_badge)
        self.lbl_status_badge.style().polish(self.lbl_status_badge)

        # Notify all tabs: only send serial if state is authorized ("device")
        target_serial = serial if state == "device" else ""
        if serial_changed or state_changed or force:
            self.tab_info.set_device(target_serial)
            self.tab_apps.set_device(target_serial)
            self.tab_files.set_device(target_serial)
            self.tab_scrcpy.set_device(target_serial)
            self.tab_fastboot.set_device(target_serial)
            self.tab_terminal.set_device(target_serial)

    def open_wireless_dialog(self):
        dlg = WirelessDialog(current_serial=self.current_serial, parent=self)
        if dlg.exec():
            self.refresh_devices()

    def open_settings_dialog(self):
        dlg = SettingsDialog(parent=self)
        if dlg.exec():
            self.status_bar.showMessage(f"Settings updated | ADB: {adb_manager.adb_bin}")
            self.tab_scrcpy.update_status()
            self.refresh_devices()

    def restart_adb_server(self):
        self.status_bar.showMessage("Restarting ADB server...")
        ok, out = adb_manager.restart_server()
        if ok:
            QMessageBox.information(self, "ADB Server", "ADB Server restarted successfully!")
            self.refresh_devices()
        else:
            QMessageBox.critical(self, "ADB Server Error", f"Failed to restart ADB server:\n{out}")

    def closeEvent(self, event):
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
        if hasattr(self, 'scan_worker') and self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.wait(500)
        event.accept()

