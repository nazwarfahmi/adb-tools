from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QWidget, QMessageBox, QGroupBox
)
from core.adb_manager import adb_manager
from ui.style import styled_btn

class WirelessDialog(QDialog):
    def __init__(self, current_serial: str = "", parent=None):
        super().__init__(parent)
        self.current_serial = current_serial
        self.setWindowTitle("Sambungkan via Wi-Fi (Wireless ADB)")
        self.resize(480, 340)
        self.setMinimumSize(440, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        tabs = QTabWidget()

        # Tab 1: Direct Connect
        tab_connect = QWidget()
        l_conn = QVBoxLayout(tab_connect)
        l_conn.setContentsMargins(8, 8, 8, 8)
        l_conn.setSpacing(6)

        lbl_desc = QLabel("Hubungkan ke HP menggunakan IP dan port jaringan Wi-Fi:")
        lbl_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        l_conn.addWidget(lbl_desc)

        box_ip = QGroupBox("Alamat IP & Port Perangkat")
        l_box = QHBoxLayout(box_ip)
        l_box.setContentsMargins(8, 8, 8, 8)
        l_box.setSpacing(6)
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("192.168.1.100")
        self.txt_port = QLineEdit("5555")
        self.txt_port.setFixedWidth(70)

        l_box.addWidget(QLabel("IP:"))
        l_box.addWidget(self.txt_ip)
        l_box.addWidget(QLabel("Port:"))
        l_box.addWidget(self.txt_port)
        l_conn.addWidget(box_ip)

        # Switch plugged-in USB device to Wi-Fi mode
        box_switch = QGroupBox("Ubah Mode USB ke Mode Wi-Fi")
        l_sw = QVBoxLayout(box_switch)
        l_sw.setContentsMargins(8, 8, 8, 8)
        l_sw.setSpacing(5)
        lbl_sw_info = QLabel("Jika HP saat ini dicolok via kabel USB, klik tombol di bawah untuk membuka port 5555:")
        lbl_sw_info.setStyleSheet("color: #64748b; font-size: 10px;")
        btn_tcpip = QPushButton("🔌 Buka Mode TCP/IP pada HP USB (adb tcpip 5555)")
        btn_tcpip.setFixedHeight(26)
        btn_tcpip.clicked.connect(self.enable_tcpip_mode)
        l_sw.addWidget(lbl_sw_info)
        l_sw.addWidget(btn_tcpip)
        l_conn.addWidget(box_switch)

        btn_connect = styled_btn("🌐 Sambungkan (Connect)", "primary")
        btn_connect.setFixedHeight(26)
        btn_connect.clicked.connect(self.connect_wireless)
        l_conn.addWidget(btn_connect)
        l_conn.addStretch()

        tabs.addTab(tab_connect, "Koneksi Langsung (IP:Port)")

        # Tab 2: Android 11+ Pairing
        tab_pair = QWidget()
        l_pair = QVBoxLayout(tab_pair)
        l_pair.setContentsMargins(8, 8, 8, 8)
        l_pair.setSpacing(6)

        lbl_pair_desc = QLabel("Pada Android 11+, buka Opsi Pengembang > Debugging Nirkabel > 'Pasangkan perangkat dengan kode penyandingan'.")
        lbl_pair_desc.setWordWrap(True)
        lbl_pair_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        l_pair.addWidget(lbl_pair_desc)

        box_pair_input = QGroupBox("Detail Pairing Android 11+")
        l_pi = QVBoxLayout(box_pair_input)
        l_pi.setContentsMargins(8, 8, 8, 8)
        l_pi.setSpacing(6)

        row_pi1 = QHBoxLayout()
        row_pi1.setSpacing(6)
        self.txt_pair_ip = QLineEdit()
        self.txt_pair_ip.setPlaceholderText("192.168.1.100")
        self.txt_pair_port = QLineEdit()
        self.txt_pair_port.setPlaceholderText("Contoh: 37123")
        self.txt_pair_port.setFixedWidth(80)
        row_pi1.addWidget(QLabel("IP:"))
        row_pi1.addWidget(self.txt_pair_ip)
        row_pi1.addWidget(QLabel("Port:"))
        row_pi1.addWidget(self.txt_pair_port)
        l_pi.addLayout(row_pi1)

        row_pi2 = QHBoxLayout()
        row_pi2.setSpacing(6)
        self.txt_pair_code = QLineEdit()
        self.txt_pair_code.setPlaceholderText("6 digit kode pairing (contoh: 123456)")
        row_pi2.addWidget(QLabel("Kode:"))
        row_pi2.addWidget(self.txt_pair_code)
        l_pi.addLayout(row_pi2)
        l_pair.addWidget(box_pair_input)

        btn_pair = styled_btn("🔗 Pasangkan & Sambungkan", "primary")
        btn_pair.setFixedHeight(26)
        btn_pair.clicked.connect(self.pair_wireless)
        l_pair.addWidget(btn_pair)
        l_pair.addStretch()

        tabs.addTab(tab_pair, "Pairing Android 11+")

        layout.addWidget(tabs)

    def enable_tcpip_mode(self):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Silakan colokkan HP via USB dan pilih perangkat terlebih dahulu.")
            return

        ok, out = adb_manager.enable_tcpip(self.current_serial, 5555)
        if ok:
            ip = adb_manager.get_ip_address(self.current_serial)
            if ip and ip != "Not Connected":
                self.txt_ip.setText(ip)
            QMessageBox.information(self, "Berhasil", f"Mode TCP/IP port 5555 aktif!\nIP HP terdeteksi: {ip}\nAnda sekarang bisa mencabut kabel USB lalu klik tombol Sambungkan.")
        else:
            QMessageBox.critical(self, "Gagal", f"Tidak dapat mengaktifkan mode TCP/IP:\n{out}")

    def connect_wireless(self):
        ip = self.txt_ip.text().strip()
        port = self.txt_port.text().strip() or "5555"
        if not ip:
            QMessageBox.warning(self, "IP Kosong", "Masukkan alamat IP perangkat terlebih dahulu.")
            return

        target = f"{ip}:{port}"
        ok, out = adb_manager.wireless_connect(target)
        if ok and ("connected to" in out.lower() or "already connected" in out.lower()):
            QMessageBox.information(self, "Terhubung", f"Berhasil tersambung ke {target} secara nirkabel!")
            self.accept()
        else:
            QMessageBox.critical(self, "Koneksi Gagal", f"Gagal menyambung ke {target}:\n{out}")

    def pair_wireless(self):
        ip = self.txt_pair_ip.text().strip()
        port = self.txt_pair_port.text().strip()
        code = self.txt_pair_code.text().strip()

        if not ip or not port or not code:
            QMessageBox.warning(self, "Data Kurang", "Harap isi alamat IP, Port pairing, dan 6-digit Kode.")
            return

        target = f"{ip}:{port}"
        ok, out = adb_manager.wireless_pair(target, code)
        if ok and "successfully paired" in out.lower():
            QMessageBox.information(self, "Pairing Sukses", "HP berhasil dipasangkan! Silakan sambungkan melalui port debugging nirkabel.")
            self.txt_ip.setText(ip)
        else:
            QMessageBox.critical(self, "Pairing Gagal", f"Gagal pairing:\n{out}")
