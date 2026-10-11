import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QMessageBox, QFileDialog, QProgressBar,
    QMenu, QButtonGroup, QRadioButton, QAbstractItemView,
    QDialog, QListWidget, QListWidgetItem, QGroupBox, QTextEdit,
    QTabWidget, QFrame, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle, QApplication, QLayout, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QRect, QEvent, QSize, QPoint
from PySide6.QtGui import QColor, QFont, QPainter
from core.adb_manager import adb_manager
from core.settings import settings
from core.debloater_service import debloater_service
from core.icon_service import icon_service
from core.package_service import get_packages_install_times
from ui.dialogs.app_audit_dialog import AppAuditDialog
from ui.dialogs.confirm_dialog import confirm_two_step
from ui.style import styled_btn

KNOWN_APP_NAMES = {
    "com.mobile.legends": "Mobile Legends: Bang Bang",
    "com.ondi.fortias.defense": "Fortias Saga: Action Defense",
    "com.dts.freefireth": "Free Fire",
    "com.dts.freefiremax": "Free Fire MAX",
    "com.tencent.ig": "PUBG MOBILE",
    "com.pubg.krmobile": "PUBG MOBILE (KR)",
    "com.vng.pubgmobile": "PUBG MOBILE (VN)",
    "com.garena.game.codm": "Call of Duty: Mobile",
    "com.activision.callofduty.shooter": "Call of Duty: Mobile",
    "com.miHoYo.GenshinImpact": "Genshin Impact",
    "com.HoYoverse.hkrpgoversea": "Honkai: Star Rail",
    "com.HoYoverse.Nap": "Zenless Zone Zero",
    "com.stove.epic7.google": "Epic Seven",
    "com.bilibili.trickcal": "Trickcal Revive",
    "com.kurogame.wutheringwaves.global": "Wuthering Waves",
    "com.roblox.client": "Roblox",
    "com.mojang.minecraftpe": "Minecraft",
    "com.ea.gp.fifamobile": "EA SPORTS FC Mobile",
    "com.konami.pesam": "eFootball",
    "com.supercell.clashofclans": "Clash of Clans",
    "com.supercell.clashroyale": "Clash Royale",
    "com.supercell.brawlstars": "Brawl Stars",
    "com.riotgames.league.wildrift": "League of Legends: Wild Rift",
    "com.levelinfinite.hotta.gp": "Tower of Fantasy",
    "com.netmarble.sololv": "Solo Leveling: ARISE",
    "com.facebook.katana": "Facebook",
    "com.facebook.orca": "Messenger",
    "com.facebook.lite": "Facebook Lite",
    "com.instagram.android": "Instagram",
    "com.whatsapp": "WhatsApp",
    "com.whatsapp.w4b": "WhatsApp Business",
    "org.telegram.messenger": "Telegram",
    "com.twitter.android": "X (Twitter)",
    "com.ss.android.ugc.trill": "TikTok",
    "com.zhiliaoapp.musically": "TikTok",
    "com.snapchat.android": "Snapchat",
    "com.discord": "Discord",
    "com.spotify.music": "Spotify",
    "com.netflix.mediaclient": "Netflix",
    "com.google.android.youtube": "YouTube",
    "app.revanced.android.youtube": "YouTube ReVanced",
    "com.google.android.apps.youtube.music": "YouTube Music",
    "com.android.chrome": "Google Chrome",
    "org.mozilla.firefox": "Firefox",
    "com.microsoft.emmx": "Microsoft Edge",
    "com.opera.browser": "Opera Browser",
    "com.shopee.id": "Shopee",
    "com.tokopedia.tkpd": "Tokopedia",
    "com.lazada.android": "Lazada",
    "com.bukalapak.android": "Bukalapak",
    "com.blibli.mobile": "Blibli",
    "com.gojek.app": "Gojek",
    "com.grabtaxi.passenger": "Grab",
    "com.maxim.taxi": "Maxim",
    "id.dana": "DANA",
    "com.telkom.indihome.external": "MyIndiHome",
    "com.byu.id": "by.U",
    "com.dafturn.mypertamina": "MyPertamina",
    "id.go.bpn.sentuh": "Sentuh Tanahku",
    "com.bca": "BCA Mobile",
    "my.bca": "myBCA",
    "id.co.bri.brimo": "BRImo",
    "id.co.bankmandiri.livin": "Livin' by Mandiri",
    "com.bankbii.mobile.android": "M2U ID",
    "com.btpn.dc": "Jenius",
    "com.seabank.mobile": "SeaBank",
    "com.neobank.bcnc": "Neobank",
    "com.dv.adm": "Advanced Download Manager (ADM)",
    "com.qooapp.qoohelper": "QooApp",
    "io.github.samolego.canta": "Canta (Debloater)",
    "gr.nikolasspyr.integritycheck": "Play Integrity API Checker",
    "tech.httptoolkit.android.v1": "HTTP Toolkit",
    "com.wandapps.multilayerphoto": "Multi Layer Photo",
    "cyou.joiplay.joiplay": "JoiPlay",
    "cyou.joiplay.runtime.rpgmaker": "JoiPlay RPG Maker",
    "cyou.joiplay.runtime.renpy": "JoiPlay Ren'Py",
    "com.google.android.safetycore": "Google Safety Core",
    "com.google.android.contactkeys": "Google Contact Keys",
    "com.google.android.verifier": "Google Play Protect Verifier",
    "com.google.android.gms": "Google Play Services",
    "com.android.vending": "Google Play Store",
    "com.google.android.googlequicksearchbox": "Google Search",
    "com.google.android.apps.maps": "Google Maps",
    "com.google.android.apps.photos": "Google Photos",
    "com.google.android.apps.docs": "Google Drive",
    "com.google.android.gm": "Gmail",
    "com.google.android.calendar": "Google Calendar",
    "com.google.android.contacts": "Google Contacts",
    "com.google.android.deskclock": "Google Clock",
    "com.google.android.calculator": "Google Calculator",
    "com.google.android.dialer": "Google Phone",
    "com.google.android.apps.messaging": "Google Messages",
    "com.google.android.keep": "Google Keep Notes",
    "com.google.android.apps.translate": "Google Translate",
    "docsreader.officeword.documentreader.offlineviewer.free": "All Document Reader & Viewer",
    "com.just4funtools.fakegpslocationprofessional": "Fake GPS Location Professional",
    "com.kblack.demo_play_integrity_api": "Demo Play Integrity API",
    "ru.zdevs.zarchiver": "ZArchiver",
    "ru.zdevs.zarchiver.pro": "ZArchiver Pro",
    "com.mxtech.videoplayer.ad": "MX Player",
    "com.mxtech.videoplayer.pro": "MX Player Pro",
    "com.lonelycatgames.Xplore": "X-plore File Manager",
    "com.limelight.noir": "Moonlight Game Streaming",
    "eu.faircode.xlua": "XPrivacyLua",
    "app.revanced.android.gms": "MicroG Services (ReVanced)",
    "com.mgoogle.android.gms": "MicroG Services",
    "com.linkit.bimatri": "bima+ (Tri)",
    "com.brave.browser": "Brave Browser",
    "com.storymatrix.drama": "ShortMax Drama",
    "com.worldance.drama": "DramaBox",
    "com.microsoft.rdc.androidx": "Microsoft Remote Desktop",
    "jp.MarvelousAQL.logres": "Logres of Swords and Sorcery",
    "com.tsng.hidemyapplist": "Hide My Applist",
    "com.freereels.app": "FreeReels Drama",
    "id.masook.personal.kotabaru": "Masook Personal Kotabaru",
    "com.ironhidegames.android.kingdomrush.alliance": "Kingdom Rush 5: Alliance",
    "io.github.auag0.hidemocklocation": "Hide Mock Location",
    "io.github.auag0.mocklocationdetector": "Mock Location Detector",
    "io.github.a13e300.ksuwebui": "KernelSU WebUI",
    "com.redfinger.global": "Redfinger Cloud Phone",
    "com.bstar.intl": "Bstation (Bilibili)",
    "com.google.ar.core": "Google Play Services for AR",
    "com.duokan.phone.remotecontroller": "Mi Remote Controller",
    "com.gear2.growslayer": "Grow Slayer",
    "us.zoom.videomeetings": "Zoom Workplace",
    "com.stardesk": "StarDesk",
    "com.amazon.appmanager": "Amazon Appstore",
    "com.android.soundrecorder": "Sound Recorder",
    "com.preff.kb.xm": "Preff Keyboard",
    "com.miui.mediaeditor": "Mi Gallery Editor",
    "com.xiaomi.scanner": "Mi Scanner",
    "com.miui.calculator": "Mi Calculator",
    "com.miui.notes": "Mi Notes",
    "com.miui.gallery": "Mi Gallery",
    "com.miui.cleanmaster": "Mi Cleaner",
    "com.miui.securityadd": "Mi Security Add-on",
    "com.miui.compass": "Mi Compass",
    "com.miui.screenrecorder": "Mi Screen Recorder",
    "com.miui.weather2": "Mi Weather",
    "com.google.android.feedback": "Google Feedback",
    "com.google.android.printservice.recommendation": "Print Service Recommendation",
    "com.android.providers.downloads": "Download Manager",
    "com.android.providers.media": "Media Storage",
    "com.android.providers.contacts": "Contacts Storage",
    "com.android.providers.telephony": "Telephony Storage",
    "com.android.providers.calendar": "Calendar Storage",
}

COMMON_WORDS = [
    "professional", "location", "fake", "gps", "multi", "layer", "photo",
    "screen", "recorder", "wallpaper", "battery", "manager", "reader", "player",
    "music", "video", "editor", "cleaner", "booster", "speed", "test", "checker",
    "integrity", "defense", "saga", "war", "clash", "hero", "heroes", "auto",
    "clicker", "file", "explorer", "security", "camera", "scanner", "notes",
    "tools", "launcher", "pertamina", "runtime", "maker", "helper", "touch",
    "browser", "keyboard", "clock", "calculator", "gallery", "market", "store",
    "docs", "office", "word", "document", "offline", "viewer", "remote",
    "controller", "streaming", "drama", "short", "cloud", "phone", "audio",
    "sound", "service", "services", "setting", "settings"
]

def split_compound_word(token: str) -> str:
    lower = token.lower()
    pos = 0
    words = []
    while pos < len(lower):
        matched = False
        for w in sorted(COMMON_WORDS, key=len, reverse=True):
            if lower[pos:].startswith(w):
                words.append(w.upper() if w in ["gps", "api", "adm", "bca", "bri", "apk", "ui"] else w.title())
                pos += len(w)
                matched = True
                break
        if not matched:
            rest = lower[pos:]
            words.append(rest.title())
            break
    if len(words) > 1:
        return " ".join(words)
    return token

def extract_app_name(pkg_name: str, desc: str = "") -> str:
    """Extract clean, accurate human-readable app title from catalog, UAD description, or smart semantic parsing."""
    # 1. Exact catalog match
    if pkg_name in KNOWN_APP_NAMES:
        return KNOWN_APP_NAMES[pkg_name]

    # Quick alias lookup
    known_aliases = {
        "partnerbookmarks": "Partner Bookmarks",
        "quicksearchbox": "Google Search",
        "globalminusscreen": "App Vault (Minus Screen)",
        "googlequicksearchbox": "Google Search",
        "freeform": "Floating Windows",
        "miwallpaper": "Mi Wallpaper",
        "catchlog": "BSP Catchlog",
        "talkback": "TalkBack",
    }
    last_token = pkg_name.split(".")[-1].lower()
    if last_token in known_aliases:
        return known_aliases[last_token]

    # 2. Check UAD description if concise title
    if desc:
        first_line = desc.strip().splitlines()[0].strip()
        clean = re.sub(r'\s*\([^)]*https?://[^)]*\)', '', first_line).strip()
        if ', ' in clean and len(clean.split(', ')[0]) <= 30:
            candidate = clean.split(', ')[0].strip()
            if not any(w in candidate.lower() for w in ['when', 'if', 'because', 'although']):
                clean = candidate
        clean = clean.rstrip('.:')
        is_sentence = any(clean.lower().startswith(p) for p in [
            'this is', 'it is', 'used to', 'provides', 'allows', 'lets you', 'an app that', 'a tool to'
        ]) or ' = ' in clean or clean.endswith('?') or len(clean.split()) > 6 or len(clean) > 35
        if clean and not is_sentence:
            if clean.startswith("Default ") and len(clean) > 10:
                clean = clean[8:]
            return clean

    # 3. Smart Semantic Token Parser
    parts = pkg_name.split('.')
    generic_domains = {'com', 'org', 'net', 'io', 'id', 'jp', 'kr', 'cn', 'vn', 'de', 'fr', 'app', 'tech', 'dev', 'cyou', 'co', 'in', 'gr', 'gov', 'ru', 'us', 'sc'}
    generic_orgs = {
        'google', 'android', 'facebook', 'microsoft', 'bilibili', 'stove', 'wandapps', 'ondi', 'dts',
        'tencent', 'xiaomi', 'samsung', 'huawei', 'oppo', 'vivo', 'transsion', 'evezzon', 'nikolasspyr',
        'just4funtools', 'lonelycatgames', 'mxtech', 'kblack', 'faircode', 'revanced', 'linkit', 'storymatrix',
        'worldance', 'redfinger', 'marvelousaql', 'ironhidegames', 'zdevs'
    }

    meaningful = []
    for idx, p in enumerate(parts):
        low = p.lower()
        if idx == 0 and low in generic_domains:
            continue
        if idx == 1 and low in generic_domains:
            continue
        if low in ['v1', 'v2', 'v3', 'api', 'beta', 'release', 'bin', 'main']:
            continue
        meaningful.append(p)

    if not meaningful:
        meaningful = parts[-2:] if len(parts) >= 2 else parts

    # Filter out generic company/developer if there are other meaningful tokens
    if len(meaningful) >= 2 and (
        meaningful[0].lower() in generic_orgs or
        any(meaningful[0].lower().endswith(s) for s in ['tools', 'games', 'game', 'studios', 'studio', 'apps', 'labs', 'team', 'devs'])
    ):
        meaningful = meaningful[1:]

    # Split camelCase / compound words for each token
    formatted_tokens = []
    for token in meaningful:
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1 \2', token)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s1)
        sub = s2.replace('_', ' ').replace('-', ' ')
        if ' ' not in sub and len(sub) > 4:
            sub = split_compound_word(sub)
        formatted_tokens.append(sub.title())

    result = " ".join(formatted_tokens)
    # Acronyms formatting
    for acr in ['Gps', 'Api', 'Adm', 'Bca', 'Bri', 'Apk', 'Http', 'Ui', 'Uad', 'Otp', 'Sms', 'Rpg']:
        result = re.sub(rf'\b{acr}\b', acr.upper(), result)
    return result

class AppPackageDelegate(QStyledItemDelegate):
    """Custom delegate to render App Icon (28x28) + 2 lines: App Title (Bold) + Package Name (Muted)."""
    def sizeHint(self, option: QStyleOptionViewItem, index):
        return QSize(option.rect.width() if option.rect.isValid() else 200, 44)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        widget = option.widget
        style = widget.style() if widget else QApplication.style()

        # 1. Base control draws background & checkbox indicator with theme stylesheet
        opt.text = ''
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)

        # 2. Checkbox indicator boundary (only offset when item actually has a checkbox)
        check_rect = style.subElementRect(QStyle.SE_ItemViewItemCheckIndicator, opt, widget)
        has_checkbox = (index.data(Qt.CheckStateRole) is not None)
        if has_checkbox and check_rect.isValid() and check_rect.width() > 0:
            cb_right = check_rect.right() + 6
        else:
            cb_right = option.rect.left() + 4

        # 3. Draw App Icon (28x28)
        icon_x = cb_right + 4
        icon_y = option.rect.top() + (option.rect.height() - 28) // 2

        full_text = index.data(Qt.DisplayRole) or ''
        parts = full_text.split('\n', 1)
        app_name = parts[0]
        pkg_name = parts[1] if len(parts) > 1 else ''

        pixmap = icon_service.get_icon(pkg_name, app_name)
        if not pixmap.isNull():
            painter.drawPixmap(icon_x, icon_y, pixmap)
            left_margin = icon_x + 28 + 8
        else:
            left_margin = icon_x

        avail_width = option.rect.right() - left_margin - 6
        is_selected = bool(option.state & QStyle.State_Selected)

        painter.save()
        # Line 1: App Name (Bold, 10pt)
        font_title = QFont(option.font)
        font_title.setPointSize(10)
        font_title.setBold(True)
        painter.setFont(font_title)
        painter.setPen(QColor('#1d4ed8' if is_selected else '#0f172a'))
        title_rect = QRect(left_margin, option.rect.top() + 4, avail_width, 18)
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, app_name)

        # Line 2: Package Name (Regular, 9pt, muted)
        font_pkg = QFont(option.font)
        font_pkg.setPointSize(9)
        font_pkg.setBold(False)
        painter.setFont(font_pkg)
        painter.setPen(QColor('#2563eb' if is_selected else '#64748b'))
        pkg_rect = QRect(left_margin, option.rect.top() + 22, avail_width, 17)
        painter.drawText(pkg_rect, Qt.AlignLeft | Qt.AlignVCenter, pkg_name)
        painter.restore()


class StatusRatingDelegate(QStyledItemDelegate):
    """Custom delegate to render 2 distinct lines: App Status (Line 1) and UAD Safety Rating (Line 2)."""
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        widget = option.widget
        style = widget.style() if widget else QApplication.style()

        # Draw base selection/hover background
        opt.text = ''
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)

        full_text = index.data(Qt.DisplayRole) or ''
        parts = full_text.split('\n', 1)
        line1 = parts[0]
        line2 = parts[1] if len(parts) > 1 else ''

        state_color = index.data(Qt.UserRole + 1) or '#64748b'
        rating_color = index.data(Qt.UserRole + 2) or '#64748b'
        is_selected = bool(option.state & QStyle.State_Selected)

        painter.save()
        # Line 1: Status (e.g. 🗑️ Terhapus (User 0) / ❄️ Dibekukan / ✅ Aktif)
        f1 = QFont(option.font)
        f1.setPointSize(9)
        f1.setBold(True)
        painter.setFont(f1)
        painter.setPen(QColor('#1d4ed8' if is_selected else state_color))
        r1 = QRect(option.rect.left() + 6, option.rect.top() + 4, option.rect.width() - 12, 17)
        painter.drawText(r1, Qt.AlignLeft | Qt.AlignVCenter, line1)

        # Line 2: Rating (e.g. 🟡 Bahaya (Perlu Pengganti) / 🟢 Rekomendasi / 🔴 Kritis)
        f2 = QFont(option.font)
        f2.setPointSize(9)
        f2.setBold(True)
        painter.setFont(f2)
        painter.setPen(QColor('#2563eb' if is_selected else rating_color))
        r2 = QRect(option.rect.left() + 6, option.rect.top() + 21, option.rect.width() - 12, 16)
        painter.drawText(r2, Qt.AlignLeft | Qt.AlignVCenter, line2)
        painter.restore()


class FlowLayout(QLayout):
    """Responsive wrapping layout that flows widgets to the next line on window resize."""
    def __init__(self, parent=None, margin=0, spacing=8):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = self.spacing()

        for item in self.itemList:
            wid = item.widget()
            spaceX = spacing
            spaceY = spacing
            hint = item.sizeHint()
            nextX = x + hint.width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + hint.width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x = nextX
            lineHeight = max(lineHeight, hint.height())

        return y + lineHeight - rect.y()

class PackageLoadWorker(QThread):
    finished = Signal(list)

    def __init__(self, serial: str, filter_type: str = "all"):
        super().__init__()
        self.serial = serial
        self.filter_type = filter_type

    def run(self):
        if not self.serial:
            self.finished.emit([])
            return

        if self.filter_type == "debloat_all":
            # 1. Fetch system packages (including bloatware previously uninstalled from user 0)
            pkgs = adb_manager.list_packages(self.serial, "system_uninstalled")
            if not pkgs:
                pkgs = adb_manager.list_packages(self.serial, "system")

            # 2. Strict Safeguard: Exclude ANY 3rd-party user installed application (-3)
            # This ensures WhatsApp, Facebook, games, etc. installed by user NEVER appear in debloater!
            user_3rd_party = set(p["name"] for p in adb_manager.list_packages(self.serial, "user"))
            pkgs = [p for p in pkgs if p["name"] not in user_3rd_party]

            # 3. Path Safeguard: Ensure APK path belongs to system partitions
            system_prefixes = ("/system", "/system_ext", "/product", "/vendor", "/apex", "/oem", "/odm")
            pkgs = [p for p in pkgs if not p.get("path") or p["path"].startswith(system_prefixes)]

            disabled_set = adb_manager.get_disabled_packages(self.serial)
            installed_set = adb_manager.get_installed_packages(self.serial)

            for p in pkgs:
                name = p["name"]
                if name in disabled_set:
                    p["state"] = "disabled"
                elif name not in installed_set:
                    p["state"] = "uninstalled"
                else:
                    p["state"] = "enabled"
                rating = debloater_service.get_safety_rating(name)
                p["rating"] = rating
                p["app_name"] = extract_app_name(name, rating.get("description", ""))

            self.finished.emit(pkgs)
            return

        pkgs = adb_manager.list_packages(self.serial, self.filter_type)
        for p in pkgs:
            p["state"] = "enabled"
            rating = debloater_service.get_safety_rating(p["name"])
            p["rating"] = rating
            p["app_name"] = extract_app_name(p["name"], rating.get("description", ""))
        self.finished.emit(pkgs)

class InstallTimesWorker(QThread):
    finished = Signal(dict)

    def __init__(self, serial: str):
        super().__init__()
        self.serial = serial

    def run(self):
        if not self.serial:
            self.finished.emit({})
            return
        times = get_packages_install_times(self.serial)
        self.finished.emit(times)

class InstallWorker(QThread):
    status_updated = Signal(str)
    log_added = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, serial: str, apk_paths: list, reinstall: bool, downgrade: bool, grant_perms: bool):
        super().__init__()
        self.serial = serial
        self.apk_paths = apk_paths
        self.reinstall = reinstall
        self.downgrade = downgrade
        self.grant_perms = grant_perms

    def run(self):
        total = len(self.apk_paths)
        for i, path in enumerate(self.apk_paths, 1):
            filename = os.path.basename(path)
            self.status_updated.emit(f"Memasang ({i}/{total}): {filename}...")
            self.log_added.emit(f"⏳ [{i}/{total}] Memasang {filename}...")

            ok, out = adb_manager.install_apk(
                self.serial, path,
                reinstall=self.reinstall,
                downgrade=self.downgrade,
                grant_perms=self.grant_perms
            )

            if ok and "Success" in out:
                self.log_added.emit(f"✅ [{i}/{total}] SUKSES: {filename} berhasil dipasang!\n")
            else:
                self.log_added.emit(f"❌ [{i}/{total}] GAGAL: {filename}\nDetail:\n{out}\n")
                self.finished.emit(False, f"Gagal memasang {filename}:\n{out}")
                return

        self.finished.emit(True, f"Semua {total} paket APK berhasil dipasang!")

class BatchDebloatWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(int, int)

    def __init__(self, serial: str, packages: list, action: str = "disable"):
        super().__init__()
        self.serial = serial
        self.packages = packages
        self.action = action

    def run(self):
        success_count = 0
        fail_count = 0
        total = len(self.packages)

        for i, pkg in enumerate(self.packages, 1):
            self.progress.emit(int((i / total) * 100), f"Memproses {pkg} ({i}/{total})...")
            if self.action == "disable":
                ok, _ = adb_manager.disable_package(self.serial, pkg)
            elif self.action == "enable":
                ok, _ = adb_manager.enable_package(self.serial, pkg)
            else:
                ok, _ = adb_manager.uninstall_package(self.serial, pkg)

            if ok:
                success_count += 1
            else:
                fail_count += 1

        self.finished.emit(success_count, fail_count)

class AppManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_serial = ""
        self.app_packages = []
        self._install_times = {}
        self.all_debloat_packages = []
        self.filtered_debloat_packages = []
        self.selected_apk_paths = []
        self._active_workers = set()
        self.apps_worker = None
        self.install_times_worker = None
        self.deb_worker = None
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Tab Widget separating the 3 distinct functional areas
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setObjectName("appManagerSubTabs")

        # 1. Sub-Tab: Kelola Aplikasi (Installed Apps)
        tab_apps = QWidget()
        self.setup_apps_tab(tab_apps)
        self.sub_tabs.addTab(tab_apps, "📦  Kelola Aplikasi")

        # 2. Sub-Tab: Smart Debloater (UAD)
        tab_debloat = QWidget()
        self.setup_debloat_tab(tab_debloat)
        self.sub_tabs.addTab(tab_debloat, "🛡️  Smart Debloater (UAD)")

        # 3. Sub-Tab: Pasang APK (Install APK)
        tab_install = QWidget()
        self.setup_install_tab(tab_install)
        self.sub_tabs.addTab(tab_install, "📥  Pasang APK")

        main_layout.addWidget(self.sub_tabs)

    # -------------------------------------------------------------
    # 1. SETUP SUB-TAB: KELOLA APLIKASI
    # -------------------------------------------------------------
    def setup_apps_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Row 1: Filter Categories + Sort Dropdown
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        self.grp_app_filter = QButtonGroup(self)
        self.rb_app_user = QRadioButton("Aplikasi Pengguna (3rd-party)")
        self.rb_app_user.setChecked(True)
        self.rb_app_all = QRadioButton("Semua")
        self.rb_app_sys = QRadioButton("Sistem")
        self.rb_app_dis = QRadioButton("Dinonaktifkan")

        for idx, rb in enumerate([self.rb_app_user, self.rb_app_all, self.rb_app_sys, self.rb_app_dis]):
            self.grp_app_filter.addButton(rb, idx)
            filter_bar.addWidget(rb)
            rb.toggled.connect(lambda checked: self.on_app_filter_changed() if checked else None)

        filter_bar.addStretch()

        lbl_sort = QLabel("Urutkan:")
        lbl_sort.setStyleSheet("font-size: 11px; font-weight: 600; color: #475569;")
        filter_bar.addWidget(lbl_sort)

        self.cmb_app_sort = QComboBox()
        self.cmb_app_sort.addItems([
            "🔤 Nama Aplikasi (A → Z)",
            "🔤 Nama Aplikasi (Z → A)",
            "🕒 Tanggal Pasang (Terbaru)",
            "🕒 Tanggal Pasang (Terlama)",
            "📦 Nama Package (A → Z)",
            "📦 Nama Package (Z → A)",
            "⚖️ Tipe (Pengguna dulu)"
        ])
        self.cmb_app_sort.setToolTip("Pilih metode pengurutan daftar aplikasi")
        self.cmb_app_sort.currentIndexChanged.connect(self.on_sort_changed)
        filter_bar.addWidget(self.cmb_app_sort)

        layout.addLayout(filter_bar)

        # Row 2: Search input + Refresh + Detail Audit button
        search_bar = QHBoxLayout()
        search_bar.setSpacing(6)

        self.txt_app_search = QLineEdit()
        self.txt_app_search.setPlaceholderText("🔍 Cari nama aplikasi atau package...")
        self.txt_app_search.textChanged.connect(self.filter_apps_table)
        search_bar.addWidget(self.txt_app_search, 1)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setToolTip("Muat ulang daftar aplikasi dari HP")
        btn_refresh.clicked.connect(self.refresh_apps)
        search_bar.addWidget(btn_refresh)

        btn_audit = styled_btn("🔍 Detail", "primary")
        btn_audit.setToolTip("Buka Detail & Audit Aplikasi lengkap (Deteksi Iklan, Pelacak, dan Izin)")
        btn_audit.clicked.connect(self.open_app_audit)
        search_bar.addWidget(btn_audit)

        layout.addLayout(search_bar)

        # Progress bar
        self.apps_progress = QProgressBar()
        self.apps_progress.setRange(0, 0)
        self.apps_progress.setFixedHeight(3)
        self.apps_progress.setVisible(False)
        layout.addWidget(self.apps_progress)

        # Table of installed apps
        self.table_apps = QTableWidget()
        self.table_apps.setColumnCount(4)
        self.table_apps.setHorizontalHeaderLabels(["Nama Aplikasi & Package", "Tipe", "Tanggal Pasang", "Path APK"])
        self.table_apps.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table_apps.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_apps.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_apps.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_apps.setColumnWidth(0, 420)
        self.table_apps.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_apps.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_apps.setItemDelegateForColumn(0, AppPackageDelegate(self.table_apps))
        self.table_apps.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_apps.customContextMenuRequested.connect(self.show_apps_context_menu)
        self.table_apps.itemDoubleClicked.connect(lambda item: self.open_app_audit())
        layout.addWidget(self.table_apps)

        # Action bar at bottom
        bot_bar = QHBoxLayout()
        bot_bar.setSpacing(5)

        self.lbl_apps_count = QLabel("Total: 0 packages")
        self.lbl_apps_count.setStyleSheet("color: #64748b; font-size: 11px;")
        bot_bar.addWidget(self.lbl_apps_count)
        bot_bar.addStretch()

        btn_bot_audit = styled_btn("🔍 Detail", "primary")
        btn_bot_audit.setToolTip("Buka halaman audit lengkap aplikasi terpilih")
        btn_bot_audit.clicked.connect(self.open_app_audit)

        btn_launch = QPushButton("🚀 Buka")
        btn_launch.clicked.connect(self.launch_selected)

        btn_freeze = QPushButton("❄ Freeze")
        btn_freeze.clicked.connect(self.disable_selected)

        btn_enable = QPushButton("⚡ Enable")
        btn_enable.clicked.connect(self.enable_selected)

        btn_stop = QPushButton("🛑 Stop")
        btn_stop.clicked.connect(self.stop_selected)

        btn_clear = QPushButton("🧹 Hapus Data")
        btn_clear.clicked.connect(self.clear_selected)

        btn_backup = QPushButton("💾 Backup APK")
        btn_backup.clicked.connect(self.backup_selected)

        btn_uninstall = styled_btn("🗑 Uninstall", "danger")
        btn_uninstall.clicked.connect(self.uninstall_selected)

        for b in [btn_bot_audit, btn_launch, btn_freeze, btn_enable, btn_stop, btn_clear, btn_backup, btn_uninstall]:
            bot_bar.addWidget(b)

        layout.addLayout(bot_bar)

    # -------------------------------------------------------------
    # 2. SETUP SUB-TAB: SMART DEBLOATER (UAD)
    # -------------------------------------------------------------
    def setup_debloat_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Informational banner
        banner = QFrame()
        banner.setObjectName("debloatBanner")
        banner.setStyleSheet("QFrame#debloatBanner { background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 5px; padding: 6px 10px; }")
        ban_layout = QHBoxLayout(banner)
        ban_layout.setContentsMargins(0, 0, 0, 0)
        ban_layout.setSpacing(8)

        lbl_icon = QLabel("🛡️")
        lbl_icon.setStyleSheet("font-size: 16px;")
        ban_layout.addWidget(lbl_icon)

        lbl_desc = QLabel("<b>Universal Android Debloater (UAD)</b>: Bersihkan aplikasi bawaan (bloatware) dengan aman. "
                         "Centang aplikasi yang ingin dihapus/dibekukan. Sistem menandai tingkat risiko agar terhindar dari bootloop.")
        lbl_desc.setStyleSheet("color: #166534; font-size: 11px;")
        lbl_desc.setWordWrap(True)
        ban_layout.addWidget(lbl_desc, 1)

        layout.addWidget(banner)

        # Row 1: Filter Categories using FlowLayout (Responsive Wrapping!)
        cat_container = QWidget()
        cat_flow = FlowLayout(cat_container, margin=0, spacing=12)

        lbl_filter = QLabel("Kategori:")
        lbl_filter.setStyleSheet("font-weight: 600; color: #475569; font-size: 11px;")
        cat_flow.addWidget(lbl_filter)

        self.grp_debloat_filter = QButtonGroup(self)
        self.rb_deb_rec = QRadioButton("🟢 Rekomendasi")
        self.rb_deb_rec.setStyleSheet("QRadioButton { color: #15803d; font-weight: bold; font-size: 11px; } QRadioButton:hover { color: #16a34a; }")
        self.rb_deb_rec.setToolTip("Aplikasi aman dihapus / dibekukan tanpa mengganggu stabilitas sistem")
        self.rb_deb_rec.setChecked(True)

        self.rb_deb_adv = QRadioButton("🟡 Bahaya")
        self.rb_deb_adv.setStyleSheet("QRadioButton { color: #b45309; font-weight: bold; font-size: 11px; } QRadioButton:hover { color: #d97706; }")
        self.rb_deb_adv.setToolTip("Aplikasi yang perlu diperhatikan / membutuhkan alternatif pengganti sebelum dihapus")

        self.rb_deb_crit = QRadioButton("🔴 Kritis")
        self.rb_deb_crit.setStyleSheet("QRadioButton { color: #dc2626; font-weight: bold; font-size: 11px; } QRadioButton:hover { color: #ef4444; }")
        self.rb_deb_crit.setToolTip("Aplikasi sistem inti, berisiko bootloop jika dihapus")

        self.rb_deb_all = QRadioButton("Semua Sistem")
        self.rb_deb_all.setStyleSheet("QRadioButton { color: #475569; font-weight: 500; font-size: 11px; }")
        self.rb_deb_all.setToolTip("Tampilkan seluruh paket sistem")

        self.rb_deb_done = QRadioButton("Sudah Didebloat")
        self.rb_deb_done.setStyleSheet("QRadioButton { color: #0284c7; font-weight: 500; font-size: 11px; }")
        self.rb_deb_done.setToolTip("Tampilkan paket yang saat ini dinonaktifkan atau dihapus dari user 0")

        for idx, rb in enumerate([self.rb_deb_rec, self.rb_deb_adv, self.rb_deb_crit, self.rb_deb_all, self.rb_deb_done]):
            self.grp_debloat_filter.addButton(rb, idx)
            cat_flow.addWidget(rb)
            rb.toggled.connect(lambda checked: self.on_debloat_filter_changed() if checked else None)

        layout.addWidget(cat_container)

        # Row 2: Checkbox Toolbar + Bulk Actions + Search + Refresh
        tools_row = QHBoxLayout()
        tools_row.setSpacing(6)

        btn_sel_all = QPushButton("☑️ Pilih Semua")
        btn_sel_all.setToolTip("Centang semua aplikasi yang sedang tampil di tabel")
        btn_sel_all.clicked.connect(self.select_all_debloat)
        tools_row.addWidget(btn_sel_all)

        btn_desel_all = QPushButton("◻️ Batal Pilih")
        btn_desel_all.setToolTip("Hapus semua centang pada tabel")
        btn_desel_all.clicked.connect(self.deselect_all_debloat)
        tools_row.addWidget(btn_desel_all)

        btn_update_db = QPushButton("🔄 Update UAD")
        btn_update_db.setToolTip("Perbarui database rekomendasi UAD dari GitHub")
        btn_update_db.clicked.connect(self.update_uad_database)
        tools_row.addWidget(btn_update_db)

        tools_row.addStretch()

        self.txt_deb_search = QLineEdit()
        self.txt_deb_search.setPlaceholderText("🔍 Cari nama package / deskripsi...")
        self.txt_deb_search.setMinimumWidth(150)
        self.txt_deb_search.setMaximumWidth(260)
        self.txt_deb_search.textChanged.connect(self.apply_debloat_filter)
        tools_row.addWidget(self.txt_deb_search)

        btn_deb_refresh = QPushButton("🔄 Refresh")
        btn_deb_refresh.setToolTip("Muat ulang daftar aplikasi dari perangkat")
        btn_deb_refresh.clicked.connect(lambda: self.refresh_debloat(force=True))
        tools_row.addWidget(btn_deb_refresh)

        btn_deb_audit = styled_btn("🔍 Detail", "primary")
        btn_deb_audit.setToolTip("Buka Detail & Audit Aplikasi lengkap")
        btn_deb_audit.clicked.connect(self.open_debloat_audit)
        tools_row.addWidget(btn_deb_audit)

        layout.addLayout(tools_row)

        # Debloat progress bar
        self.debloat_progress = QProgressBar()
        self.debloat_progress.setRange(0, 0)
        self.debloat_progress.setFixedHeight(3)
        self.debloat_progress.setVisible(False)
        layout.addWidget(self.debloat_progress)

        # Debloat Table with Checkboxes & 2-Line Items
        self.table_debloat = QTableWidget()
        self.table_debloat.setColumnCount(3)
        self.table_debloat.setHorizontalHeaderLabels(["Aplikasi & Package (Klik untuk Memilih)", "Status Keamanan UAD", "Deskripsi & Rekomendasi"])
        self.table_debloat.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table_debloat.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table_debloat.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_debloat.setColumnWidth(0, 420)
        self.table_debloat.setColumnWidth(1, 230)
        self.table_debloat.setWordWrap(True)
        self.table_debloat.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_debloat.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_debloat.setItemDelegateForColumn(0, AppPackageDelegate(self.table_debloat))
        self.table_debloat.setItemDelegateForColumn(1, StatusRatingDelegate(self.table_debloat))
        self.table_debloat.itemSelectionChanged.connect(self.on_debloat_selection_changed)
        self.table_debloat.itemChanged.connect(self.on_debloat_item_changed)
        self.table_debloat.cellClicked.connect(self.on_debloat_cell_clicked)
        self.table_debloat.itemDoubleClicked.connect(lambda item: self.open_debloat_audit())
        self.table_debloat.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_debloat.customContextMenuRequested.connect(self.show_debloat_context_menu)

        def on_deb_key_press(event):
            if event.key() == Qt.Key_Space:
                rows = set(idx.row() for idx in self.table_debloat.selectedIndexes())
                if rows:
                    self.table_debloat.blockSignals(True)
                    first_row = next(iter(rows))
                    first_it = self.table_debloat.item(first_row, 0)
                    new_st = Qt.Unchecked if (first_it and first_it.checkState() == Qt.Checked) else Qt.Checked
                    for r in rows:
                        it = self.table_debloat.item(r, 0)
                        if it:
                            it.setCheckState(new_st)
                    self.table_debloat.blockSignals(False)
                    self.update_debloat_selected_count()
                    return
            QTableWidget.keyPressEvent(self.table_debloat, event)

        self.table_debloat.keyPressEvent = on_deb_key_press
        layout.addWidget(self.table_debloat)


        # Detail information card
        self.card_debloat_info = QGroupBox("ℹ️ Detail Aplikasi && Panduan Keamanan")
        self.card_debloat_info.setFixedHeight(105)
        card_layout = QVBoxLayout(self.card_debloat_info)
        card_layout.setContentsMargins(8, 6, 8, 6)
        card_layout.setSpacing(3)

        self.lbl_deb_selected_title = QLabel("Klik salah satu aplikasi di tabel untuk melihat alasan keamanan dan risikonya.")
        self.lbl_deb_selected_title.setStyleSheet("font-weight: 600; color: #0284c7; font-size: 11px;")
        card_layout.addWidget(self.lbl_deb_selected_title)

        self.txt_deb_selected_desc = QTextEdit()
        self.txt_deb_selected_desc.setReadOnly(True)
        self.txt_deb_selected_desc.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; font-size: 11px; color: #1e293b;")
        card_layout.addWidget(self.txt_deb_selected_desc)

        layout.addWidget(self.card_debloat_info)

        # Debloat action row (bottom)
        deb_act_bar = QHBoxLayout()
        deb_act_bar.setSpacing(6)

        self.lbl_debloat_count = QLabel("Total: 0 packages")
        self.lbl_debloat_count.setStyleSheet("color: #64748b; font-size: 11px;")
        deb_act_bar.addWidget(self.lbl_debloat_count)
        deb_act_bar.addStretch()

        btn_deb_freeze = QPushButton("❄ Bekukan Terpilih (Freeze)")
        btn_deb_freeze.setToolTip("Nonaktifkan aplikasi yang dicentang tanpa menghapus file sistem")
        btn_deb_freeze.clicked.connect(self.disable_selected_debloat)

        btn_deb_restore = QPushButton("⚡ Pulihkan Terpilih (Enable)")
        btn_deb_restore.setToolTip("Aktifkan kembali / pulihkan aplikasi yang sudah didebloat (baik yang dibekukan maupun terhapus dari user 0)")
        btn_deb_restore.clicked.connect(self.enable_selected_debloat)

        btn_deb_uninstall = styled_btn("🗑 Uninstall Terpilih", "danger")
        btn_deb_uninstall.setToolTip("Hapus permanen paket yang dicentang dari user 0")
        btn_deb_uninstall.clicked.connect(self.uninstall_selected_debloat)

        deb_act_bar.addWidget(btn_deb_freeze)
        deb_act_bar.addWidget(btn_deb_restore)
        deb_act_bar.addWidget(btn_deb_uninstall)

        layout.addLayout(deb_act_bar)

    # -------------------------------------------------------------
    # 3. SETUP SUB-TAB: PASANG APK
    # -------------------------------------------------------------
    def setup_install_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Drag and Drop Banner
        self.drop_zone = QWidget()
        self.drop_zone.setObjectName("dropZone")
        self.drop_zone.setStyleSheet(
            "QWidget#dropZone { background-color: #f8fafc; border: 2px dashed #93c5fd; border-radius: 8px; padding: 16px; }"
        )
        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setSpacing(6)
        drop_layout.setAlignment(Qt.AlignCenter)

        self.lbl_drop_title = QLabel("📥 Seret & Lepas (Drag & Drop) File .APK ke Sini")
        self.lbl_drop_title.setAlignment(Qt.AlignCenter)
        self.lbl_drop_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #1e293b;")
        drop_layout.addWidget(self.lbl_drop_title)

        lbl_drop_sub = QLabel("atau klik tombol di bawah untuk memilih file dari komputer")
        lbl_drop_sub.setAlignment(Qt.AlignCenter)
        lbl_drop_sub.setStyleSheet("font-size: 11px; color: #64748b;")
        drop_layout.addWidget(lbl_drop_sub)

        btn_browse_apk = styled_btn("📂 Pilih File .APK dari Komputer...", "primary")
        btn_browse_apk.setFixedHeight(28)
        btn_browse_apk.setFixedWidth(240)
        btn_browse_apk.clicked.connect(self.browse_apks)
        drop_layout.addWidget(btn_browse_apk, 0, Qt.AlignCenter)

        layout.addWidget(self.drop_zone)

        # Selected APK Files List
        grp_files = QGroupBox("📋 File APK Terpilih")
        files_layout = QVBoxLayout(grp_files)
        files_layout.setContentsMargins(8, 6, 8, 6)
        files_layout.setSpacing(4)

        self.list_apks = QListWidget()
        self.list_apks.setFixedHeight(85)
        files_layout.addWidget(self.list_apks)

        layout.addWidget(grp_files)

        # Install Options
        grp_opts = QGroupBox("⚙️ Opsi Penginstalan")
        opts_layout = QHBoxLayout(grp_opts)
        opts_layout.setContentsMargins(8, 4, 8, 4)
        opts_layout.setSpacing(14)

        self.chk_reinstall = QCheckBox("Timpa Aplikasi yang Ada (-r / Reinstall)")
        self.chk_reinstall.setChecked(True)
        self.chk_downgrade = QCheckBox("Izinkan Downgrade Versi (-d)")
        self.chk_grant = QCheckBox("Berikan Semua Izin Otomatis (-g)")
        self.chk_grant.setChecked(True)

        opts_layout.addWidget(self.chk_reinstall)
        opts_layout.addWidget(self.chk_downgrade)
        opts_layout.addWidget(self.chk_grant)
        opts_layout.addStretch()

        layout.addWidget(grp_opts)

        # Install Action Row & Progress
        act_row = QHBoxLayout()
        act_row.setSpacing(8)

        self.btn_start_install = styled_btn("🚀 Pasang (Install) APK Sekarang", "success")
        self.btn_start_install.setFixedHeight(28)
        self.btn_start_install.clicked.connect(self.start_install_process)
        act_row.addWidget(self.btn_start_install)

        btn_clear_list = QPushButton("🧹 Kosongkan Daftar")
        btn_clear_list.setFixedHeight(28)
        btn_clear_list.clicked.connect(self.clear_selected_apks)
        act_row.addWidget(btn_clear_list)

        act_row.addStretch()
        layout.addLayout(act_row)

        self.install_progress = QProgressBar()
        self.install_progress.setRange(0, 0)
        self.install_progress.setFixedHeight(4)
        self.install_progress.setVisible(False)
        layout.addWidget(self.install_progress)

        # Log Output Area
        self.txt_install_log = QTextEdit()
        self.txt_install_log.setReadOnly(True)
        self.txt_install_log.setPlaceholderText("Log proses penginstalan APK akan muncul di sini...")
        self.txt_install_log.setFixedHeight(95)
        layout.addWidget(self.txt_install_log)

    # -------------------------------------------------------------
    # DEVICE STATE & DATA LOADING
    # -------------------------------------------------------------
    def set_device(self, serial: str):
        if self.current_serial == serial and self.all_debloat_packages:
            return
        self.current_serial = serial
        self.all_debloat_packages = []
        self.filtered_debloat_packages = []
        self.app_packages = []
        self._install_times = {}
        if serial:
            self.refresh_apps()
            self.refresh_debloat(force=True)
        else:
            self.table_apps.setRowCount(0)
            self.table_debloat.setRowCount(0)
            self.lbl_apps_count.setText("Total: 0 packages")
            self.lbl_debloat_count.setText("Total: 0 packages")

    # -------------------------------------------------------------
    # LOGIC: KELOLA APLIKASI
    # -------------------------------------------------------------
    def on_app_filter_changed(self):
        self.refresh_apps()

    def get_app_filter_type(self) -> str:
        if self.rb_app_user.isChecked():
            return "user"
        elif self.rb_app_sys.isChecked():
            return "system"
        elif self.rb_app_dis.isChecked():
            return "disabled"
        return "all"

    def refresh_apps(self):
        if not self.current_serial:
            return

        if self.apps_worker and self.apps_worker.isRunning():
            try:
                self.apps_worker.finished.disconnect()
            except Exception:
                pass

        self.apps_progress.setVisible(True)
        filter_type = self.get_app_filter_type()
        worker = PackageLoadWorker(self.current_serial, filter_type)
        self.apps_worker = worker
        self._active_workers.add(worker)

        def on_done(packages: list):
            self._active_workers.discard(worker)
            self.on_apps_loaded(packages)

        worker.finished.connect(on_done)
        worker.start()

        # Silently pre-fetch install times in background for fast date sorting
        if not self._install_times:
            self._start_fetch_install_times()

    def _start_fetch_install_times(self):
        if not self.current_serial:
            return
        if self.install_times_worker and self.install_times_worker.isRunning():
            return
        worker = InstallTimesWorker(self.current_serial)
        self.install_times_worker = worker
        self._active_workers.add(worker)

        def on_times_loaded(times: dict):
            self._active_workers.discard(worker)
            self._install_times = times
            # Re-render table if date sorting or to populate date column
            self.filter_apps_table()

        worker.finished.connect(on_times_loaded)
        worker.start()

    def on_sort_changed(self):
        sort_mode = self.cmb_app_sort.currentIndex()
        if sort_mode in (2, 3) and not self._install_times and self.current_serial:
            if self.install_times_worker and self.install_times_worker.isRunning():
                QApplication.setOverrideCursor(Qt.WaitCursor)
                try:
                    self.install_times_worker.wait(4000)
                finally:
                    QApplication.restoreOverrideCursor()
            else:
                self._start_fetch_install_times()
        self.filter_apps_table()

    def on_apps_loaded(self, packages: list):
        self.apps_progress.setVisible(False)
        self.app_packages = packages
        self.filter_apps_table()

    def filter_apps_table(self):
        query = self.txt_app_search.text().strip().lower()
        filtered = [
            p for p in self.app_packages
            if query in p["name"].lower() or query in p.get("app_name", "").lower() or query in p.get("path", "").lower()
        ]

        # Apply sorting based on cmb_app_sort
        sort_mode = self.cmb_app_sort.currentIndex() if hasattr(self, 'cmb_app_sort') else 0
        if sort_mode == 0:
            # Nama Aplikasi (A → Z)
            filtered.sort(key=lambda p: (p.get("app_name") or p["name"]).lower())
        elif sort_mode == 1:
            # Nama Aplikasi (Z → A)
            filtered.sort(key=lambda p: (p.get("app_name") or p["name"]).lower(), reverse=True)
        elif sort_mode == 2:
            # Tanggal Pasang (Terbaru)
            filtered.sort(key=lambda p: self._install_times.get(p["name"], ""), reverse=True)
        elif sort_mode == 3:
            # Tanggal Pasang (Terlama)
            filtered.sort(key=lambda p: self._install_times.get(p["name"], "9999-99-99"))
        elif sort_mode == 4:
            # Nama Package (A → Z)
            filtered.sort(key=lambda p: p["name"].lower())
        elif sort_mode == 5:
            # Nama Package (Z → A)
            filtered.sort(key=lambda p: p["name"].lower(), reverse=True)
        elif sort_mode == 6:
            # Tipe (Pengguna dulu)
            def type_key(p):
                path = p.get("path", "")
                is_user = not path.startswith("/system/") and not path.startswith("/apex/")
                return (0 if is_user else 1, (p.get("app_name") or p["name"]).lower())
            filtered.sort(key=type_key)

        self.table_apps.setRowCount(len(filtered))
        for row, pkg in enumerate(filtered):
            pkg_name = pkg["name"]
            app_title = pkg.get("app_name") or extract_app_name(pkg_name)
            name_item = QTableWidgetItem(f"{app_title}\n{pkg_name}")
            name_item.setData(Qt.UserRole, pkg)
            name_item.setToolTip(f"📱 {app_title}\n📦 {pkg_name}\n📂 {pkg.get('path', '')}")

            pkg_type = "Pengguna" if not pkg["path"].startswith("/system/") and not pkg["path"].startswith("/apex/") else "Sistem"
            type_item = QTableWidgetItem(pkg_type)
            type_item.setForeground(QColor("#0284c7" if pkg_type == "Pengguna" else "#64748b"))

            install_date = self._install_times.get(pkg_name, "")
            display_date = install_date[:16] if len(install_date) >= 16 else install_date
            date_item = QTableWidgetItem(display_date or "-")
            date_item.setForeground(QColor("#475569"))
            if install_date:
                date_item.setToolTip(f"Dipasang pada: {install_date}")

            path_item = QTableWidgetItem(pkg["path"])
            path_item.setToolTip(pkg["path"])

            item_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            name_item.setFlags(item_flags)
            type_item.setFlags(item_flags)
            date_item.setFlags(item_flags)
            path_item.setFlags(item_flags)

            self.table_apps.setItem(row, 0, name_item)
            self.table_apps.setItem(row, 1, type_item)
            self.table_apps.setItem(row, 2, date_item)
            self.table_apps.setItem(row, 3, path_item)
            self.table_apps.setRowHeight(row, 44)

        self.lbl_apps_count.setText(f"Menampilkan {len(filtered)} dari {len(self.app_packages)} aplikasi")

    def get_selected_app_package(self) -> str:
        row = self.table_apps.currentRow()
        if row >= 0:
            item = self.table_apps.item(row, 0)
            if item:
                data = item.data(Qt.UserRole)
                if data and isinstance(data, dict):
                    return data.get("name", "")
                text = item.text()
                if "\n" in text:
                    return text.split("\n", 1)[1].strip()
                if "(" in text and text.endswith(")"):
                    return text.rsplit("(", 1)[1].rstrip(")").strip()
                return text
        return ""

    def get_selected_app_path(self) -> str:
        row = self.table_apps.currentRow()
        if row >= 0:
            item0 = self.table_apps.item(row, 0)
            if item0:
                data = item0.data(Qt.UserRole)
                if data and isinstance(data, dict) and data.get("path"):
                    return data.get("path")
            item_last = self.table_apps.item(row, 3)
            return item_last.text() if item_last else ""
        return ""

    def open_app_audit(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            QMessageBox.information(self, "Pilih Aplikasi", "Silakan pilih salah satu aplikasi di tabel terlebih dahulu untuk melihat audit & detail.")
            return

        row = self.table_apps.currentRow()
        app_title = ""
        if row >= 0:
            item = self.table_apps.item(row, 0)
            if item:
                data = item.data(Qt.UserRole)
                if data and isinstance(data, dict):
                    app_title = data.get("app_name", "")
        if not app_title:
            app_title = extract_app_name(pkg)

        dlg = AppAuditDialog(self.current_serial, pkg, app_title, self)
        dlg.exec()

    def launch_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        adb_manager.launch_app(self.current_serial, pkg)

    def disable_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        app_title = extract_app_name(pkg)
        rating = debloater_service.get_safety_rating(pkg)
        is_unsafe = rating.get("level") in ["Unsafe", "Expert", "Advanced"]
        warning_msg = f"{rating.get('label')} - {rating.get('description')}" if is_unsafe else ""
        if not confirm_two_step(self, "freeze", app_title, pkg, warning_msg, is_critical_system=(rating.get("level") == "Unsafe")):
            return
        ok, out = adb_manager.disable_package(self.current_serial, pkg)
        if ok:
            QMessageBox.information(self, "Berhasil", f"Paket {app_title} ({pkg}) berhasil dibekukan (disabled)!")
            self.refresh_apps()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal menonaktifkan:\n{out}")

    def enable_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        app_title = extract_app_name(pkg)
        reply = QMessageBox.question(
            self, "Konfirmasi Aktifkan",
            f"Aktifkan kembali aplikasi <b>{app_title}</b> ({pkg})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return
        ok, out = adb_manager.enable_package(self.current_serial, pkg)
        if ok:
            QMessageBox.information(self, "Berhasil", f"Paket {app_title} ({pkg}) berhasil diaktifkan kembali!")
            self.refresh_apps()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal mengaktifkan:\n{out}")

    def stop_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        adb_manager.force_stop_package(self.current_serial, pkg)
        QMessageBox.information(self, "Force Stop", f"Berhasil menghentikan {pkg}")

    def clear_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        app_title = extract_app_name(pkg)
        if not confirm_two_step(self, "clear_data", app_title, pkg):
            return
        ok, out = adb_manager.clear_package_data(self.current_serial, pkg)
        if ok:
            QMessageBox.information(self, "Sukses", f"Data & cache {app_title} ({pkg}) berhasil dibersihkan.")
        else:
            QMessageBox.critical(self, "Gagal", out)

    def backup_selected(self):
        path = self.get_selected_app_path()
        name = self.get_selected_app_package()
        if not path or not name or not self.current_serial:
            return
        default_dir = settings.get("default_download_dir") or os.getcwd()
        dest_path, _ = QFileDialog.getSaveFileName(self, "Simpan APK", os.path.join(default_dir, f"{name}.apk"), "Android Package (*.apk)")
        if dest_path:
            self.apps_progress.setVisible(True)
            ok, out = adb_manager.pull_apk(self.current_serial, path, dest_path)
            self.apps_progress.setVisible(False)
            if ok:
                QMessageBox.information(self, "Sukses", f"APK berhasil diekstrak ke:\n{dest_path}")
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal ekstrak APK:\n{out}")

    def uninstall_selected(self):
        pkg = self.get_selected_app_package()
        if not pkg or not self.current_serial:
            return
        app_title = extract_app_name(pkg)
        rating = debloater_service.get_safety_rating(pkg)
        is_unsafe = rating.get("level") in ["Unsafe", "Expert", "Advanced"]
        warning_msg = f"{rating.get('label')} - {rating.get('description')}" if is_unsafe else ""

        if not confirm_two_step(self, "uninstall", app_title, pkg, warning_msg, is_critical_system=(rating.get("level") == "Unsafe")):
            return
        ok, out = adb_manager.uninstall_package(self.current_serial, pkg)
        if ok and "Success" in out:
            QMessageBox.information(self, "Berhasil", f"Berhasil menghapus (uninstall) {app_title} ({pkg})")
            self.refresh_apps()
        else:
            QMessageBox.critical(self, "Gagal", f"Gagal uninstall:\n{out}")

    def show_apps_context_menu(self, pos):
        item = self.table_apps.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.addAction("🔍 Detail & Audit Aplikasi", self.open_app_audit)
        menu.addSeparator()
        menu.addAction("🚀 Buka Aplikasi", self.launch_selected)
        menu.addAction("❄ Freeze / Bekukan", self.disable_selected)
        menu.addAction("⚡ Enable / Aktifkan", self.enable_selected)
        menu.addAction("🛑 Force Stop", self.stop_selected)
        menu.addAction("🧹 Clear Data & Cache", self.clear_selected)
        menu.addAction("💾 Backup / Ekstrak APK", self.backup_selected)
        menu.addSeparator()
        menu.addAction("🗑 Uninstall", self.uninstall_selected)
        menu.exec(self.table_apps.viewport().mapToGlobal(pos))

    # -------------------------------------------------------------
    # LOGIC: SMART DEBLOATER (UAD)
    # -------------------------------------------------------------
    def on_debloat_filter_changed(self):
        self.apply_debloat_filter()

    def get_debloat_filter_type(self) -> str:
        if self.rb_deb_rec.isChecked():
            return "rec"
        elif self.rb_deb_adv.isChecked():
            return "adv"
        elif self.rb_deb_crit.isChecked():
            return "unsafe"
        elif self.rb_deb_done.isChecked():
            return "debloated"
        return "system"

    def refresh_debloat(self, force: bool = False):
        if not self.current_serial:
            return

        if self.all_debloat_packages and not force:
            self.apply_debloat_filter()
            return

        # Disconnect previous debloat worker if running to prevent stale updates
        if self.deb_worker and self.deb_worker.isRunning():
            try:
                self.deb_worker.finished.disconnect()
            except Exception:
                pass

        self.debloat_progress.setVisible(True)
        worker = PackageLoadWorker(self.current_serial, "debloat_all")
        self.deb_worker = worker
        self._active_workers.add(worker)

        def on_done(pkgs: list):
            self._active_workers.discard(worker)
            self.debloat_progress.setVisible(False)
            self.all_debloat_packages = pkgs
            self.apply_debloat_filter()

        worker.finished.connect(on_done)
        worker.start()

    def apply_debloat_filter(self):
        if not self.all_debloat_packages:
            if self.current_serial:
                self.refresh_debloat()
            return

        flt = self.get_debloat_filter_type()
        query = self.txt_deb_search.text().strip().lower()

        filtered = []
        for p in self.all_debloat_packages:
            rating = p.get("rating", {})
            level = rating.get("level", "Unknown")
            pkg_name = p.get("name", "")
            app_name = p.get("app_name", "")
            desc = rating.get("description", "")
            state = p.get("state", "enabled")

            # Filter by safety category or debloated state
            if flt == "debloated":
                # Only show packages that have been debloated (disabled or uninstalled)
                if state not in ["disabled", "uninstalled"]:
                    continue
            elif flt == "rec":
                if level != "Recommended" or state != "enabled":
                    continue
            elif flt == "adv":
                if level not in ["Advanced", "Expert"] or state != "enabled":
                    continue
            elif flt == "unsafe":
                if level != "Unsafe" or state != "enabled":
                    continue
            elif flt == "system":
                # All system packages
                pass

            # Filter by search query (checks package name, app name, and description)
            if query and (query not in pkg_name.lower() and query not in app_name.lower() and query not in desc.lower()):
                continue

            filtered.append(p)

        self.filtered_debloat_packages = filtered
        self.populate_debloat_table(filtered)

    def populate_debloat_table(self, packages=None):
        if packages is None:
            packages = self.filtered_debloat_packages

        self.table_debloat.blockSignals(True)
        self.table_debloat.setRowCount(len(packages))

        for row, pkg in enumerate(packages):
            pkg_name = pkg["name"]
            rating = pkg.get("rating", debloater_service.get_safety_rating(pkg_name))
            app_name = pkg.get("app_name") or extract_app_name(pkg_name, rating.get("description", ""))
            pkg["app_name"] = app_name

            # Col 0: Checkbox + Icon + 2-line: Nama Aplikasi (Line 1) & Nama Paket (Line 2)
            name_item = QTableWidgetItem(f"{app_name}\n{pkg_name}")
            # Note: Do not set Qt.ItemIsUserCheckable so Qt does not conflict with row-wide click toggle!
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            name_item.setCheckState(Qt.Unchecked)
            name_item.setData(Qt.UserRole, pkg)
            name_item.setToolTip(f"{app_name}\nPackage: {pkg_name}\n(Klik di mana saja pada baris untuk memilih)")

            # Col 1: Status & Safety Rating (Format 2 Baris Bersih)
            state = pkg.get("state", "enabled")
            if state == "disabled":
                state_text = "❄️ Dibekukan"
                state_color = "#0284c7"
            elif state == "uninstalled":
                state_text = "🗑️ Terhapus (User 0)"
                state_color = "#64748b"
            else:
                state_text = "✅ Aktif Terpasang"
                state_color = "#15803d"

            rating_label = rating["label"]
            rating_color = rating["color"]

            status_2lines = f"{state_text}\n{rating_label}"
            safety_item = QTableWidgetItem(status_2lines)
            safety_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            safety_item.setData(Qt.UserRole + 1, state_color)
            safety_item.setData(Qt.UserRole + 2, rating_color)
            safety_item.setToolTip(f"Status saat ini: {state.capitalize()}\nLevel UAD: {rating['label']}")

            # Col 2: Description (shows full text across stretched column width)
            raw_desc = rating.get("description", "").strip()
            clean_desc = " ".join(raw_desc.splitlines()).strip()
            desc_item = QTableWidgetItem(clean_desc or "Aplikasi bawaan sistem")
            desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            desc_item.setToolTip(raw_desc or "Aplikasi bawaan sistem")

            self.table_debloat.setItem(row, 0, name_item)
            self.table_debloat.setItem(row, 1, safety_item)
            self.table_debloat.setItem(row, 2, desc_item)
            self.table_debloat.setRowHeight(row, 44)

        self.table_debloat.blockSignals(False)
        self.update_debloat_selected_count()
        self.clear_debloat_selection_info()

    def on_debloat_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            self.update_debloat_selected_count()

    def on_debloat_cell_clicked(self, row: int, col: int):
        # Toggle checkbox when clicking ANYWHERE on the row (Col 0, Col 1, Col 2)
        item = self.table_debloat.item(row, 0)
        if item:
            new_state = Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
            item.setCheckState(new_state)

    def update_debloat_selected_count(self):
        total = self.table_debloat.rowCount()
        checked = self.get_checked_debloat_packages()
        flt = self.get_debloat_filter_type()
        status_suffix = "sudah didebloat" if flt == "debloated" else "paket"
        if checked:
            self.lbl_debloat_count.setText(f"Menampilkan {total} {status_suffix} | <b><font color='#2563eb'>{len(checked)} dipilih</font></b>")
        else:
            self.lbl_debloat_count.setText(f"Menampilkan {total} {status_suffix}")

    def select_all_debloat(self):
        self.table_debloat.blockSignals(True)
        for r in range(self.table_debloat.rowCount()):
            it = self.table_debloat.item(r, 0)
            if it:
                it.setCheckState(Qt.Checked)
        self.table_debloat.blockSignals(False)
        self.update_debloat_selected_count()

    def deselect_all_debloat(self):
        self.table_debloat.blockSignals(True)
        for r in range(self.table_debloat.rowCount()):
            it = self.table_debloat.item(r, 0)
            if it:
                it.setCheckState(Qt.Unchecked)
        self.table_debloat.blockSignals(False)
        self.update_debloat_selected_count()

    def get_checked_debloat_packages(self) -> list:
        checked = []
        for r in range(self.table_debloat.rowCount()):
            it = self.table_debloat.item(r, 0)
            if it and it.checkState() == Qt.Checked:
                data = it.data(Qt.UserRole)
                if data:
                    checked.append(data)
                else:
                    raw_pkg = it.text().split("\n")[-1].strip()
                    checked.append({"name": raw_pkg, "rating": debloater_service.get_safety_rating(raw_pkg)})
        return checked

    def get_target_debloat_packages(self) -> list:
        checked = self.get_checked_debloat_packages()
        if checked:
            return checked

        row = self.table_debloat.currentRow()
        if row >= 0:
            it = self.table_debloat.item(row, 0)
            if it:
                data = it.data(Qt.UserRole)
                if data:
                    return [data]
                raw_pkg = it.text().split("\n")[-1].strip()
                return [{"name": raw_pkg, "rating": debloater_service.get_safety_rating(raw_pkg)}]
        return []

    def on_debloat_selection_changed(self):
        row = self.table_debloat.currentRow()
        if row >= 0:
            name_item = self.table_debloat.item(row, 0)
            if name_item:
                pkg_data = name_item.data(Qt.UserRole)
                if pkg_data:
                    pkg_name = pkg_data.get("name", "")
                    app_name = pkg_data.get("app_name") or pkg_name
                    rating = pkg_data.get("rating", debloater_service.get_safety_rating(pkg_name))
                    state = pkg_data.get("state", "enabled")
                    state_tag = " [❄️ DIBEKUKAN]" if state == "disabled" else (" [🗑️ TERHAPUS DARI USER 0]" if state == "uninstalled" else "")
                    self.lbl_deb_selected_title.setText(f"📦 {app_name} ({pkg_name}){state_tag} — {rating['label']}")
                    self.lbl_deb_selected_title.setStyleSheet(f"font-weight: 600; color: {rating['color']}; font-size: 11px;")
                    self.txt_deb_selected_desc.setText(rating["description"])
                    return
        self.clear_debloat_selection_info()

    def clear_debloat_selection_info(self):
        self.lbl_deb_selected_title.setText("Klik salah satu aplikasi di tabel untuk melihat alasan keamanan dan risikonya.")
        self.lbl_deb_selected_title.setStyleSheet("font-weight: 600; color: #0284c7; font-size: 11px;")
        self.txt_deb_selected_desc.clear()

    def open_debloat_audit(self):
        row = self.table_debloat.currentRow()
        if row < 0 or not self.current_serial:
            QMessageBox.information(self, "Pilih Aplikasi", "Silakan pilih salah satu aplikasi di tabel terlebih dahulu.")
            return
        item = self.table_debloat.item(row, 0)
        if not item:
            return
        pkg_data = item.data(Qt.UserRole)
        if not pkg_data or not isinstance(pkg_data, dict):
            return
        pkg = pkg_data.get("name", "")
        app_title = pkg_data.get("app_name", "") or extract_app_name(pkg)
        dlg = AppAuditDialog(self.current_serial, pkg, app_title, self)
        dlg.exec()

    def show_debloat_context_menu(self, pos):
        item = self.table_debloat.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.addAction("🔍 Detail & Audit Aplikasi", self.open_debloat_audit)
        menu.addSeparator()
        menu.addAction("❄ Bekukan (Freeze)", self.disable_selected_debloat)
        menu.addAction("⚡ Pulihkan (Enable)", self.enable_selected_debloat)
        menu.addSeparator()
        menu.addAction("☑️ Centang Semua", self.select_all_debloat)
        menu.addAction("◻️ Batal Centang Semua", self.deselect_all_debloat)
        menu.addSeparator()
        menu.addAction("🗑 Uninstall", self.uninstall_selected_debloat)
        menu.exec(self.table_debloat.viewport().mapToGlobal(pos))

    def disable_selected_debloat(self):
        targets = self.get_target_debloat_packages()
        if not targets:
            QMessageBox.warning(self, "Pilih Aplikasi", "Silakan centang satu atau beberapa aplikasi pada tabel untuk dibekukan (freeze).")
            return
        if not self.current_serial:
            return

        count = len(targets)
        if count == 1:
            pkg_name = targets[0]["name"]
            app_title = targets[0].get("app_name") or extract_app_name(pkg_name)
            rating = debloater_service.get_safety_rating(pkg_name)
            is_unsafe = rating.get("level") in ["Unsafe", "Expert", "Advanced"]
            warning_msg = f"{rating.get('label')} - {rating.get('description')}" if is_unsafe else ""
            if not confirm_two_step(self, "freeze", app_title, pkg_name, warning_msg, is_critical_system=(rating.get("level") == "Unsafe")):
                return
        else:
            msg1 = QMessageBox(self)
            msg1.setIcon(QMessageBox.Question)
            msg1.setWindowTitle("❄️ Konfirmasi Bekukan Aplikasi (Langkah 1/2)")
            msg1.setText(f"Apakah Anda yakin ingin membekukan (nonaktifkan) <b>{count} aplikasi</b> terpilih?\n\nAplikasi yang dibekukan dapat dipulihkan kapan saja.")
            btn_yes1 = msg1.addButton("Ya, Lanjutkan", QMessageBox.YesRole)
            btn_no1 = msg1.addButton("Batal", QMessageBox.NoRole)
            msg1.setDefaultButton(btn_no1)
            msg1.exec()
            if msg1.clickedButton() != btn_yes1:
                return

            msg2 = QMessageBox(self)
            msg2.setIcon(QMessageBox.Warning)
            msg2.setWindowTitle("⚠️ Verifikasi Pembekuan (Langkah 2/2)")
            msg2.setText(f"Lanjutkan pembekuan untuk <b>{count} aplikasi</b> terpilih sekarang?")
            btn_yes2 = msg2.addButton("Ya, Bekukan Sekarang", QMessageBox.YesRole)
            btn_no2 = msg2.addButton("Batal", QMessageBox.NoRole)
            msg2.setDefaultButton(btn_no2)
            msg2.exec()
            if msg2.clickedButton() != btn_yes2:
                return

        self.execute_batch_debloat(targets, "disable")

    def enable_selected_debloat(self):
        targets = self.get_target_debloat_packages()
        if not targets:
            QMessageBox.warning(self, "Pilih Aplikasi", "Silakan centang satu atau beberapa aplikasi pada tabel untuk dipulihkan (enable).")
            return
        if not self.current_serial:
            return

        count = len(targets)
        reply = QMessageBox.question(
            self, "Konfirmasi Pulihkan",
            f"Aktifkan kembali (restore) <b>{count} aplikasi</b> terpilih?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        self.execute_batch_debloat(targets, "enable")

    def uninstall_selected_debloat(self):
        targets = self.get_target_debloat_packages()
        if not targets:
            QMessageBox.warning(self, "Pilih Aplikasi", "Silakan centang satu atau beberapa aplikasi pada tabel untuk dihapus (uninstall).")
            return
        if not self.current_serial:
            return

        count = len(targets)
        if count == 1:
            pkg_name = targets[0]["name"]
            app_title = targets[0].get("app_name") or extract_app_name(pkg_name)
            rating = debloater_service.get_safety_rating(pkg_name)
            is_unsafe = rating.get("level") in ["Unsafe", "Expert", "Advanced"]
            warning_msg = f"{rating.get('label')} - {rating.get('description')}" if is_unsafe else ""
            if not confirm_two_step(self, "uninstall", app_title, pkg_name, warning_msg, is_critical_system=(rating.get("level") == "Unsafe")):
                return
        else:
            msg1 = QMessageBox(self)
            msg1.setIcon(QMessageBox.Question)
            msg1.setWindowTitle("⚠️ Konfirmasi Uninstall Batch (Langkah 1/2)")
            msg1.setText(f"Apakah Anda yakin ingin mencopot (uninstall dari user 0) <b>{count} aplikasi</b> terpilih?")
            msg1.setInformativeText("Klik 'Ya, Lanjutkan' untuk memeriksa verifikasi risiko keamanan.")
            btn_yes1 = msg1.addButton("Ya, Lanjutkan", QMessageBox.YesRole)
            btn_no1 = msg1.addButton("Batal", QMessageBox.NoRole)
            msg1.setDefaultButton(btn_no1)
            msg1.exec()
            if msg1.clickedButton() != btn_yes1:
                return

            unsafe_items = []
            adv_items = []
            for p in targets:
                name = p.get("name", "")
                rating = p.get("rating", debloater_service.get_safety_rating(name))
                if rating["level"] == "Unsafe":
                    unsafe_items.append(f"• {name} (BAHAYA: {rating['label']})")
                elif rating["level"] in ["Expert", "Advanced"]:
                    adv_items.append(f"• {name} ({rating['label']})")

            msg2 = QMessageBox(self)
            if unsafe_items:
                msg2.setIcon(QMessageBox.Critical)
                msg2.setWindowTitle("🚨 PERINGATAN BAHAYA KRITIS SISTEM! (Langkah 2/2)")
                unsafe_str = "\n".join(unsafe_items[:8])
                if len(unsafe_items) > 8:
                    unsafe_str += f"\n... dan {len(unsafe_items) - 8} lainnya"
                msg2.setText(
                    f"Terdapat <b>{len(unsafe_items)} aplikasi KRITIS</b> terpilih:\n\n{unsafe_str}\n\n"
                    f"⚠️ <b>PERINGATAN KERUSAKAN:</b>\n"
                    f"Menghapus aplikasi ini hampir dipastikan akan membuat HP Anda <b>BOOTLOOP</b>!\n\n"
                    f"Apakah Anda BENAR-BENAR YAKIN ingin menanggung risiko kerusakan ini?"
                )
            elif adv_items:
                msg2.setIcon(QMessageBox.Warning)
                msg2.setWindowTitle("⚠️ Peringatan Keamanan Lanjutan (Langkah 2/2)")
                adv_str = "\n".join(adv_items[:8])
                msg2.setText(
                    f"Terdapat <b>{len(adv_items)} aplikasi lanjutan</b> terpilih:\n\n{adv_str}\n\n"
                    f"Pastikan Anda memiliki aplikasi pengganti sebelum menghapus.\n\n"
                    f"Apakah Anda yakin ingin melanjutkan pencopotan {count} aplikasi?"
                )
            else:
                msg2.setIcon(QMessageBox.Warning)
                msg2.setWindowTitle("🚨 Verifikasi Akhir Uninstall (Langkah 2/2)")
                msg2.setText(
                    f"Tindakan ini akan menghapus (uninstall dari user 0) <b>{count} aplikasi</b> terpilih.\n\n"
                    f"Apakah Anda BENAR-BENAR YAKIN ingin mencopot sekarang?"
                )

            btn_yes2 = msg2.addButton("Ya, Saya Yakin", QMessageBox.YesRole)
            btn_no2 = msg2.addButton("Batal", QMessageBox.NoRole)
            msg2.setDefaultButton(btn_no2)
            msg2.exec()
            if msg2.clickedButton() != btn_yes2:
                return

        self.execute_batch_debloat(targets, "uninstall")

    def execute_batch_debloat(self, target_packages: list, action_type: str):
        action_names = {
            "disable": ("Membekukan", "dibekukan"),
            "enable": ("Memulihkan", "dipulihkan"),
            "uninstall": ("Menghapus", "dihapus")
        }
        title, past_verb = action_names.get(action_type, ("Memproses", "diproses"))
        pkg_names = [p["name"] if isinstance(p, dict) else str(p) for p in target_packages]
        total = len(pkg_names)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{title} {total} Paket")
        dlg.setFixedSize(400, 130)
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(14, 12, 14, 12)
        dlg_layout.setSpacing(8)

        lbl_status = QLabel(f"Sedang {title.lower()} aplikasi (0/{total})...")
        lbl_status.setStyleSheet("font-size: 11px; color: #1e293b; font-weight: 500;")
        dlg_layout.addWidget(lbl_status)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setFixedHeight(8)
        dlg_layout.addWidget(progress)

        worker = BatchDebloatWorker(self.current_serial, pkg_names, action_type)
        self._active_workers.add(worker)

        worker.progress.connect(lambda pct, msg: (progress.setValue(pct), lbl_status.setText(msg)))

        def on_done(s_count, f_count):
            self._active_workers.discard(worker)
            dlg.accept()
            msg = f"Proses selesai!\n• Berhasil {past_verb}: {s_count}\n• Gagal: {f_count}"
            QMessageBox.information(self, f"{title} Selesai", msg)
            self.refresh_debloat(force=True)

        worker.finished.connect(on_done)
        worker.start()

        dlg.exec()

    def update_uad_database(self):
        self.debloat_progress.setVisible(True)
        ok, msg = debloater_service.update_database_online()
        self.debloat_progress.setVisible(False)
        if ok:
            QMessageBox.information(self, "Database UAD Terupdate", msg)
            self.refresh_debloat()
        else:
            QMessageBox.critical(self, "Gagal Update", msg)

    def open_batch_debloat_dialog(self):
        if not self.current_serial:
            QMessageBox.warning(self, "No Device", "Silakan hubungkan perangkat terlebih dahulu.")
            return

        # Fetch all recommended packages currently on the device
        all_pkgs = adb_manager.list_packages(self.current_serial, "all")
        rec_pkgs = []
        for p in all_pkgs:
            rating = debloater_service.get_safety_rating(p["name"])
            if rating["level"] == "Recommended":
                rec_pkgs.append(p)

        if not rec_pkgs:
            QMessageBox.information(self, "Bersih!", "Tidak ditemukan aplikasi bloatware 'Recommended' yang terpasang di perangkat Anda!")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Batch Debloat (Aplikasi Rekomendasi Aman)")
        dlg.resize(480, 420)
        d_layout = QVBoxLayout(dlg)
        d_layout.setContentsMargins(12, 12, 12, 12)
        d_layout.setSpacing(8)

        lbl_info = QLabel(f"Ditemukan {len(rec_pkgs)} aplikasi bloatware yang 100% AMAN untuk didebloat:")
        lbl_info.setStyleSheet("color: #16a34a; font-weight: 600; font-size: 11px;")
        d_layout.addWidget(lbl_info)

        list_widget = QListWidget()
        for p in rec_pkgs:
            item = QListWidgetItem(f"🟢 {p['name']}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, p["name"])
            list_widget.addItem(item)
        d_layout.addWidget(list_widget)

        chk_freeze_only = QCheckBox("Bekukan saja (Disable/Freeze - Disarankan)")
        chk_freeze_only.setChecked(True)
        d_layout.addWidget(chk_freeze_only)

        progress_debloat = QProgressBar()
        progress_debloat.setVisible(False)
        d_layout.addWidget(progress_debloat)

        row_btn = QHBoxLayout()
        btn_sel_all = QPushButton("Pilih Semua")
        btn_sel_all.clicked.connect(lambda: [list_widget.item(i).setCheckState(Qt.Checked) for i in range(list_widget.count())])
        btn_desel = QPushButton("Hapus Pilihan")
        btn_desel.clicked.connect(lambda: [list_widget.item(i).setCheckState(Qt.Unchecked) for i in range(list_widget.count())])

        btn_run = styled_btn("🚀 Eksekusi Debloat", "primary")

        def run_batch():
            selected = []
            for i in range(list_widget.count()):
                it = list_widget.item(i)
                if it.checkState() == Qt.Checked:
                    selected.append(it.data(Qt.UserRole))

            if not selected:
                QMessageBox.warning(dlg, "Pilih Aplikasi", "Pilih minimal 1 aplikasi untuk didebloat.")
                return

            action_type = "disable" if chk_freeze_only.isChecked() else "uninstall"
            action_label = "membekukan" if action_type == "disable" else "menghapus"

            reply = QMessageBox.question(dlg, "Konfirmasi", f"Anda yakin ingin {action_label} {len(selected)} aplikasi terpilih?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

            btn_run.setEnabled(False)
            progress_debloat.setVisible(True)

            self.batch_worker = BatchDebloatWorker(self.current_serial, selected, action_type)
            self._active_workers.add(self.batch_worker)
            self.batch_worker.progress.connect(lambda pct, s: progress_debloat.setValue(pct))

            def on_batch_done(s_count, f_count):
                self._active_workers.discard(self.batch_worker)
                progress_debloat.setVisible(False)
                btn_run.setEnabled(True)
                QMessageBox.information(dlg, "Selesai", f"Proses debloat selesai!\nBerhasil: {s_count}\nGagal: {f_count}")
                dlg.accept()
                self.refresh_debloat(force=True)

            self.batch_worker.finished.connect(on_batch_done)
            self.batch_worker.start()

        btn_run.clicked.connect(run_batch)

        row_btn.addWidget(btn_sel_all)
        row_btn.addWidget(btn_desel)
        row_btn.addStretch()
        row_btn.addWidget(btn_run)
        d_layout.addLayout(row_btn)

        dlg.exec()

    # -------------------------------------------------------------
    # LOGIC: PASANG APK
    # -------------------------------------------------------------
    def browse_apks(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Pilih File .APK untuk Dipasang", "", "Android Packages (*.apk)")
        if paths:
            self.add_apks_to_list(paths)

    def add_apks_to_list(self, paths: list):
        for p in paths:
            if p not in self.selected_apk_paths and p.lower().endswith(".apk"):
                self.selected_apk_paths.append(p)
                file_size_mb = os.path.getsize(p) / (1024 * 1024) if os.path.exists(p) else 0
                self.list_apks.addItem(f"📦 {os.path.basename(p)}  ({file_size_mb:.1f} MB)  -  {p}")

    def clear_selected_apks(self):
        self.selected_apk_paths = []
        self.list_apks.clear()
        self.txt_install_log.clear()

    def start_install_process(self):
        if not self.current_serial:
            QMessageBox.warning(self, "Perangkat Belum Terhubung", "Silakan hubungkan perangkat Android terlebih dahulu.")
            return

        if not self.selected_apk_paths:
            QMessageBox.warning(self, "Pilih APK", "Belum ada file APK yang dipilih. Klik 'Pilih File APK' atau seret file ke area di atas.")
            return

        self.btn_start_install.setEnabled(False)
        self.install_progress.setVisible(True)
        self.txt_install_log.append(f"🚀 Memulai instalasi {len(self.selected_apk_paths)} paket APK ke perangkat...\n")

        worker = InstallWorker(
            self.current_serial,
            self.selected_apk_paths,
            self.chk_reinstall.isChecked(),
            self.chk_downgrade.isChecked(),
            self.chk_grant.isChecked()
        )
        self.inst_worker = worker
        self._active_workers.add(worker)
        worker.log_added.connect(lambda log: self.txt_install_log.append(log))

        def on_inst_done(success, message):
            self._active_workers.discard(worker)
            self.on_install_finished(success, message)

        worker.finished.connect(on_inst_done)
        worker.start()

    def on_install_finished(self, success: bool, message: str):
        self.btn_start_install.setEnabled(True)
        self.install_progress.setVisible(False)
        if success:
            QMessageBox.information(self, "Instalasi Berhasil", message)
            self.clear_selected_apks()
            self.refresh_apps()
        else:
            QMessageBox.critical(self, "Instalasi Gagal", message)

    # Drag and Drop handlers
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(".apk") for u in urls):
                event.acceptProposedAction()
                self.drop_zone.setStyleSheet(
                    "QWidget#dropZone { background-color: #eff6ff; border: 2px dashed #2563eb; border-radius: 8px; padding: 16px; }"
                )

    def dragLeaveEvent(self, event):
        self.drop_zone.setStyleSheet(
            "QWidget#dropZone { background-color: #f8fafc; border: 2px dashed #93c5fd; border-radius: 8px; padding: 16px; }"
        )

    def dropEvent(self, event):
        self.drop_zone.setStyleSheet(
            "QWidget#dropZone { background-color: #f8fafc; border: 2px dashed #93c5fd; border-radius: 8px; padding: 16px; }"
        )
        apk_paths = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().lower().endswith(".apk")]
        if apk_paths:
            # Switch to Install APK subtab automatically
            self.sub_tabs.setCurrentIndex(2)
            self.add_apks_to_list(apk_paths)

    # -------------------------------------------------------------
    # SAFETY GUARDRAILS (Anti-Bootloop checks)
    # -------------------------------------------------------------
    def confirm_safety_check(self, pkg_name: str, action_name: str = "menghapus") -> bool:
        rating = debloater_service.get_safety_rating(pkg_name)
        level = rating["level"]
        desc = rating["description"]

        if level == "Unsafe":
            reply = QMessageBox.critical(
                self,
                "🚨 PERINGATAN BAHAYA TINGKAT TINGGI! (RISIKO BOOTLOOP)",
                f"Paket: '{pkg_name}'\nStatus: {rating['label']}\n\n"
                f"⚠️ PERINGATAN KERUSAKAN:\n{desc}\n\n"
                f"Aplikasi ini merupakan komponen inti sistem Android. {action_name.capitalize()} aplikasi ini "
                f"hampir dipastikan akan membuat HP Anda BOOTLOOP atau tidak bisa masuk ke layar utama!\n\n"
                f"Apakah Anda BENAR-BENAR YAKIN ingin menanggung risiko kerusakan ini?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes

        elif level in ["Expert", "Advanced"]:
            reply = QMessageBox.warning(
                self,
                f"⚠️ Peringatan Keamanan ({rating['label']})",
                f"Paket: '{pkg_name}'\nStatus: {rating['label']}\n\n"
                f"Penjelasan:\n{desc}\n\n"
                f"Apakah Anda yakin ingin melanjutkan tindakan {action_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes

        elif level == "Recommended":
            reply = QMessageBox.question(
                self,
                "Konfirmasi (Aman)",
                f"Paket: '{pkg_name}'\nStatus: 🟢 Aman Dihapus (Rekomendasi UAD)\n\n"
                f"Penjelasan: {desc}\n\n"
                f"Lanjutkan {action_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        else:
            reply = QMessageBox.question(
                self,
                f"Konfirmasi {action_name.capitalize()}",
                f"Paket '{pkg_name}' tidak terdaftar dalam database UAD.\nLanjutkan {action_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
