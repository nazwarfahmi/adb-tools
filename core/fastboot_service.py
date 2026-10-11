import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Optional, Tuple
from core.cmd_runner import cmd_runner

def fastboot_reboot(serial: Optional[str] = None, mode: str = "system") -> Tuple[bool, str]:
    """Reboot from fastboot mode into system, recovery, bootloader, or fastbootd."""
    mode = mode.lower()
    if mode == "system":
        return cmd_runner.run_fastboot(["reboot"], serial=serial)
    elif mode == "bootloader":
        return cmd_runner.run_fastboot(["reboot-bootloader"], serial=serial)
    elif mode == "recovery":
        return cmd_runner.run_fastboot(["reboot", "recovery"], serial=serial)
    elif mode == "fastbootd":
        return cmd_runner.run_fastboot(["reboot", "fastboot"], serial=serial)
    return False, f"Unknown fastboot reboot mode: {mode}"

def fastboot_getvar_all(serial: Optional[str] = None) -> Tuple[bool, str]:
    """Retrieve all bootloader variables via getvar all."""
    return cmd_runner.run_fastboot(["getvar", "all"], serial=serial)

if __name__ == "__main__":
    print("Testing Fastboot Service...")
    from core.device_service import get_fastboot_devices
    fb_devs = get_fastboot_devices()
    print(f"Fastboot devices detected: {fb_devs}")
