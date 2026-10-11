"""
Debloater Service module.
Handles integration with the Universal Android Debloater (UAD) database,
providing safety recommendations, app descriptions, and removal risk assessments.
"""

import sys
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

if getattr(sys, 'frozen', False):
    ROOT_DIR = getattr(sys, '_MEIPASS', str(Path(sys.executable).parent))
else:
    ROOT_DIR = str(Path(__file__).resolve().parent.parent)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DATA_FILE = Path(ROOT_DIR) / "data" / "uad_lists.json"
# Fallback check next to executable
if not DATA_FILE.exists() and getattr(sys, 'frozen', False):
    DATA_FILE = Path(sys.executable).parent / "data" / "uad_lists.json"
UAD_URL = "https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json"

CUSTOM_ENTRIES = {
    "org.lineageos.jelly": {
        "list": "Oem",
        "description": "LineageOS Browser App, based on chromium.\nSafe to remove if you don't need it or have replaced it with another app.\nOtherwise there will be no browser app on your device.",
        "dependencies": [],
        "neededBy": [],
        "labels": [],
        "removal": "Recommended"
    },
    "com.cyanogenmod.filemanager": {
        "list": "Oem",
        "description": "Cyanogenmod file manager, safe to remove if you use another one.",
        "dependencies": [],
        "neededBy": [],
        "labels": [],
        "removal": "Advanced"
    }
}

class DebloaterService:
    def __init__(self):
        self.db: Dict[str, Any] = {}
        self.load_database()

    def load_database(self):
        """Load UAD debloat database from local cache."""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.db = json.load(f)
            except Exception as e:
                print(f"[Debloater] Error reading local database: {e}")
                self.db = {}

        # Merge custom additions
        self.db.update(CUSTOM_ENTRIES)

    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve debloat info for a package."""
        return self.db.get(package_name)

    def get_safety_rating(self, package_name: str) -> Dict[str, str]:
        """
        Evaluate safety for removing/disabling a package.
        Returns dictionary with:
        - level: 'Recommended', 'Advanced', 'Expert', 'Unsafe', 'Unknown'
        - label: Human readable Indonesian label
        - color: Hex color for UI badge
        - description: Explanation of package
        - is_critical: True if removing may cause serious instability or bootloop
        """
        info = self.get_package_info(package_name)
        if not info:
            return {
                "level": "Unknown",
                "label": "⚪ Tidak Diketahui",
                "color": "#64748b",
                "description": "Aplikasi ini tidak terdaftar dalam database UAD. Harap berhati-hati jika ingin menghapus.",
                "is_critical": False
            }

        removal = info.get("removal", "Unknown")
        desc = info.get("description", "Tidak ada deskripsi.")

        if removal == "Recommended":
            return {
                "level": "Recommended",
                "label": "🟢 Rekomendasi (Aman)",
                "color": "#15803d",
                "description": desc,
                "is_critical": False
            }
        elif removal == "Advanced":
            return {
                "level": "Advanced",
                "label": "🟡 Bahaya (Perlu Pengganti)",
                "color": "#b45309",
                "description": f"{desc}\n\n⚠️ Peringatan: Pastikan Anda sudah menginstal aplikasi pengganti sebelum menghapus!",
                "is_critical": False
            }
        elif removal == "Expert":
            return {
                "level": "Expert",
                "label": "🟠 Bahaya (Berisiko Lanjutan)",
                "color": "#c2410c",
                "description": f"{desc}\n\n⚠️ Peringatan: Menghapus aplikasi ini dapat merusak sebagian fungsi perangkat!",
                "is_critical": True
            }
        elif removal == "Unsafe":
            return {
                "level": "Unsafe",
                "label": "🔴 Kritis (Risiko Bootloop)",
                "color": "#dc2626",
                "description": f"{desc}\n\n🚨 KRITIS: Aplikasi sistem penting! Menghapus aplikasi ini dapat menyebabkan HP bootloop atau mati total!",
                "is_critical": True
            }

        else:
            return {
                "level": "Unknown",
                "label": "⚪ Tidak Diketahui",
                "color": "#64748b",
                "description": desc,
                "is_critical": False
            }

    def update_database_online(self) -> Tuple[bool, str]:
        """Download latest UAD database from GitHub and save to local data/."""
        try:
            req = urllib.request.Request(UAD_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            data.update(CUSTOM_ENTRIES)
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.db = data
            return True, f"Berhasil memperbarui database! Total {len(self.db)} paket aplikasi."
        except Exception as e:
            return False, f"Gagal memperbarui database: {str(e)}"

# Global singleton
debloater_service = DebloaterService()

if __name__ == "__main__":
    print("Testing Debloater Service...")
    print(f"Total database entries: {len(debloater_service.db)}")

    test_pkgs = ["org.lineageos.jelly", "com.cyanogenmod.filemanager", "com.google.android.youtube", "com.android.systemui"]
    for pkg in test_pkgs:
        rating = debloater_service.get_safety_rating(pkg)
        print(f"[{pkg}] -> {rating['label']} | Critical: {rating['is_critical']}")
