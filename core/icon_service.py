"""
App Icon Service module.
Generates and caches crisp, beautiful 28x28 app icon pixmaps
for Android packages based on brand, category, and system role.
Supports loading custom PNG icons from data/icons/<package_name>.png if available.
"""

import os
from pathlib import Path
from typing import Dict, Tuple

from PySide6.QtGui import QPixmap, QPainter, QFont, QColor
from PySide6.QtCore import Qt, QRect

ICON_DIR = Path(__file__).resolve().parent.parent / "data" / "icons"


class IconService:
    def __init__(self):
        self._cache: Dict[str, QPixmap] = {}
        if not ICON_DIR.exists():
            ICON_DIR.mkdir(parents=True, exist_ok=True)

    def get_icon(self, package_name: str, app_name: str = "") -> QPixmap:
        """Return a 28x28 QPixmap icon for the given package."""
        if package_name in self._cache:
            return self._cache[package_name]

        # 1. Check if custom icon file exists on disk
        local_png = ICON_DIR / f"{package_name}.png"
        if local_png.exists():
            try:
                pm = QPixmap(str(local_png))
                if not pm.isNull():
                    scaled = pm.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self._cache[package_name] = scaled
                    return scaled
            except Exception:
                pass

        # 2. Generate vector glyph icon badge
        pixmap = self._generate_icon_badge(package_name, app_name)
        self._cache[package_name] = pixmap
        return pixmap

    def _generate_icon_badge(self, pkg: str, name: str) -> QPixmap:
        p = pkg.lower()
        n = name.lower()

        # Determine icon symbol and theme colors: (glyph, bg_color, border_color)
        glyph, bg_hex, border_hex = self._match_icon(p, n)

        size = 28
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Draw rounded squircle background
        painter.setBrush(QColor(bg_hex))
        painter.setPen(QColor(border_hex))
        painter.drawRoundedRect(0, 0, size - 1, size - 1, 6, 6)

        # Draw centered glyph
        f = QFont("Segoe UI Emoji", 11)
        painter.setFont(f)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, glyph)

        painter.end()
        return pixmap

    def _match_icon(self, p: str, n: str) -> Tuple[str, str, str]:
        # Downloads & storage
        if "download" in p or "download" in n:
            return "📥", "#eff6ff", "#93c5fd"
        if "bookmark" in p or "bookmark" in n:
            return "🔖", "#fffbeb", "#fcd34d"
        if "catchlog" in p or "logcat" in p or "log" in p:
            return "📋", "#f1f5f9", "#cbd5e1"
        if "wellbeing" in p or "wellbeing" in n:
            return "🧘", "#f0fdfa", "#99f6e4"
        if "feedback" in p or "feedback" in n:
            return "💬", "#eff6ff", "#bfdbfe"
        if "chrome" in p or "browser" in p or "jelly" in p or "browser" in n:
            return "🌐", "#ecfeff", "#a5f3fc"
        if "youtube" in p or "youtube" in n:
            return "▶️", "#fef2f2", "#fca5a5"
        if "gmail" in p or "mail" in p or "email" in n:
            return "✉️", "#fef2f2", "#fca5a5"
        if "maps" in p or "location" in p or "gps" in p:
            return "📍", "#f0fdf4", "#86efac"
        if "photo" in p or "gallery" in p or "gallery" in n:
            return "🖼️", "#faf5ff", "#d8b4fe"
        if "camera" in p or "camera" in n:
            return "📷", "#f0f9ff", "#bae6fd"
        if "music" in p or "audio" in p or "spotify" in p or "music" in n:
            return "🎵", "#f0fdf4", "#86efac"
        if "settings" in p or "config" in p or "settings" in n:
            return "⚙️", "#f8fafc", "#cbd5e1"
        if "vending" in p or "store" in p or "playstore" in n:
            return "🛍️", "#eff6ff", "#93c5fd"
        if "dialer" in p or "phone" in p or "telecom" in p or "telephony" in p:
            return "📞", "#f0fdf4", "#86efac"
        if "mms" in p or "message" in p or "sms" in p or "pesan" in n:
            return "💬", "#f0f9ff", "#7dd3fc"
        if "contact" in p or "kontak" in n:
            return "👤", "#eff6ff", "#93c5fd"
        if "clock" in p or "alarm" in p or "jam" in n:
            return "⏰", "#fffbeb", "#fcd34d"
        if "calculator" in p or "kalkulator" in n:
            return "🧮", "#eef2ff", "#c7d2fe"
        if "calendar" in p or "kalender" in n:
            return "📅", "#eff6ff", "#93c5fd"
        if "document" in p or "file" in p or "berkas" in n:
            return "📁", "#fefce8", "#fef08a"
        if "bluetooth" in p:
            return "ᛒ", "#eff6ff", "#93c5fd"
        if "wifi" in p or "network" in p:
            return "📶", "#ecfeff", "#a5f3fc"
        if "security" in p or "protect" in p or "guard" in p:
            return "🛡️", "#f0fdf4", "#86efac"
        if "battery" in p or "power" in p:
            return "🔋", "#f0fdf4", "#86efac"
        if "keyboard" in p or "inputmethod" in p or "ime" in p:
            return "⌨️", "#f1f5f9", "#cbd5e1"
        if "packageinstaller" in p or "installer" in p:
            return "📦", "#fffbeb", "#fcd34d"

        # Social & Bloatware
        if "facebook" in p or "katana" in p or "orca" in p:
            return "📘", "#eff6ff", "#93c5fd"
        if "instagram" in p:
            return "📷", "#fdf2f8", "#fbcfe8"
        if "whatsapp" in p:
            return "💬", "#f0fdf4", "#86efac"
        if "netflix" in p:
            return "🎬", "#fef2f2", "#fca5a5"
        if "tiktok" in p or "musically" in p:
            return "🎵", "#f1f5f9", "#334155"

        # OEM Brands
        if "samsung" in p or "sec" in p:
            return "🌌", "#eff6ff", "#93c5fd"
        if "miui" in p or "xiaomi" in p:
            return "🟠", "#fff7ed", "#fdba74"
        if "coloros" in p or "oppo" in p or "realme" in p:
            return "🟢", "#ecfdf5", "#a7f3d0"
        if "vivo" in p or "bbk" in p:
            return "🔵", "#eff6ff", "#93c5fd"
        if "huawei" in p:
            return "🔴", "#fef2f2", "#fca5a5"
        if "qualcomm" in p or "qti" in p or "bsp" in p or "mediatek" in p:
            return "⚡", "#fffbeb", "#fcd34d"

        # Google Services
        if "com.google." in p:
            return "🔹", "#eff6ff", "#93c5fd"

        # Default Android Robot
        return "🤖", "#f0fdf4", "#86efac"


# Global singleton instance
icon_service = IconService()
