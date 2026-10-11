import sys
from pathlib import Path
ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import List, Dict, Tuple
from core.cmd_runner import cmd_runner

def list_packages(serial: str, filter_type: str = "all") -> List[Dict[str, str]]:
    """
    List installed packages with APK paths.
    filter_type options: 'all', 'user', 'system', 'disabled'
    """
    flag_map = {
        "all": ["-f"],
        "all_uninstalled": ["-u", "-f"],
        "user": ["-3", "-f"],
        "system": ["-s", "-f"],
        "system_uninstalled": ["-s", "-u", "-f"],
        "disabled": ["-d", "-f"]
    }
    flags = flag_map.get(filter_type, ["-f"])
    success, out = cmd_runner.run_adb(["shell", "pm", "list", "packages"] + flags, serial=serial)
    if not success and filter_type in ("all_uninstalled", "system_uninstalled"):
        # Fallback if device doesn't support -u flag
        fallback_flags = ["-s", "-f"] if filter_type == "system_uninstalled" else ["-f"]
        success, out = cmd_runner.run_adb(["shell", "pm", "list", "packages"] + fallback_flags, serial=serial)

    if not success:
        return []

    packages = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            raw = line[8:]
            if "=" in raw:
                apk_path, pkg_name = raw.rsplit("=", 1)
                packages.append({"name": pkg_name.strip(), "path": apk_path.strip()})
            else:
                packages.append({"name": raw.strip(), "path": ""})
    return sorted(packages, key=lambda x: x["name"])

def get_packages_install_times(serial: str) -> Dict[str, str]:
    """Retrieve firstInstallTime for all packages in a single dumpsys command."""
    success, out = cmd_runner.run_adb(["shell", "dumpsys", "package"], serial=serial, timeout=12)
    if not success or not out:
        return {}

    times = {}
    cur_pkg = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Package [") and "]" in line:
            cur_pkg = line[9:line.index("]")]
        elif cur_pkg and line.startswith("firstInstallTime="):
            times[cur_pkg] = line.split("=", 1)[1].strip()
            cur_pkg = None
    return times


def get_disabled_packages(serial: str) -> set:
    """Return set of package names currently disabled/frozen on device."""
    success, out = cmd_runner.run_adb(["shell", "pm", "list", "packages", "-d"], serial=serial)
    if not success:
        return set()
    result = set()
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            result.add(line[8:].strip())
    return result

def get_installed_packages(serial: str) -> set:
    """Return set of package names currently installed for user 0."""
    success, out = cmd_runner.run_adb(["shell", "pm", "list", "packages"], serial=serial)
    if not success:
        return set()
    result = set()
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            result.add(line[8:].strip())
    return result

def install_apk(serial: str, apk_path: str, reinstall: bool = True, downgrade: bool = False, grant_perms: bool = True) -> Tuple[bool, str]:
    """Install an APK file onto the specified device."""
    args = ["install"]
    if reinstall:
        args.append("-r")
    if downgrade:
        args.append("-d")
    if grant_perms:
        args.append("-g")
    args.append(apk_path)
    return cmd_runner.run_adb(args, serial=serial, timeout=120)

def uninstall_package(serial: str, package_name: str, keep_data: bool = False) -> Tuple[bool, str]:
    """Uninstall a package by package name."""
    args = ["uninstall"]
    if keep_data:
        args.append("-k")
    args.append(package_name)
    return cmd_runner.run_adb(args, serial=serial)

def clear_package_data(serial: str, package_name: str) -> Tuple[bool, str]:
    """Clear app data and caches."""
    return cmd_runner.run_adb(["shell", "pm", "clear", package_name], serial=serial)

def force_stop_package(serial: str, package_name: str) -> Tuple[bool, str]:
    """Force stop a running app process."""
    return cmd_runner.run_adb(["shell", "am", "force-stop", package_name], serial=serial)

def disable_package(serial: str, package_name: str) -> Tuple[bool, str]:
    """Freeze/disable a package."""
    return cmd_runner.run_adb(["shell", "pm", "disable-user", "--user", "0", package_name], serial=serial)

def enable_package(serial: str, package_name: str) -> Tuple[bool, str]:
    """Unfreeze/enable or restore a debloated package (disabled or uninstalled from user 0)."""
    # 1. First, attempt to restore if it was uninstalled from user 0 (works on Android 8+)
    cmd_runner.run_adb(["shell", "cmd", "package", "install-existing", package_name], serial=serial)
    cmd_runner.run_adb(["shell", "pm", "install-existing", package_name], serial=serial)
    
    # 2. Unhide if hidden
    cmd_runner.run_adb(["shell", "pm", "unhide", "--user", "0", package_name], serial=serial)

    # 3. Enable / unfreeze package
    ok, out = cmd_runner.run_adb(["shell", "pm", "enable", package_name], serial=serial)
    if ok and ("enabled" in out.lower() or "new state" in out.lower()):
        return True, out

    # 4. If pm enable didn't output "new state", reset default state and retry enable
    cmd_runner.run_adb(["shell", "pm", "default-state", "--user", "0", package_name], serial=serial)
    ok2, out2 = cmd_runner.run_adb(["shell", "pm", "enable", package_name], serial=serial)
    if ok2 and ("enabled" in out2.lower() or "new state" in out2.lower()):
        return True, out2

    return ok or ok2, out2 or out


def launch_app(serial: str, package_name: str) -> Tuple[bool, str]:
    """Launch application via monkey tool."""
    return cmd_runner.run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"], serial=serial)

def pull_apk(serial: str, remote_apk_path: str, local_save_path: str) -> Tuple[bool, str]:
    """Extract and download base APK from device to PC."""
    return cmd_runner.run_adb(["pull", remote_apk_path, local_save_path], serial=serial, timeout=180)

if __name__ == "__main__":
    print("Testing Package Service...")
    from core.device_service import get_adb_devices
    devs = get_adb_devices()
    if devs:
        s = devs[0]["serial"]
        print(f"Listing 3rd-party packages for {s}...")
        pkgs = list_packages(s, "user")
        print(f"Found {len(pkgs)} packages. Sample: {pkgs[:3]}")
    else:
        print("No device attached to test package service.")
