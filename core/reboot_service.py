import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Tuple
from core.cmd_runner import cmd_runner

def reboot_device(serial: str, mode: str = "system") -> Tuple[bool, str]:
    """
    Reboot device into designated mode:
    'system', 'recovery', 'bootloader', 'fastboot', 'edl', 'sideload'
    """
    mode = mode.lower()
    if mode == "system":
        return cmd_runner.run_adb(["reboot"], serial=serial)
    elif mode == "recovery":
        return cmd_runner.run_adb(["reboot", "recovery"], serial=serial)
    elif mode == "bootloader":
        return cmd_runner.run_adb(["reboot", "bootloader"], serial=serial)
    elif mode == "fastboot":
        return cmd_runner.run_adb(["reboot", "fastboot"], serial=serial)
    elif mode == "edl":
        return cmd_runner.run_adb(["reboot", "edl"], serial=serial)
    elif mode == "sideload":
        return cmd_runner.run_adb(["reboot", "sideload"], serial=serial)
    return False, f"Unknown reboot target mode: {mode}"

if __name__ == "__main__":
    print("Testing Reboot Service...")
    print("Available modes: system, recovery, bootloader, fastboot, edl, sideload")
