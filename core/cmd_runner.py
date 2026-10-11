import os
import sys
from pathlib import Path

# Ensure root dir is in sys.path for direct debugging
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import subprocess
from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal
from core.settings import settings

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

class CommandRunner(QObject):
    """Singleton dispatcher for executing external binaries (ADB & Fastboot) safely."""
    log_emitted = Signal(str, str)  # (command_executed, output_or_error)

    def run(self, args: List[str], timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute an external command synchronously without popping up a console window.
        Returns (success: bool, output: str).
        """
        cmd_str = " ".join(args)
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=CREATE_NO_WINDOW,
                encoding='utf-8',
                errors='replace'
            )
            stdout, stderr = process.communicate(timeout=timeout)
            output = (stdout + "\n" + stderr).strip()
            success = (process.returncode == 0)
            self.log_emitted.emit(cmd_str, output)
            return success, output
        except subprocess.TimeoutExpired:
            process.kill()
            msg = f"Command timed out after {timeout} seconds"
            self.log_emitted.emit(cmd_str, msg)
            return False, msg
        except Exception as e:
            msg = f"Execution error: {str(e)}"
            self.log_emitted.emit(cmd_str, msg)
            return False, msg

    def run_adb(self, args: List[str], serial: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str]:
        """Run an ADB command with auto-resolved adb binary path."""
        adb_bin = settings.get("adb_path") or "adb"
        full_args = [adb_bin]
        if serial:
            full_args.extend(["-s", serial])
        full_args.extend(args)
        return self.run(full_args, timeout=timeout)

    def run_fastboot(self, args: List[str], serial: Optional[str] = None, timeout: int = 45) -> Tuple[bool, str]:
        """Run a Fastboot command with auto-resolved fastboot binary path."""
        fb_bin = settings.get("fastboot_path") or "fastboot"
        full_args = [fb_bin]
        if serial:
            full_args.extend(["-s", serial])
        full_args.extend(args)
        return self.run(full_args, timeout=timeout)

# Global singleton
cmd_runner = CommandRunner()

if __name__ == "__main__":
    print("Testing Command Runner...")
    ok, out = cmd_runner.run_adb(["version"])
    print(f"Success: {ok}\nOutput:\n{out}")
