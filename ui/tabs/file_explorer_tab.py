import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QProgressBar, QMenu, QInputDialog,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal
from core.adb_manager import adb_manager
from core.settings import settings
from ui.dialogs.confirm_dialog import confirm_two_step
from ui.style import styled_btn

class FileListWorker(QThread):
    finished = Signal(list)

    def __init__(self, serial: str, remote_path: str):
        super().__init__()
        self.serial = serial
        self.remote_path = remote_path

    def run(self):
        if not self.serial:
            self.finished.emit([])
            return
        files = adb_manager.list_files(self.serial, self.remote_path)
        self.finished.emit(files)

class TransferWorker(QThread):
    status = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, mode: str, serial: str, source: str, destination: str):
        super().__init__()
        self.mode = mode  # "push" or "pull"
        self.serial = serial
        self.source = source
        self.destination = destination

    def run(self):
        if self.mode == "push":
            self.status.emit(f"Mengirim {os.path.basename(self.source)} ke perangkat...")
            ok, out = adb_manager.push_file(self.serial, self.source, self.destination)
            self.finished.emit(ok, out)
        else:
            self.status.emit(f"Mengunduh {os.path.basename(self.source)} ke PC...")
            ok, out = adb_manager.pull_file(self.serial, self.source, self.destination)
            self.finished.emit(ok, out)

def format_size(bytes_str: str) -> str:
    try:
        val = int(bytes_str)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if val < 1024.0:
                return f"{val:.1f} {unit}"
            val /= 1024.0
        return f"{val:.1f} TB"
    except Exception:
        return bytes_str

class FileExplorerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.current_path = "/sdcard"
        self.files_cache = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # 1. Quick Bookmarks Bar
        bookmark_bar = QHBoxLayout()
        bookmark_bar.setSpacing(6)
        lbl_bm = QLabel("📍 Pintasan Cepat:")
        lbl_bm.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        bookmark_bar.addWidget(lbl_bm)

        bm_sdcard = QPushButton("📂 /sdcard")
        bm_dcim = QPushButton("📷 DCIM (Foto)")
        bm_down = QPushButton("⬇ Download")
        bm_root = QPushButton("⚙ Root (/)")

        bm_sdcard.clicked.connect(lambda: self.navigate_to("/sdcard"))
        bm_dcim.clicked.connect(lambda: self.navigate_to("/sdcard/DCIM"))
        bm_down.clicked.connect(lambda: self.navigate_to("/sdcard/Download"))
        bm_root.clicked.connect(lambda: self.navigate_to("/"))

        for b in [bm_sdcard, bm_dcim, bm_down, bm_root]:
            bookmark_bar.addWidget(b)
        bookmark_bar.addStretch()
        layout.addLayout(bookmark_bar)

        # 2. Path Navigation & Filter Bar
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(6)

        btn_up = QPushButton("⬆ Naik")
        btn_up.clicked.connect(self.go_up)
        nav_bar.addWidget(btn_up)

        self.txt_path = QLineEdit(self.current_path)
        self.txt_path.setPlaceholderText("Ketik path folder...")
        self.txt_path.returnPressed.connect(lambda: self.navigate_to(self.txt_path.text()))
        nav_bar.addWidget(self.txt_path, 1)

        btn_go = styled_btn("Buka", "primary")
        btn_go.clicked.connect(lambda: self.navigate_to(self.txt_path.text()))
        nav_bar.addWidget(btn_go)

        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("🔍 Filter file...")
        self.txt_filter.setFixedWidth(160)
        self.txt_filter.textChanged.connect(self.apply_filter)
        nav_bar.addWidget(self.txt_filter)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.refresh_files)
        nav_bar.addWidget(btn_refresh)

        layout.addLayout(nav_bar)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 3. File List Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nama File / Folder", "Ukuran", "Izin Akses", "Terakhir Diubah"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        # 4. Bottom Bar: Actions & Transfer
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(5)

        self.lbl_status = QLabel("Siap")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")
        bottom_bar.addWidget(self.lbl_status)
        bottom_bar.addStretch()

        btn_pull = styled_btn("📥 Unduh ke PC", "primary")
        btn_pull.clicked.connect(self.pull_selected)

        btn_push_file = QPushButton("📤 Kirim File")
        btn_push_file.clicked.connect(self.push_file)

        btn_push_folder = QPushButton("📁 Kirim Folder")
        btn_push_folder.clicked.connect(self.push_folder)

        btn_mkdir = QPushButton("➕ Folder Baru")
        btn_mkdir.clicked.connect(self.create_folder)

        btn_rename = QPushButton("✏ Ubah Nama")
        btn_rename.clicked.connect(self.rename_selected)

        btn_delete = styled_btn("🗑 Hapus", "danger")
        btn_delete.clicked.connect(self.delete_selected)

        for b in [btn_pull, btn_push_file, btn_push_folder, btn_mkdir, btn_rename, btn_delete]:
            bottom_bar.addWidget(b)

        layout.addLayout(bottom_bar)

    def set_device(self, serial: str):
        self.current_serial = serial
        if serial:
            self.refresh_files()
        else:
            self.files_cache = []
            self.table.setRowCount(0)
            self.lbl_status.setText("Tidak ada perangkat yang terhubung")

    def navigate_to(self, path: str):
        if not path.startswith("/"):
            path = "/" + path
        self.current_path = path.rstrip("/") if path != "/" else "/"
        self.txt_path.setText(self.current_path)
        self.refresh_files()

    def go_up(self):
        if self.current_path == "/":
            return
        parent = str(Path(self.current_path).parent).replace("\\", "/")
        self.navigate_to(parent)

    def refresh_files(self):
        if not self.current_serial:
            return

        self.progress_bar.setVisible(True)
        self.lbl_status.setText(f"Memuat {self.current_path}...")
        self.worker = FileListWorker(self.current_serial, self.current_path)
        self.worker.finished.connect(self.on_files_loaded)
        self.worker.start()

    def on_files_loaded(self, files: list):
        self.progress_bar.setVisible(False)
        self.files_cache = files
        self.apply_filter()

    def apply_filter(self):
        query = self.txt_filter.text().strip().lower()
        filtered = [f for f in self.files_cache if not query or query in f["name"].lower()]

        self.table.setRowCount(len(filtered))
        for row, f in enumerate(filtered):
            icon = "📁 " if f["is_dir"] else ("🔗 " if f["is_link"] else "📄 ")
            name_item = QTableWidgetItem(f"{icon}{f['name']}")
            size_item = QTableWidgetItem(format_size(f["size"]) if not f["is_dir"] else "<DIR>")
            perms_item = QTableWidgetItem(f["perms"])
            date_item = QTableWidgetItem(f["date"])

            name_item.setData(Qt.UserRole, f)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, size_item)
            self.table.setItem(row, 2, perms_item)
            self.table.setItem(row, 3, date_item)

        self.lbl_status.setText(f"{len(filtered)} item di {self.current_path}")

    def on_item_double_clicked(self, item):
        row = item.row()
        f_info = self.table.item(row, 0).data(Qt.UserRole)
        if f_info and f_info.get("is_dir"):
            target = f"{self.current_path.rstrip('/')}/{f_info['name']}"
            self.navigate_to(target)

    def get_selected_file_info(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.UserRole)
        return None

    def pull_selected(self):
        f = self.get_selected_file_info()
        if not f or not self.current_serial:
            QMessageBox.warning(self, "Pilih File", "Pilih file atau folder yang ingin diunduh terlebih dahulu.")
            return

        remote = f"{self.current_path.rstrip('/')}/{f['name']}"
        default_dir = settings.get("default_download_dir") or os.getcwd()

        if f["is_dir"]:
            dest = QFileDialog.getExistingDirectory(self, "Pilih Folder Tujuan Penyimpanan", default_dir)
            if dest:
                dest = os.path.join(dest, f["name"])
        else:
            dest, _ = QFileDialog.getSaveFileName(self, "Simpan File Sebagai", os.path.join(default_dir, f["name"]))

        if dest:
            self.start_transfer("pull", remote, dest)

    def push_file(self):
        if not self.current_serial:
            return
        local_path, _ = QFileDialog.getOpenFileName(self, "Pilih File untuk Dikirim ke HP")
        if local_path:
            self.start_transfer("push", local_path, self.current_path)

    def push_folder(self):
        if not self.current_serial:
            return
        local_path = QFileDialog.getExistingDirectory(self, "Pilih Folder untuk Dikirim ke HP")
        if local_path:
            self.start_transfer("push", local_path, self.current_path)

    def start_transfer(self, mode: str, source: str, destination: str):
        self.progress_bar.setVisible(True)
        self.transfer_worker = TransferWorker(mode, self.current_serial, source, destination)
        self.transfer_worker.status.connect(lambda s: self.lbl_status.setText(s))
        self.transfer_worker.finished.connect(self.on_transfer_finished)
        self.transfer_worker.start()

    def on_transfer_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Transfer Selesai", "Proses transfer file berhasil!")
            self.refresh_files()
        else:
            QMessageBox.critical(self, "Transfer Gagal", f"Gagal mentransfer file:\n{message}")

    def create_folder(self):
        if not self.current_serial:
            return
        name, ok = QInputDialog.getText(self, "Folder Baru", "Masukkan nama folder baru:")
        if ok and name.strip():
            target = f"{self.current_path.rstrip('/')}/{name.strip()}"
            success, out = adb_manager.create_dir(self.current_serial, target)
            if success:
                self.refresh_files()
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal membuat folder:\n{out}")

    def rename_selected(self):
        f = self.get_selected_file_info()
        if not f or not self.current_serial:
            return
        old_path = f"{self.current_path.rstrip('/')}/{f['name']}"
        new_name, ok = QInputDialog.getText(self, "Ubah Nama", "Nama baru:", text=f['name'])
        if ok and new_name.strip() and new_name.strip() != f['name']:
            new_path = f"{self.current_path.rstrip('/')}/{new_name.strip()}"
            success, out = adb_manager.rename_file(self.current_serial, old_path, new_path)
            if success:
                self.refresh_files()
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal mengubah nama:\n{out}")

    def delete_selected(self):
        f = self.get_selected_file_info()
        if not f or not self.current_serial:
            return
        target = f"{self.current_path.rstrip('/')}/{f['name']}"
        if not confirm_two_step(self, "delete_file", f['name'], target):
            return
        success, out = adb_manager.delete_file(self.current_serial, target)
        if success:
            self.refresh_files()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal menghapus file:\n{out}")

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.addAction("📥 Unduh (Pull ke PC)", self.pull_selected)
        menu.addAction("✏ Ubah Nama", self.rename_selected)
        menu.addSeparator()
        menu.addAction("🗑 Hapus", self.delete_selected)
        menu.exec(self.table.viewport().mapToGlobal(pos))
