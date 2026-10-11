import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Tuple
from core.cmd_runner import cmd_runner

def connect_wireless(ip_port: str) -> Tuple[bool, str]:
    """Connect to a device over TCP/IP: adb connect <ip>:<port>."""
    return cmd_runner.run_adb(["connect", ip_port])

def disconnect_wireless(ip_port: str) -> Tuple[bool, str]:
    """Disconnect a wireless device: adb disconnect <ip>:<port>."""
    return cmd_runner.run_adb(["disconnect", ip_port])

def pair_wireless(ip_port: str, code: str) -> Tuple[bool, str]:
    """Pair an Android 11+ device: adb pair <ip>:<port> <code>."""
    return cmd_runner.run_adb(["pair", ip_port, code])

def enable_tcpip(serial: str, port: int = 5555) -> Tuple[bool, str]:
    """Restart adbd listening on TCP on specified port: adb tcpip <port>."""
    return cmd_runner.run_adb(["tcpip", str(port)], serial=serial)

if __name__ == "__main__":
    print("Testing Wireless Service...")
    print("Use connect_wireless('192.168.1.x:5555') to test.")
