import os
import sys
import json
import shutil
from pathlib import Path

CONFIG_FILE = Path.home() / ".adb_gui_tools_config.json"

DEFAULT_SETTINGS = {
    "adb_path": "",
    "fastboot_path": "",
    "scrcpy_path": "",
    "default_download_dir": str(Path.home() / "Downloads"),
    "auto_refresh_interval": 3,
    "theme": "dark"
}

def find_executable(name: str, preferred_paths: list[str]) -> str:
    """Find executable by checking preferred paths first, then system PATH."""
    for path_str in preferred_paths:
        if path_str and os.path.isfile(path_str):
            return os.path.abspath(path_str)
    
    which_path = shutil.which(name)
    if which_path:
        return os.path.abspath(which_path)
    return ""

def get_app_dir() -> Path:
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def get_default_adb_path() -> str:
    app_dir = get_app_dir()
    exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else app_dir
    preferred = [
        str(app_dir / "bin" / "adb.exe"),
        str(exe_dir / "bin" / "adb.exe"),
        str(app_dir / "platform-tools" / "adb.exe"),
        str(app_dir / "adb.exe"),
        str(exe_dir / "adb.exe"),
        r"C:\Program Files\platform-tools\adb.exe",
        r"C:\adb\adb.exe",
    ]
    return find_executable("adb", preferred)

def get_default_fastboot_path() -> str:
    app_dir = get_app_dir()
    exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else app_dir
    preferred = [
        str(app_dir / "bin" / "fastboot.exe"),
        str(exe_dir / "bin" / "fastboot.exe"),
        str(app_dir / "platform-tools" / "fastboot.exe"),
        str(app_dir / "fastboot.exe"),
        str(exe_dir / "fastboot.exe"),
        r"C:\Program Files\platform-tools\fastboot.exe",
        r"C:\adb\fastboot.exe",
    ]
    return find_executable("fastboot", preferred)

def get_default_scrcpy_path() -> str:
    app_dir = get_app_dir()
    exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else app_dir
    preferred = [
        str(app_dir / "scrcpy" / "scrcpy.exe"),
        str(exe_dir / "scrcpy" / "scrcpy.exe"),
        str(app_dir / "bin" / "scrcpy" / "scrcpy.exe"),
        str(exe_dir / "bin" / "scrcpy" / "scrcpy.exe"),
        r"C:\scrcpy\scrcpy.exe",
        r"C:\Program Files\scrcpy\scrcpy.exe",
    ]
    return find_executable("scrcpy", preferred)
    return find_executable("scrcpy", preferred)

class AppSettings:
    """Manages persistent application settings."""
    def __init__(self):
        self.data = DEFAULT_SETTINGS.copy()
        self.load()

        # Initialize defaults if not set
        if not self.data.get("adb_path") or not os.path.isfile(self.data["adb_path"]):
            self.data["adb_path"] = get_default_adb_path()
            
        if not self.data.get("fastboot_path") or not os.path.isfile(self.data["fastboot_path"]):
            self.data["fastboot_path"] = get_default_fastboot_path()

        if not self.data.get("scrcpy_path") or not os.path.isfile(self.data["scrcpy_path"]):
            self.data["scrcpy_path"] = get_default_scrcpy_path()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

# Global singleton
settings = AppSettings()
