import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import List, Dict, Tuple
from core.cmd_runner import cmd_runner

def list_files(serial: str, remote_path: str) -> List[Dict[str, str]]:
    """
    List directory contents on device.
    Returns: List of dicts [{"name", "is_dir", "is_link", "size", "date", "perms", "path"}]
    """
    clean_path = remote_path.rstrip("/") + "/"
    success, out = cmd_runner.run_adb(["shell", f"ls -la '{clean_path}'"], serial=serial)
    if not success:
        return []

    entries = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("total ") or line.startswith("ls:"):
            continue

        parts = line.split(None, 7)
        if len(parts) >= 8:
            perms = parts[0]
            is_dir = perms.startswith("d")
            is_link = perms.startswith("l")
            size = parts[4]
            date_str = f"{parts[5]} {parts[6]}"
            name = parts[7]

            if name in [".", ".."]:
                continue

            if is_link and " -> " in name:
                name = name.split(" -> ")[0]

            entries.append({
                "name": name,
                "is_dir": is_dir,
                "is_link": is_link,
                "size": size if not is_dir else "",
                "date": date_str,
                "perms": perms,
                "path": f"{clean_path}{name}".replace("//", "/")
            })
        else:
            name = parts[-1] if parts else line
            if name not in [".", ".."]:
                entries.append({
                    "name": name,
                    "is_dir": False,
                    "is_link": False,
                    "size": "",
                    "date": "",
                    "perms": "",
                    "path": f"{clean_path}{name}".replace("//", "/")
                })
    return sorted(entries, key=lambda x: (not x["is_dir"], x["name"].lower()))

def push_file(serial: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
    """Push local PC file or directory to remote Android path."""
    return cmd_runner.run_adb(["push", local_path, remote_path], serial=serial, timeout=300)

def pull_file(serial: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
    """Download remote Android file or directory to local PC path."""
    return cmd_runner.run_adb(["pull", remote_path, local_path], serial=serial, timeout=300)

def delete_remote(serial: str, remote_path: str) -> Tuple[bool, str]:
    """Recursively delete a remote file or folder."""
    return cmd_runner.run_adb(["shell", f"rm -rf '{remote_path}'"], serial=serial)

def mkdir_remote(serial: str, remote_path: str) -> Tuple[bool, str]:
    """Create directory on remote device."""
    return cmd_runner.run_adb(["shell", f"mkdir -p '{remote_path}'"], serial=serial)

def rename_remote(serial: str, old_path: str, new_path: str) -> Tuple[bool, str]:
    """Rename or move a remote file or directory."""
    return cmd_runner.run_adb(["shell", f"mv '{old_path}' '{new_path}'"], serial=serial)

if __name__ == "__main__":
    print("Testing File Service...")
    from core.device_service import get_adb_devices
    devs = get_adb_devices()
    if devs:
        s = devs[0]["serial"]
        print(f"Listing /sdcard on {s}...")
        files = list_files(s, "/sdcard")
        print(f"Found {len(files)} items. Sample: {[f['name'] for f in files[:5]]}")
    else:
        print("No device attached to test file service.")
