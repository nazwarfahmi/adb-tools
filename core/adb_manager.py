"""
ADB Manager Facade.
Aggregates all separated core domain services into a single unified interface:
- cmd_runner: Low-level command execution & logging signals
- device_service: Device discovery, specs, battery, and storage
- package_service: App and APK management
- file_service: Android filesystem navigation and transfers
- control_service: Remote keys, inputs, screenshot, clipboard
- reboot_service: Power management and reboot targets
- fastboot_service: Fastboot flashing, erase, boot, and unlock
- wireless_service: Wi-Fi connection, pairing, TCP/IP setup
- server_service: ADB daemon lifecycle control
"""

from typing import List, Dict, Optional, Tuple
from PySide6.QtCore import QObject, Signal
from core.settings import settings
from core.cmd_runner import cmd_runner, CREATE_NO_WINDOW
from core import (
    device_service,
    package_service,
    file_service,
    control_service,
    reboot_service,
    fastboot_service,
    wireless_service,
    server_service,
    debloater_service
)

class ADBManager(QObject):
    """Unified Facade for all ADB & Fastboot services."""

    def __init__(self):
        super().__init__()
        # Forward command runner log signal
        self.log_emitted = cmd_runner.log_emitted
        self.debloater = debloater_service.debloater_service

    @property
    def adb_bin(self) -> str:
        return settings.get("adb_path") or "adb"

    @property
    def fastboot_bin(self) -> str:
        return settings.get("fastboot_path") or "fastboot"

    # Command Execution
    def run_cmd(self, args: List[str], timeout: int = 30) -> Tuple[bool, str]:
        return cmd_runner.run(args, timeout=timeout)

    def run_adb(self, args: List[str], serial: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str]:
        return cmd_runner.run_adb(args, serial=serial, timeout=timeout)

    def run_fastboot(self, args: List[str], serial: Optional[str] = None, timeout: int = 45) -> Tuple[bool, str]:
        return cmd_runner.run_fastboot(args, serial=serial, timeout=timeout)

    # Server Lifecycle
    def start_server(self) -> Tuple[bool, str]:
        return server_service.start_server()

    def kill_server(self) -> Tuple[bool, str]:
        return server_service.kill_server()

    def restart_server(self) -> Tuple[bool, str]:
        return server_service.restart_server()

    # Device Discovery & Properties
    def get_devices(self) -> List[Dict[str, str]]:
        return device_service.get_adb_devices()

    def get_fastboot_devices(self) -> List[Dict[str, str]]:
        return device_service.get_fastboot_devices()

    def get_device_props(self, serial: str) -> Dict[str, str]:
        return device_service.get_device_props(serial)

    def get_battery_info(self, serial: str) -> Dict[str, str]:
        return device_service.get_battery_info(serial)

    def get_display_info(self, serial: str) -> Tuple[str, str]:
        return device_service.get_display_info(serial)

    def get_storage_info(self, serial: str) -> Dict[str, str]:
        return device_service.get_storage_info(serial)

    def get_ram_info(self, serial: str) -> Dict[str, str]:
        return device_service.get_ram_info(serial)

    def get_ip_address(self, serial: str) -> str:
        return device_service.get_ip_address(serial)

    # Package & APK Operations
    def list_packages(self, serial: str, filter_type: str = "all") -> List[Dict[str, str]]:
        return package_service.list_packages(serial, filter_type=filter_type)

    def install_apk(self, serial: str, apk_path: str, reinstall: bool = True, downgrade: bool = False, grant_perms: bool = True) -> Tuple[bool, str]:
        return package_service.install_apk(serial, apk_path, reinstall=reinstall, downgrade=downgrade, grant_perms=grant_perms)

    def uninstall_package(self, serial: str, package_name: str, keep_data: bool = False) -> Tuple[bool, str]:
        return package_service.uninstall_package(serial, package_name, keep_data=keep_data)

    def clear_package_data(self, serial: str, package_name: str) -> Tuple[bool, str]:
        return package_service.clear_package_data(serial, package_name)

    def force_stop_package(self, serial: str, package_name: str) -> Tuple[bool, str]:
        return package_service.force_stop_package(serial, package_name)

    def disable_package(self, serial: str, package_name: str) -> Tuple[bool, str]:
        return package_service.disable_package(serial, package_name)

    def enable_package(self, serial: str, package_name: str) -> Tuple[bool, str]:
        return package_service.enable_package(serial, package_name)

    def get_disabled_packages(self, serial: str) -> set:
        return package_service.get_disabled_packages(serial)

    def get_installed_packages(self, serial: str) -> set:
        return package_service.get_installed_packages(serial)

    def launch_app(self, serial: str, package_name: str) -> Tuple[bool, str]:
        return package_service.launch_app(serial, package_name)

    def pull_apk(self, serial: str, remote_apk_path: str, local_save_path: str) -> Tuple[bool, str]:
        return package_service.pull_apk(serial, remote_apk_path, local_save_path)

    # File Explorer Operations
    def list_files(self, serial: str, remote_path: str) -> List[Dict[str, str]]:
        return file_service.list_files(serial, remote_path)

    def push_file(self, serial: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
        return file_service.push_file(serial, local_path, remote_path)

    def pull_file(self, serial: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
        return file_service.pull_file(serial, remote_path, local_path)

    def delete_remote(self, serial: str, remote_path: str) -> Tuple[bool, str]:
        return file_service.delete_remote(serial, remote_path)

    def mkdir_remote(self, serial: str, remote_path: str) -> Tuple[bool, str]:
        return file_service.mkdir_remote(serial, remote_path)

    # Remote Inputs & Screen Controls
    def send_key(self, serial: str, keycode: int) -> Tuple[bool, str]:
        return control_service.send_key(serial, keycode)

    def send_text(self, serial: str, text: str) -> Tuple[bool, str]:
        return control_service.send_text(serial, text)

    def take_screenshot(self, serial: str, local_dest_path: str) -> bool:
        return control_service.take_screenshot(serial, local_dest_path)

    def get_clipboard(self, serial: str) -> str:
        return control_service.get_clipboard(serial)

    def set_clipboard(self, serial: str, text: str) -> Tuple[bool, str]:
        return control_service.set_clipboard(serial, text)

    # Reboot Targets
    def reboot(self, serial: str, mode: str = "system") -> Tuple[bool, str]:
        return reboot_service.reboot_device(serial, mode=mode)

    # Fastboot Operations
    def fastboot_reboot(self, serial: Optional[str] = None, mode: str = "system") -> Tuple[bool, str]:
        return fastboot_service.fastboot_reboot(serial=serial, mode=mode)

    def fastboot_getvar_all(self, serial: Optional[str] = None) -> Tuple[bool, str]:
        return fastboot_service.fastboot_getvar_all(serial=serial)

    # Wireless Operations
    def wireless_connect(self, ip_port: str) -> Tuple[bool, str]:
        return wireless_service.connect_wireless(ip_port)

    def wireless_disconnect(self, ip_port: str) -> Tuple[bool, str]:
        return wireless_service.disconnect_wireless(ip_port)

    def wireless_pair(self, ip_port: str, code: str) -> Tuple[bool, str]:
        return wireless_service.pair_wireless(ip_port, code)

    def enable_tcpip(self, serial: str, port: int = 5555) -> Tuple[bool, str]:
        return wireless_service.enable_tcpip(serial, port=port)

    # Private DNS & Ad-Blocking Operations
    def get_private_dns(self, serial: str) -> Tuple[str, str]:
        """Returns (mode, specifier/hostname). Mode is usually 'hostname', 'off', or 'opportunistic'."""
        _, mode = cmd_runner.run_adb(["shell", "settings", "get", "global", "private_dns_mode"], serial=serial)
        _, spec = cmd_runner.run_adb(["shell", "settings", "get", "global", "private_dns_specifier"], serial=serial)
        mode = mode.strip() if mode else "off"
        spec = spec.strip() if spec and spec.strip() != "null" else ""
        return mode, spec

    def set_private_dns(self, serial: str, hostname: str) -> Tuple[bool, str]:
        """Set Android Private DNS to custom hostname (e.g. dns.adguard-dns.com)."""
        ok1, out1 = cmd_runner.run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"], serial=serial)
        if not ok1:
            return False, out1
        ok2, out2 = cmd_runner.run_adb(["shell", "settings", "put", "global", "private_dns_specifier", hostname], serial=serial)
        return ok2, out2

    def disable_private_dns(self, serial: str) -> Tuple[bool, str]:
        """Reset Android Private DNS back to default off/automatic."""
        ok1, _ = cmd_runner.run_adb(["shell", "settings", "put", "global", "private_dns_mode", "off"], serial=serial)
        ok2, out2 = cmd_runner.run_adb(["shell", "settings", "delete", "global", "private_dns_specifier"], serial=serial)
        return ok1, out2

    def block_app_background(self, serial: str, package_name: str) -> Tuple[bool, str]:
        """Restrict background execution for an app via AppOps."""
        return cmd_runner.run_adb(["shell", "cmd", "appops", "set", package_name, "RUN_IN_BACKGROUND", "ignore"], serial=serial)

    def allow_app_background(self, serial: str, package_name: str) -> Tuple[bool, str]:
        """Allow background execution for an app via AppOps."""
        return cmd_runner.run_adb(["shell", "cmd", "appops", "set", package_name, "RUN_IN_BACKGROUND", "allow"], serial=serial)

# Global singleton
adb_manager = ADBManager()
