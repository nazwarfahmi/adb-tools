import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Tuple
from core.cmd_runner import cmd_runner
from core.settings import settings

def start_server() -> Tuple[bool, str]:
    """Start the ADB server daemon."""
    adb_bin = settings.get("adb_path") or "adb"
    return cmd_runner.run([adb_bin, "start-server"])

def kill_server() -> Tuple[bool, str]:
    """Kill the currently running ADB server daemon."""
    adb_bin = settings.get("adb_path") or "adb"
    return cmd_runner.run([adb_bin, "kill-server"])

def restart_server() -> Tuple[bool, str]:
    """Kill and immediately restart the ADB server daemon."""
    kill_server()
    return start_server()

if __name__ == "__main__":
    print("Testing Server Service...")
    ok, out = start_server()
    print(f"Start server: {ok}, {out}")
