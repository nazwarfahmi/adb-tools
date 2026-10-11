import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import subprocess
from typing import Tuple
from core.cmd_runner import cmd_runner, CREATE_NO_WINDOW
from core.settings import settings

def send_key(serial: str, keycode: int) -> Tuple[bool, str]:
    """
    Send an Android keyevent.
    Keycodes: 3=Home, 4=Back, 24=VolUp, 25=VolDown, 26=Power, 187=RecentApps
    """
    return cmd_runner.run_adb(["shell", "input", "keyevent", str(keycode)], serial=serial)

def send_text(serial: str, text: str) -> Tuple[bool, str]:
    """Type text into currently focused Android input field."""
    safe_text = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
    return cmd_runner.run_adb(["shell", "input", "text", safe_text], serial=serial)

def take_screenshot(serial: str, local_dest_path: str) -> bool:
    """Capture device screen directly to local PNG file using exec-out."""
    adb_bin = settings.get("adb_path") or "adb"
    try:
        with open(local_dest_path, "wb") as f:
            process = subprocess.Popen(
                [adb_bin, "-s", serial, "exec-out", "screencap", "-p"],
                stdout=f,
                stderr=subprocess.PIPE,
                creationflags=CREATE_NO_WINDOW
            )
            _, stderr = process.communicate(timeout=15)
            return process.returncode == 0
    except Exception as e:
        cmd_runner.log_emitted.emit("screencap", f"Screenshot capture error: {e}")
        return False

def get_clipboard(serial: str) -> str:
    """Retrieve text from Android clipboard (Android 10+)."""
    success, out = cmd_runner.run_adb(["shell", "cmd", "clipboard", "get"], serial=serial)
    return out if success else ""

def set_clipboard(serial: str, text: str) -> Tuple[bool, str]:
    """Set Android device clipboard content."""
    return cmd_runner.run_adb(["shell", "cmd", "clipboard", "set", text], serial=serial)

if __name__ == "__main__":
    print("Testing Control Service...")
    from core.device_service import get_adb_devices
    devs = get_adb_devices()
    if devs:
        s = devs[0]["serial"]
        print(f"Testing screenshot on {s}...")
        ok = take_screenshot(s, "test_screen.png")
        print(f"Screenshot success: {ok}")
    else:
        print("No device attached to test control service.")
