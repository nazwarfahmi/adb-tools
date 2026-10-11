import os
import sys
import json
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from PySide6.QtCore import QObject, Signal, QThread
from core.settings import settings

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

DEFAULT_SCRCPY_RELEASES = [
    {
        "tag": "v5.0.1",
        "name": "scrcpy 5.0.1 (Latest)",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v5.0.1/scrcpy-win64-v5.0.1.zip",
        "size_mb": 15.2,
        "published": "2025-02"
    },
    {
        "tag": "v5.0",
        "name": "scrcpy 5.0",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v5.0/scrcpy-win64-v5.0.zip",
        "size_mb": 15.1,
        "published": "2025-01"
    },
    {
        "tag": "v4.1",
        "name": "scrcpy 4.1",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v4.1/scrcpy-win64-v4.1.zip",
        "size_mb": 14.8,
        "published": "2024-11"
    },
    {
        "tag": "v4.0",
        "name": "scrcpy 4.0",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v4.0/scrcpy-win64-v4.0.zip",
        "size_mb": 14.7,
        "published": "2024-09"
    },
    {
        "tag": "v3.3.4",
        "name": "scrcpy 3.3.4",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v3.3.4/scrcpy-win64-v3.3.4.zip",
        "size_mb": 14.2,
        "published": "2024-06"
    },
    {
        "tag": "v3.1",
        "name": "scrcpy 3.1",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-win64-v3.1.zip",
        "size_mb": 13.9,
        "published": "2024-03"
    },
    {
        "tag": "v3.0.2",
        "name": "scrcpy 3.0.2",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v3.0.2/scrcpy-win64-v3.0.2.zip",
        "size_mb": 13.8,
        "published": "2024-02"
    },
    {
        "tag": "v2.7",
        "name": "scrcpy 2.7 (Legacy Stable)",
        "url": "https://github.com/Genymobile/scrcpy/releases/download/v2.7/scrcpy-win64-v2.7.zip",
        "size_mb": 12.5,
        "published": "2023-11"
    }
]

class ScrcpyReleasesWorker(QThread):
    """Worker to fetch available scrcpy releases asynchronously from GitHub."""
    releases_loaded = Signal(list, bool, str)  # releases_list, from_github, message

    def run(self):
        cache_file = Path(__file__).resolve().parent.parent / "data" / "scrcpy_releases.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        url = "https://api.github.com/repos/Genymobile/scrcpy/releases?per_page=25"
        req = urllib.request.Request(url, headers={"User-Agent": "ADB-Studio-Suite"})

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                parsed = []
                for r in raw:
                    tag = r.get("tag_name", "")
                    name = r.get("name") or tag
                    published = r.get("published_at", "")[:10]
                    win64_url = None
                    size_mb = 0.0

                    for a in r.get("assets", []):
                        a_name = a.get("name", "").lower()
                        if "win64" in a_name and a_name.endswith(".zip"):
                            win64_url = a.get("browser_download_url")
                            size_mb = round(a.get("size", 0) / (1024 * 1024), 1)
                            break

                    if win64_url:
                        parsed.append({
                            "tag": tag,
                            "name": name,
                            "url": win64_url,
                            "size_mb": size_mb,
                            "published": published
                        })

                if parsed:
                    # Save to cache
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(parsed, f, indent=2)
                    self.releases_loaded.emit(parsed, True, f"Ditemukan {len(parsed)} versi resmi dari GitHub.")
                    return

        except Exception as e:
            err_msg = str(e)

        # Fallback to local cache if available
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached:
                        self.releases_loaded.emit(cached, False, f"Memuat {len(cached)} versi dari cache lokal.")
                        return
            except Exception:
                pass

        # Built-in fallback
        self.releases_loaded.emit(DEFAULT_SCRCPY_RELEASES, False, "Menggunakan daftar rilis bawaan.")

class ScrcpyVersionDownloadWorker(QThread):
    """Worker to download and extract a specific scrcpy version from GitHub."""
    progress = Signal(int, str)  # percent, message
    finished_download = Signal(bool, str, str)  # success, tag, exe_path_or_err

    def __init__(self, tag: str, download_url: str):
        super().__init__()
        self.tag = tag
        self.download_url = download_url

    def run(self):
        try:
            self.progress.emit(5, f"Mempersiapkan folder unduhan untuk Scrcpy {self.tag}...")
            versions_dir = Path(__file__).resolve().parent.parent / "bin" / "scrcpy_versions" / self.tag
            versions_dir.mkdir(parents=True, exist_ok=True)

            zip_dest = versions_dir / f"scrcpy_{self.tag}.zip"

            self.progress.emit(15, f"Mengunduh Scrcpy {self.tag} dari GitHub...")

            def report_hook(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    pct = min(int((downloaded / total_size) * 65) + 15, 80)
                    mb_cur = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    self.progress.emit(pct, f"Mengunduh {self.tag}: {mb_cur:.1f} MB / {mb_tot:.1f} MB ({pct}%)")

            urllib.request.urlretrieve(self.download_url, zip_dest, reporthook=report_hook)

            self.progress.emit(85, f"Mengekstrak file Scrcpy {self.tag}...")
            with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
                zip_ref.extractall(versions_dir)

            # Cleanup zip
            if zip_dest.exists():
                zip_dest.unlink()

            # Locate scrcpy.exe inside the extracted folder
            found_exe = None
            for p in versions_dir.rglob("scrcpy.exe"):
                found_exe = str(p)
                break

            if found_exe and os.path.isfile(found_exe):
                settings.set("scrcpy_path", found_exe)
                self.progress.emit(100, f"Scrcpy {self.tag} berhasil diunduh dan diaktifkan!")
                self.finished_download.emit(True, self.tag, found_exe)
            else:
                self.finished_download.emit(False, self.tag, "scrcpy.exe tidak ditemukan di dalam paket yang diekstrak.")

        except Exception as e:
            self.finished_download.emit(False, self.tag, f"Gagal mengunduh {self.tag}: {str(e)}")

class ScrcpyWatcher(QThread):
    """Watches scrcpy subprocess asynchronously, prevents pipe deadlock, and emits finished signal upon exit."""
    process_finished = Signal(int, str)  # exit_code, stderr

    def __init__(self, process: subprocess.Popen):
        super().__init__()
        self.process = process

    def run(self):
        stderr_text = ""
        try:
            _, err = self.process.communicate()
            if err:
                stderr_text = err.decode("utf-8", errors="replace")
        except Exception:
            pass
        exit_code = self.process.poll()
        if exit_code is None:
            exit_code = 0
        self.process_finished.emit(exit_code, stderr_text)

class ScrcpyManager(QObject):
    process_started = Signal()
    process_ended = Signal(int)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.process: Optional[subprocess.Popen] = None
        self._watcher: Optional[ScrcpyWatcher] = None

    @property
    def scrcpy_bin(self) -> str:
        return settings.get("scrcpy_path") or "scrcpy"

    def get_versions_dir(self) -> Path:
        p = Path(__file__).resolve().parent.parent / "bin" / "scrcpy_versions"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_installed_versions(self) -> Dict[str, str]:
        """Scans local directories for downloaded scrcpy versions. Returns {tag: path}."""
        installed = {}
        v_dir = self.get_versions_dir()

        # Check versions inside bin/scrcpy_versions/
        if v_dir.exists():
            for sub in v_dir.iterdir():
                if sub.is_dir():
                    exe = next(sub.rglob("scrcpy.exe"), None)
                    if exe and exe.is_file():
                        installed[sub.name] = str(exe)

        # Check default bin/scrcpy/
        default_dir = Path(__file__).resolve().parent.parent / "bin" / "scrcpy"
        if default_dir.exists():
            exe = next(default_dir.rglob("scrcpy.exe"), None)
            if exe and exe.is_file():
                if "v3.1" not in installed:
                    installed["v3.1"] = str(exe)

        # Also check current active path from settings
        active_path = settings.get("scrcpy_path")
        if active_path and os.path.isfile(active_path):
            # Check if already tagged
            already_tagged = False
            for tag, path in installed.items():
                if os.path.abspath(path) == os.path.abspath(active_path):
                    already_tagged = True
                    break
            if not already_tagged:
                installed["Custom"] = active_path

        return installed

    def set_active_version_path(self, path: str):
        if path and os.path.isfile(path):
            settings.set("scrcpy_path", path)

    def is_installed(self) -> bool:
        p = self.scrcpy_bin
        if p and os.path.isfile(p):
            return True
        return shutil.which(p) is not None

    def start_mirror(self, serial: str, options: Dict[str, Any]) -> Tuple[bool, str]:
        """Start scrcpy screen mirroring with supplied configuration."""
        if not self.is_installed():
            return False, "Executable Scrcpy tidak ditemukan. Silakan unduh atau pilih path scrcpy.exe terlebih dahulu."

        if self.is_running():
            return False, "Sesi screen mirror sedang berjalan aktif."

        cmd = [self.scrcpy_bin]
        if serial:
            cmd.extend(["-s", serial])

        # Apply display settings
        max_size = options.get("max_size", 0)
        if max_size and int(max_size) > 0:
            cmd.extend(["--max-size", str(max_size)])

        bitrate = options.get("bitrate", "")
        if bitrate and bitrate != "Default":
            cmd.extend(["--video-bit-rate", str(bitrate)])

        max_fps = options.get("max_fps", 0)
        if max_fps and int(max_fps) > 0:
            cmd.extend(["--max-fps", str(max_fps)])

        if options.get("stay_awake", False):
            cmd.append("--stay-awake")

        if options.get("turn_screen_off", False):
            cmd.append("--turn-screen-off")

        if options.get("no_audio", False):
            cmd.append("--no-audio")

        if options.get("fullscreen", False):
            cmd.append("--fullscreen")

        if options.get("always_on_top", False):
            cmd.append("--always-on-top")

        if options.get("show_touches", False):
            cmd.append("--show-touches")

        if options.get("otg", False):
            cmd.append("--otg")

        record_file = options.get("record_file")
        if record_file:
            cmd.extend(["--record", record_file])

        # Prepare environment variable to force scrcpy to use ADB Studio's adb binary
        # This prevents ADB version mismatches and daemon killing!
        env = os.environ.copy()
        adb_bin = settings.get("adb_path") or str(Path(__file__).resolve().parent.parent / "bin" / "adb.exe")
        if os.path.isfile(adb_bin):
            env["ADB"] = str(Path(adb_bin).resolve())

        try:
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=0  # Show Scrcpy GUI window!
            )
            # Start background watcher to react immediately when user closes the Scrcpy window
            self._watcher = ScrcpyWatcher(self.process)
            self._watcher.process_finished.connect(self._on_scrcpy_exit)
            self._watcher.start()

            self.process_started.emit()
            return True, "Scrcpy berhasil dimulai."
        except Exception as e:
            err = f"Gagal menjalankan Scrcpy: {str(e)}"
            self.error_occurred.emit(err)
            return False, err

    def _on_scrcpy_exit(self, exit_code: int, stderr_text: str):
        self.process = None
        self._watcher = None
        self.process_ended.emit(exit_code)
        if exit_code != 0 and stderr_text and "Device disconnected" not in stderr_text:
            self.error_occurred.emit(stderr_text.strip())

    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def stop_mirror(self):
        """Terminate active scrcpy mirroring session."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

        if self._watcher and self._watcher.isRunning():
            try:
                self._watcher.wait(1000)
            except Exception:
                pass
            self._watcher = None

        self.process_ended.emit(0)

scrcpy_manager = ScrcpyManager()
