import re
import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import List, Dict, Tuple
from core.cmd_runner import cmd_runner

def get_adb_devices() -> List[Dict[str, str]]:
    """
    List connected ADB devices with status and model name.
    Returns: List of dicts [{"serial": ..., "state": ..., "model": ...}]
    """
    success, out = cmd_runner.run_adb(["devices", "-l"])
    if not success:
        return []

    devices = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("*") or line.startswith("List of devices"):
            continue

        parts = line.split()
        if len(parts) >= 2:
            serial = parts[0]
            state = parts[1]  # 'device', 'unauthorized', 'offline', 'recovery', 'sideload'
            dev_info = {"serial": serial, "state": state, "model": "", "product": "", "device": ""}
            for part in parts[2:]:
                if ":" in part:
                    k, v = part.split(":", 1)
                    if k in dev_info:
                        dev_info[k] = v
            devices.append(dev_info)
    return devices

def get_fastboot_devices() -> List[Dict[str, str]]:
    """List connected Fastboot devices."""
    success, out = cmd_runner.run_fastboot(["devices"])
    if not success:
        return []

    devices = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 1:
            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "fastboot"
            devices.append({"serial": serial, "state": state, "model": "Fastboot Device"})
    return devices

def get_device_props(serial: str) -> Dict[str, str]:
    """Retrieve all getprop key-value pairs from the device."""
    success, out = cmd_runner.run_adb(["shell", "getprop"], serial=serial)
    if not success:
        return {}

    props = {}
    for line in out.splitlines():
        match = re.match(r'\[(.*?)\]:\s*\[(.*?)\]', line)
        if match:
            props[match.group(1)] = match.group(2)
    return props

def get_battery_info(serial: str) -> Dict[str, str]:
    """Parse 'dumpsys battery' for battery metrics."""
    success, out = cmd_runner.run_adb(["shell", "dumpsys", "battery"], serial=serial)
    if not success:
        return {}

    data = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip().lower()] = v.strip()
    return data

def get_display_info(serial: str) -> Tuple[str, str]:
    """Return (resolution, density_dpi)."""
    _, size_out = cmd_runner.run_adb(["shell", "wm", "size"], serial=serial)
    _, dens_out = cmd_runner.run_adb(["shell", "wm", "density"], serial=serial)

    res = "Unknown"
    dens = "Unknown"
    for line in size_out.splitlines():
        if "size:" in line:
            res = line.split("size:", 1)[1].strip()
    for line in dens_out.splitlines():
        if "density:" in line:
            dens = line.split("density:", 1)[1].strip() + " DPI"
    return res, dens

def get_storage_info(serial: str) -> Dict[str, str]:
    """Return storage usage details for /data partition."""
    success, out = cmd_runner.run_adb(["shell", "df", "-h", "/data"], serial=serial)
    if not success:
        return {}
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) >= 2:
        parts = lines[-1].split()
        if len(parts) >= 5:
            return {
                "total": parts[1],
                "used": parts[2],
                "free": parts[3],
                "percent": parts[4]
            }
    return {}

def get_ram_info(serial: str) -> Dict[str, str]:
    """Return RAM memory information from /proc/meminfo."""
    success, out = cmd_runner.run_adb(["shell", "cat", "/proc/meminfo"], serial=serial)
    if not success:
        return {}
    info = {}
    for line in out.splitlines()[:6]:
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return info

def get_ip_address(serial: str) -> str:
    """Retrieve device Wi-Fi IP address."""
    success, out = cmd_runner.run_adb(["shell", "ip", "route"], serial=serial)
    if success:
        match = re.search(r'src\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', out)
        if match:
            return match.group(1)

    _, out2 = cmd_runner.run_adb(["shell", "ifconfig", "wlan0"], serial=serial)
    match2 = re.search(r'inet addr:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', out2)
    if match2:
        return match2.group(1)
    return "Not Connected"

if __name__ == "__main__":
    print("Testing Device Service...")
    devs = get_adb_devices()
    print(f"Connected ADB devices: {devs}")
    fb_devs = get_fastboot_devices()
    print(f"Connected Fastboot devices: {fb_devs}")
