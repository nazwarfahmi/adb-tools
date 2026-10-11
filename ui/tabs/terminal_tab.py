import subprocess
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QFileDialog, QTabWidget,
    QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from core.adb_manager import adb_manager, CREATE_NO_WINDOW
from ui.style import styled_btn

class LogcatWorker(QThread):
    new_line = Signal(str)

    def __init__(self, serial: str, log_level: str = "V", filter_str: str = ""):
        super().__init__()
        self.serial = serial
        self.log_level = log_level
        self.filter_str = filter_str
        self.running = True
        self.process = None

    def run(self):
        if not self.serial:
            return

        cmd = [adb_manager.adb_bin, "-s", self.serial, "logcat", f"*:{self.log_level}"]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=CREATE_NO_WINDOW,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                if line:
                    if not self.filter_str or self.filter_str.lower() in line.lower():
                        self.new_line.emit(line.rstrip())
            self.process.stdout.close()
        except Exception as e:
            self.new_line.emit(f"[Logcat Error] {e}")

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass

class TerminalTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.cmd_history = []
        self.history_index = -1
        self.logcat_worker = None
        self.init_ui()

        # Connect to ADB manager log emitter
        adb_manager.log_emitted.connect(self.on_adb_log_emitted)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        self.sub_tabs = QTabWidget()

        # Tab 1: Shell Console
        tab_shell = QWidget()
        shell_layout = QVBoxLayout(tab_shell)
        shell_layout.setContentsMargins(6, 6, 6, 6)
        shell_layout.setSpacing(6)

        # Quick Presets
        presets_row = QHBoxLayout()
        presets_row.setSpacing(6)
        lbl_pre = QLabel("Quick Shell Presets:")
        lbl_pre.setStyleSheet("color: #64748b; font-weight: 500; font-size: 11px;")
        presets_row.addWidget(lbl_pre)

        presets = [
            ("List 3rd-Party Apps", "pm list packages -3"),
            ("Battery Status", "dumpsys battery"),
            ("Disk Free", "df -h"),
            ("Top Processes", "top -n 1"),
            ("Device Props", "getprop | head -n 30"),
            ("WLAN Config", "ip addr show wlan0"),
        ]

        for label, cmd_str in presets:
            btn = QPushButton(label)
            btn.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn.clicked.connect(lambda _, c=cmd_str: self.run_shell_preset(c))
            presets_row.addWidget(btn)
        presets_row.addStretch()
        shell_layout.addLayout(presets_row)

        # Terminal Output
        self.txt_shell_output = QTextEdit()
        self.txt_shell_output.setReadOnly(True)
        self.txt_shell_output.setStyleSheet("background-color: #0f172a; color: #38bdf8; font-family: Consolas, monospace; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px;")
        shell_layout.addWidget(self.txt_shell_output)

        # Input Row
        input_row = QHBoxLayout()
        input_row.setSpacing(6)
        lbl_prompt = QLabel("adb shell $")
        lbl_prompt.setStyleSheet("color: #0284c7; font-weight: bold; font-size: 11px;")
        input_row.addWidget(lbl_prompt)

        self.txt_cmd = QLineEdit()
        self.txt_cmd.setPlaceholderText("Ketik perintah adb shell (contoh: ls, getprop, dumpsys)...")
        self.txt_cmd.returnPressed.connect(self.execute_shell_cmd)
        input_row.addWidget(self.txt_cmd)

        btn_run = styled_btn("Jalankan", "primary")
        btn_run.clicked.connect(self.execute_shell_cmd)
        input_row.addWidget(btn_run)

        btn_clear = QPushButton("Bersihkan")
        btn_clear.clicked.connect(self.txt_shell_output.clear)
        input_row.addWidget(btn_clear)

        shell_layout.addLayout(input_row)
        self.sub_tabs.addTab(tab_shell, "💻  ADB Shell Console")

        # Tab 2: Live Logcat Streamer
        tab_logcat = QWidget()
        logcat_layout = QVBoxLayout(tab_logcat)
        logcat_layout.setContentsMargins(6, 6, 6, 6)
        logcat_layout.setSpacing(6)

        lc_ctrl = QHBoxLayout()
        lc_ctrl.setSpacing(6)
        self.btn_lc_stream = styled_btn("▶ Mulai Stream", "primary")
        self.btn_lc_stream.clicked.connect(self.toggle_logcat)
        lc_ctrl.addWidget(self.btn_lc_stream)

        lbl_lvl = QLabel("Level:")
        lbl_lvl.setStyleSheet("color: #64748b; font-size: 11px;")
        self.cb_log_lvl = QComboBox()
        self.cb_log_lvl.addItems(["V (Verbose)", "D (Debug)", "I (Info)", "W (Warning)", "E (Error)", "F (Fatal)"])
        self.cb_log_lvl.setCurrentIndex(0)
        lc_ctrl.addWidget(lbl_lvl)
        lc_ctrl.addWidget(self.cb_log_lvl)

        lbl_filter = QLabel("Filter:")
        lbl_filter.setStyleSheet("color: #64748b; font-size: 11px;")
        self.txt_lc_filter = QLineEdit()
        self.txt_lc_filter.setPlaceholderText("Filter tag atau teks...")
        lc_ctrl.addWidget(lbl_filter)
        lc_ctrl.addWidget(self.txt_lc_filter)

        btn_lc_clear = QPushButton("Bersihkan")
        btn_lc_clear.clicked.connect(self.clear_logcat)
        btn_lc_export = QPushButton("💾 Ekspor Log...")
        btn_lc_export.clicked.connect(self.export_logcat)

        lc_ctrl.addWidget(btn_lc_clear)
        lc_ctrl.addWidget(btn_lc_export)
        logcat_layout.addLayout(lc_ctrl)

        self.txt_logcat = QTextEdit()
        self.txt_logcat.setReadOnly(True)
        self.txt_logcat.setStyleSheet("background-color: #0f172a; color: #4ade80; font-family: Consolas, monospace; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px;")
        logcat_layout.addWidget(self.txt_logcat)

        self.sub_tabs.addTab(tab_logcat, "📜  Live Logcat Stream")

        # Tab 3: System ADB Command Audit Log
        tab_audit = QWidget()
        audit_layout = QVBoxLayout(tab_audit)
        audit_layout.setContentsMargins(6, 6, 6, 6)
        audit_layout.setSpacing(6)

        audit_top = QHBoxLayout()
        lbl_audit_desc = QLabel("Catatan riwayat seluruh perintah ADB yang dipanggil oleh aplikasi:")
        lbl_audit_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        btn_clear_audit = QPushButton("Bersihkan Riwayat")
        btn_clear_audit.clicked.connect(lambda: self.txt_audit.clear())

        audit_top.addWidget(lbl_audit_desc)
        audit_top.addStretch()
        audit_top.addWidget(btn_clear_audit)
        audit_layout.addLayout(audit_top)

        self.txt_audit = QTextEdit()
        self.txt_audit.setReadOnly(True)
        self.txt_audit.setStyleSheet("background-color: #0f172a; color: #cbd5e1; font-family: Consolas, monospace; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 4px; padding: 6px;")
        audit_layout.addWidget(self.txt_audit)

        self.sub_tabs.addTab(tab_audit, "🔍  Riwayat Perintah ADB")

        layout.addWidget(self.sub_tabs)

    def set_device(self, serial: str):
        self.current_serial = serial
        if self.logcat_worker and self.logcat_worker.isRunning():
            self.stop_logcat()

    def run_shell_preset(self, cmd_str: str):
        self.txt_cmd.setText(cmd_str)
        self.execute_shell_cmd()

    def execute_shell_cmd(self):
        cmd = self.txt_cmd.text().strip()
        if not cmd:
            return

        if not self.current_serial:
            self.txt_shell_output.append("<font color='#f87171'>[Error] No active device selected.</font>")
            return

        self.cmd_history.append(cmd)
        self.history_index = len(self.cmd_history)
        self.txt_cmd.clear()

        self.txt_shell_output.append(f"<font color='#38bdf8'><b>$ {cmd}</b></font>")
        ok, out = adb_manager.run_adb(["shell", cmd], serial=self.current_serial)
        if out:
            self.txt_shell_output.append(out)
        self.txt_shell_output.verticalScrollBar().setValue(self.txt_shell_output.verticalScrollBar().maximum())

    def toggle_logcat(self):
        if self.logcat_worker and self.logcat_worker.isRunning():
            self.stop_logcat()
        else:
            self.start_logcat()

    def start_logcat(self):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Please select a device for logcat.")
            return

        lvl = self.cb_log_lvl.currentText()[0]
        flt = self.txt_lc_filter.text().strip()

        self.logcat_worker = LogcatWorker(self.current_serial, log_level=lvl, filter_str=flt)
        self.logcat_worker.new_line.connect(self.append_logcat_line)
        self.logcat_worker.start()

        self.btn_lc_stream.setText("⏹ Stop Streaming")
        self.btn_lc_stream.setStyleSheet("background-color: #dc2626;")

    def stop_logcat(self):
        if self.logcat_worker:
            self.logcat_worker.stop()
            self.logcat_worker.wait(1000)
            self.logcat_worker = None
        self.btn_lc_stream.setText("▶ Start Streaming")
        self.btn_lc_stream.setStyleSheet("")

    def append_logcat_line(self, line: str):
        # Colorize by level
        color = "#e5e7eb"
        if " E " in line or " E/" in line:
            color = "#f87171"
        elif " W " in line or " W/" in line:
            color = "#fbbf24"
        elif " I " in line or " I/" in line:
            color = "#38bdf8"
        elif " D " in line or " D/" in line:
            color = "#a7f3d0"

        self.txt_logcat.append(f"<font color='{color}'>{line}</font>")
        # Auto scroll to bottom
        self.txt_logcat.verticalScrollBar().setValue(self.txt_logcat.verticalScrollBar().maximum())

    def clear_logcat(self):
        self.txt_logcat.clear()
        if self.current_serial:
            adb_manager.run_adb(["logcat", "-c"], serial=self.current_serial)

    def export_logcat(self):
        text = self.txt_logcat.toPlainText()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Logcat", "logcat.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Exported", f"Logcat saved to:\n{path}")

    def on_adb_log_emitted(self, command: str, output: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_audit.append(f"<font color='#38bdf8'><b>[{timestamp}] CMD:</b> {command}</font>")
        if output:
            preview = output[:300] + ("..." if len(output) > 300 else "")
            self.txt_audit.append(f"<font color='#94a3b8'>{preview}</font><br>")
