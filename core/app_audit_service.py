"""
App Audit Service module.
Performs in-depth analysis of Android applications via ADB:
- Detailed app metadata (versions, install/update times, installer source, UID, paths)
- Adware & Tracker SDK detection (AdMob, Unity, AppLovin, ironSource, Meta Audience Network, etc.)
- Granular permissions audit (Dangerous/sensitive vs special vs standard, granted vs denied)
"""

import re
from typing import Dict, Any, List, Optional
from core.cmd_runner import cmd_runner

# Known Ad Networks & Monetization SDKs
AD_NETWORKS_CATALOG = [
    ("Google AdMob", ["com.google.android.gms.ads", "com.google.ads"], "Jaringan Iklan Google AdMob / Ads"),
    ("Unity Ads", ["com.unity3d.services.ads", "com.unity3d.ads"], "Jaringan Iklan Video Unity"),
    ("AppLovin / MAX", ["com.applovin"], "Platform Mediasi & Iklan AppLovin MAX"),
    ("ironSource / LevelPlay", ["com.ironsource"], "Jaringan Iklan & Mediasi ironSource"),
    ("Meta Audience Network", ["com.facebook.ads"], "Jaringan Iklan Facebook / Meta"),
    ("Liftoff / Vungle", ["com.vungle"], "Jaringan Iklan Video Vungle"),
    ("Mintegral / Mobvista", ["com.mintegral", "com.mbridge.msdk"], "Jaringan Iklan Programatik Mintegral"),
    ("InMobi", ["com.inmobi"], "Jaringan Iklan InMobi"),
    ("TikTok Pangle", ["com.bytedance.sdk.openadsdk", "com.pangle"], "Jaringan Iklan Pangle ByteDance"),
    ("Chartboost", ["com.chartboost"], "Jaringan Iklan Game Chartboost"),
    ("AdColony", ["com.adcolony"], "Jaringan Iklan Video AdColony"),
    ("Tapjoy", ["com.tapjoy"], "Platform Offerwall & Iklan Tapjoy"),
    ("Amazon Mobile Ads", ["com.amazon.device.ads"], "Jaringan Iklan Amazon Mobile Ads"),
    ("SayGames / SayKit", ["by.saygames", "saygames.saykit"], "SDK Iklan & Telemetri SayGames (Game Kasual)"),
    ("Bigo Ads", ["sg.bigo.ads"], "Platform Iklan Seluler Bigo Ads"),
    ("Tramini / TopOn Mediation", ["com.tramini", "com.thinkup"], "Mediasi & Iklan Pop-up Tramini / TopOn"),
    ("Ogury Ads", ["com.ogury"], "Platform Iklan Seluler Interstitial Ogury"),
    ("Smaato Ads", ["com.smaato"], "Platform Monetisasi & Iklan Smaato"),
    ("Digital Turbine Ignite", ["com.digitalturbine"], "Sistem Iklan & Penginstal Otomatis Digital Turbine"),
    ("Plutus Monetization", ["com.plutus"], "Modul Iklan & Monetisasi Keyboard Plutus"),
    ("Xiaomi / MIUI System Ads (MSA)", ["com.miui.msa.", "com.miui.msasdk"], "Modul Layanan Iklan Bawaan Xiaomi/MIUI"),
    ("Zeus Columbus Ads", ["com.zeus.gmc.sdk"], "Jaringan Iklan Zeus Columbus SDK"),
    ("AppMetrica / Yandex Ads", ["io.appmetrica"], "Pelacak & SDK Iklan AppMetrica"),
    ("SmartDigiMkt", ["com.smartdigimkt"], "Modul Monetisasi Iklan SmartDigiMkt"),
]

# Known Trackers & Analytics SDKs
TRACKERS_CATALOG = [
    ("Firebase Analytics", ["com.google.firebase.analytics"], "Analitik Pengguna Google Firebase"),
    ("Google Measurement", ["com.google.android.gms.measurement"], "Telemetri Google Play Services"),
    ("AppsFlyer", ["com.appsflyer"], "Pelacak Atribusi & Kampanye AppsFlyer"),
    ("Adjust", ["com.adjust.sdk"], "Pelacak Penginstalan & Atribusi Adjust"),
    ("Facebook Analytics", ["com.facebook.appevents"], "Pelacak Perilaku Pengguna Meta / Facebook"),
    ("Flurry Analytics", ["com.flurry"], "Analitik Seluler Yahoo Flurry"),
    ("Branch.io", ["io.branch"], "Pelacak Deep Linking & Kampanye Branch"),
    ("OneSignal", ["com.onesignal"], "Pelacak Interaksi & Notifikasi OneSignal"),
    ("Firebase Crashlytics", ["com.google.firebase.crashlytics", "com.crashlytics"], "Pelacak Kerusakan Aplikasi"),
]

# Sensitive & Dangerous Permission Definitions with Friendly Explanations
PERMISSION_INFO_MAP = {
    # 🔴 Sensitive / Dangerous (Privacy & Security Risk)
    "android.permission.CAMERA": ("Kamera", "🔴 Berbahaya", "Dapat mengambil foto dan merekam video kapan saja."),
    "android.permission.RECORD_AUDIO": ("Mikrofon", "🔴 Berbahaya", "Dapat merekam suara dan percakapan di sekitar HP."),
    "android.permission.ACCESS_FINE_LOCATION": ("Lokasi Presisi (GPS)", "🔴 Berbahaya", "Melacak lokasi geografis akurat Anda secara realtime."),
    "android.permission.ACCESS_COARSE_LOCATION": ("Lokasi Perkiraan", "🔴 Berbahaya", "Memperkirakan lokasi berdasarkan Wi-Fi dan menara seluler."),
    "android.permission.READ_CONTACTS": ("Baca Kontak", "🔴 Berbahaya", "Dapat membaca semua nomor telepon, nama, dan email di kontak Anda."),
    "android.permission.WRITE_CONTACTS": ("Ubah Kontak", "🔴 Berbahaya", "Dapat menambah, mengubah, atau menghapus daftar kontak Anda."),
    "android.permission.READ_CALENDAR": ("Baca Kalender", "🔴 Berbahaya", "Dapat membaca seluruh jadwal dan agenda pribadi di kalender."),
    "android.permission.WRITE_CALENDAR": ("Ubah Kalender", "🔴 Berbahaya", "Dapat menambah atau menghapus acara kalender."),
    "android.permission.READ_SMS": ("Baca SMS", "🔴 Berbahaya", "Dapat membaca pesan SMS masuk/keluar termasuk kode OTP rahasia."),
    "android.permission.SEND_SMS": ("Kirim SMS", "🔴 Berbahaya", "Dapat mengirim SMS tanpa izin yang berpotensi memotong pulsa."),
    "android.permission.RECEIVE_SMS": ("Terima SMS", "🔴 Berbahaya", "Dapat memantau dan memproses pesan SMS yang masuk ke HP."),
    "android.permission.READ_CALL_LOG": ("Riwayat Panggilan", "🔴 Berbahaya", "Melihat siapa saja yang menelepon Anda dan durasi panggilan."),
    "android.permission.WRITE_CALL_LOG": ("Ubah Riwayat Telepon", "🔴 Berbahaya", "Dapat memodifikasi atau menghapus catatan riwayat panggilan."),
    "android.permission.READ_PHONE_STATE": ("Status Telepon & IMEI", "🔴 Berbahaya", "Membaca nomor ponsel, status panggilan, dan nomor identitas IMEI."),
    "android.permission.CALL_PHONE": ("Panggilan Langsung", "🔴 Berbahaya", "Dapat melakukan panggilan telepon tanpa membuka layar dialer."),
    "android.permission.READ_EXTERNAL_STORAGE": ("Baca File Memori", "🔴 Berbahaya", "Membaca seluruh dokumen, foto, dan berkas di penyimpanan."),
    "android.permission.WRITE_EXTERNAL_STORAGE": ("Ubah File Memori", "🔴 Berbahaya", "Dapat memodifikasi atau menghapus file pada penyimpanan."),
    "android.permission.READ_MEDIA_IMAGES": ("Akses Foto / Galeri", "🔴 Berbahaya", "Membaca galeri foto Anda (Android 13+)."),
    "android.permission.READ_MEDIA_VIDEO": ("Akses Video", "🔴 Berbahaya", "Membaca rekaman video pribadi Anda (Android 13+)."),
    "android.permission.READ_MEDIA_AUDIO": ("Akses Audio / Lagu", "🔴 Berbahaya", "Membaca file musik dan rekaman suara Anda (Android 13+)."),
    "android.permission.BODY_SENSORS": ("Sensor Tubuh", "🔴 Berbahaya", "Mengakses data detak jantung atau sensor biometrik kesehatan."),
    "android.permission.ACTIVITY_RECOGNITION": ("Pengenal Aktivitas Fisik", "🔴 Berbahaya", "Mendeteksi apakah Anda sedang berjalan, berlari, atau berkendara."),

    # 🔴 Sensitive / Dangerous (Privacy & Security Risk)
    "android.permission.REORDER_TASKS": ("Bawa Tugas ke Depan (REORDER_TASKS)", "🔴 Berbahaya (Bajak Layar)", "Dapat memaksakan jendela aplikasi sendiri tampil di depan saat membuka WhatsApp atau aplikasi lain (penyebab iklan pop-up 1 layar penuh)."),

    # 🟡 Special Access (Privilege Risk)
    "android.permission.SYSTEM_ALERT_WINDOW": ("Overlay / Di Atas Aplikasi", "🟡 Spesial (Risiko Pop-up)", "Dapat menampilkan jendela melayang atau iklan pop-up penuh di atas aplikasi lain."),
    "android.permission.BIND_INPUT_METHOD": ("Layanan Keyboard Sistem (IME)", "🟡 Akses Keyboard", "Berjalan di latar belakang setiap saat Anda membuka pesan/chat."),
    "android.permission.REQUEST_INSTALL_PACKAGES": ("Pasang File APK", "🟡 Spesial", "Dapat mengunduh dan memasang aplikasi luar tanpa Play Store."),
    "android.permission.PACKAGE_USAGE_STATS": ("Pantau Pemakaian Aplikasi", "🟡 Spesial", "Melihat aplikasi apa saja yang sedang Anda buka dan seberapa lama."),
    "android.permission.POST_NOTIFICATIONS": ("Kirim Notifikasi", "🟡 Perhatian", "Dapat mengirim pesan pemberitahuan di bilah status."),
    "android.permission.WRITE_SETTINGS": ("Ubah Pengaturan Sistem", "🟡 Spesial", "Dapat mengubah pengaturan sistem perangkat."),
    "android.permission.MANAGE_EXTERNAL_STORAGE": ("Akses Semua Berkas", "🟡 Spesial", "Memiliki kontrol penuh atas seluruh berkas di memori."),
    "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS": ("Abaikan Hemat Baterai", "🟡 Spesial", "Berjalan di latar belakang tanpa dibatasi sistem."),

    # 🟢 Normal Permissions
    "android.permission.INTERNET": ("Akses Internet Penuh", "🟢 Normal", "Menghubungkan aplikasi ke server online dan jaringan internet."),
    "android.permission.ACCESS_NETWORK_STATE": ("Lihat Status Jaringan", "🟢 Normal", "Memeriksa apakah koneksi internet sedang aktif atau mati."),
    "android.permission.ACCESS_WIFI_STATE": ("Lihat Status Wi-Fi", "🟢 Normal", "Memeriksa informasi koneksi jaringan Wi-Fi."),
    "android.permission.CHANGE_WIFI_STATE": ("Ubah Status Wi-Fi", "🟢 Normal", "Dapat menyalakan atau mematikan modul Wi-Fi."),
    "android.permission.VIBRATE": ("Getaran", "🟢 Normal", "Dapat mengaktifkan motor getar pada ponsel."),
    "android.permission.WAKE_LOCK": ("Cegah Layar Tidur", "🟢 Normal", "Mencegah layar atau CPU masuk ke mode hemat energi."),
    "android.permission.FOREGROUND_SERVICE": ("Layanan Latar Belakang", "🟢 Normal", "Menjalankan tugas terus-menerus dengan menampilkan notifikasi."),
    "android.permission.RECEIVE_BOOT_COMPLETED": ("Mulai Saat HP Nyala", "🟢 Normal", "Otomatis berjalan ketika perangkat baru selesai dinyalakan."),
    "android.permission.BLUETOOTH": ("Koneksi Bluetooth", "🟢 Normal", "Dapat terhubung ke perangkat Bluetooth lain."),
    "android.permission.BLUETOOTH_ADMIN": ("Kelola Bluetooth", "🟢 Normal", "Dapat mencari dan menyandingkan perangkat Bluetooth."),
}


def audit_package(serial: str, package_name: str) -> Dict[str, Any]:
    """
    Perform a complete audit on an installed application.
    Returns metadata, ad detection results, and permission breakdown.
    """
    if not serial or not package_name:
        return {}

    # Run dumpsys package for the specified application
    success, raw_dump = cmd_runner.run_adb(["shell", "dumpsys", "package", package_name], serial=serial, timeout=12)
    if not success or not raw_dump:
        return {"error": "Gagal membaca data dumpsys aplikasi."}

    info: Dict[str, Any] = {
        "package_name": package_name,
        "version_name": "-",
        "version_code": "-",
        "target_sdk": "-",
        "min_sdk": "-",
        "first_install_time": "-",
        "last_update_time": "-",
        "installer": "Sideload / Tidak Diketahui",
        "data_dir": "-",
        "code_path": "-",
        "uid": "-",
        "is_system": False,
        "is_disabled": False,
        "apk_size": "-",
        "ad_networks": [],
        "trackers": [],
        "permissions_summary": {"dangerous_count": 0, "special_count": 0, "normal_count": 0, "granted_count": 0},
        "permissions_list": [],
        "components_count": {"activities": 0, "services": 0, "receivers": 0, "providers": 0}
    }

    # 1. Parse Metadata
    m_vname = re.search(r'versionName=([^\s\r\n]+)', raw_dump)
    if m_vname: info["version_name"] = m_vname.group(1)

    m_vcode = re.search(r'versionCode=(\d+)', raw_dump)
    if m_vcode: info["version_code"] = m_vcode.group(1)

    m_target = re.search(r'targetSdk=(\d+)', raw_dump)
    if m_target: info["target_sdk"] = m_target.group(1)

    m_min = re.search(r'minSdk=(\d+)', raw_dump)
    if m_min: info["min_sdk"] = m_min.group(1)

    m_fit = re.search(r'firstInstallTime=([^\r\n]+)', raw_dump)
    if m_fit: info["first_install_time"] = m_fit.group(1).strip()

    m_lut = re.search(r'lastUpdateTime=([^\r\n]+)', raw_dump)
    if m_lut: info["last_update_time"] = m_lut.group(1).strip()

    m_inst = re.search(r'installerPackageName=([^\s\r\n]+)', raw_dump)
    if m_inst:
        installer_pkg = m_inst.group(1)
        if installer_pkg == "com.android.vending":
            info["installer"] = "Google Play Store (com.android.vending)"
        elif "packageinstaller" in installer_pkg:
            info["installer"] = "Package Installer Lokal (Sideload)"
        else:
            info["installer"] = installer_pkg

    m_path = re.search(r'codePath=([^\s\r\n]+)', raw_dump)
    if m_path:
        code_p = m_path.group(1)
        info["code_path"] = code_p
        if code_p.startswith("/system/") or code_p.startswith("/apex/") or code_p.startswith("/vendor/"):
            info["is_system"] = True

    m_data = re.search(r'dataDir=([^\s\r\n]+)', raw_dump)
    if m_data: info["data_dir"] = m_data.group(1)

    m_uid = re.search(r'userId=(\d+)', raw_dump)
    if m_uid: info["uid"] = m_uid.group(1)

    if "enabled=2" in raw_dump or "enabled=3" in raw_dump:
        info["is_disabled"] = True

    # 2. Get APK File Size
    if info["code_path"] != "-":
        ok_size, out_size = cmd_runner.run_adb(["shell", "stat", "-c", "%s", f"{info['code_path']}/base.apk"], serial=serial, timeout=3)
        if not ok_size or not out_size.strip().isdigit():
            ok_size, out_size = cmd_runner.run_adb(["shell", "stat", "-c", "%s", info["code_path"]], serial=serial, timeout=3)
        if ok_size and out_size.strip().isdigit():
            bytes_val = int(out_size.strip())
            mb_val = round(bytes_val / (1024 * 1024), 2)
            info["apk_size"] = f"{mb_val} MB ({bytes_val:,} bytes)"

    # Filter out queriesPackages and queriesIntents to prevent false positive matches
    clean_dump_lines = [
        l for l in raw_dump.splitlines()
        if not l.strip().startswith("queriesPackages=") and not l.strip().startswith("queriesIntents=")
    ]
    clean_dump = "\n".join(clean_dump_lines)

    # 3. Detect Ad Networks
    detected_ads = []
    for ad_name, patterns, ad_desc in AD_NETWORKS_CATALOG:
        for p in patterns:
            if p in clean_dump:
                detected_ads.append({"name": ad_name, "category": "Iklan", "description": ad_desc, "evidence": p})
                break
    info["ad_networks"] = detected_ads

    # 4. Detect Trackers & Analytics
    detected_trackers = []
    for tr_name, patterns, tr_desc in TRACKERS_CATALOG:
        for p in patterns:
            if p in clean_dump:
                detected_trackers.append({"name": tr_name, "category": "Pelacak / Analitik", "description": tr_desc, "evidence": p})
                break
    info["trackers"] = detected_trackers

    # 5. Parse Permissions & Granted Status
    requested_perms = []
    runtime_statuses: Dict[str, bool] = {}

    in_requested = False
    in_runtime = False

    for line in raw_dump.splitlines():
        trimmed = line.strip()
        if "requested permissions:" in line:
            in_requested = True
            in_runtime = False
            continue
        elif "runtime permissions:" in line or "install permissions:" in line:
            in_requested = False
            in_runtime = True
            continue
        elif line.startswith("    ") and not line.startswith("      ") and ":" in line:
            in_requested = False
            in_runtime = False

        if in_requested and trimmed.startswith("android.permission."):
            if trimmed not in requested_perms:
                requested_perms.append(trimmed)
        elif in_runtime and ":" in trimmed:
            parts = trimmed.split(":", 1)
            perm_key = parts[0].strip()
            is_granted = "granted=true" in parts[1].lower()
            runtime_statuses[perm_key] = is_granted

    # Structure permissions
    perms_list = []
    dang_count = 0
    spec_count = 0
    norm_count = 0
    grant_count = 0

    for perm in requested_perms:
        info_tuple = PERMISSION_INFO_MAP.get(perm)
        if info_tuple:
            friendly_name, danger_level, desc = info_tuple
        else:
            simple_name = perm.rsplit(".", 1)[-1].replace("_", " ").title()
            friendly_name = simple_name
            danger_level = "🟢 Normal"
            desc = "Izin standar sistem Android."

        is_granted = runtime_statuses.get(perm, True)  # default true for install permissions
        if is_granted:
            grant_count += 1

        if "Berbahaya" in danger_level:
            dang_count += 1
            sort_rank = 1
        elif "Spesial" in danger_level or "Perhatian" in danger_level:
            spec_count += 1
            sort_rank = 2
        else:
            norm_count += 1
            sort_rank = 3

        perms_list.append({
            "permission": perm,
            "name": friendly_name,
            "danger_level": danger_level,
            "description": desc,
            "granted": is_granted,
            "sort_rank": sort_rank
        })

    # Sort permissions: Dangerous first, then Special, then Normal
    perms_list.sort(key=lambda x: (x["sort_rank"], not x["granted"], x["name"]))
    info["permissions_list"] = perms_list
    info["permissions_summary"] = {
        "dangerous_count": dang_count,
        "special_count": spec_count,
        "normal_count": norm_count,
        "granted_count": grant_count,
        "total_requested": len(requested_perms)
    }

    # 6. Count Components
    info["components_count"]["activities"] = len(re.findall(r'Activity\s*\{', raw_dump))
    info["components_count"]["services"] = len(re.findall(r'Service\s*\{', raw_dump))
    info["components_count"]["receivers"] = len(re.findall(r'Receiver\s*\{', raw_dump))
    info["components_count"]["providers"] = len(re.findall(r'Provider\s*\{', raw_dump))

    # 7. Adware & Rogue Pop-up Threat Assessment
    has_saw = any(p["permission"] == "android.permission.SYSTEM_ALERT_WINDOW" and p["granted"] for p in perms_list)
    has_reorder = any(p["permission"] == "android.permission.REORDER_TASKS" and p["granted"] for p in perms_list)
    has_ime = "android.permission.BIND_INPUT_METHOD" in raw_dump
    has_fgs = any(p["permission"] == "android.permission.FOREGROUND_SERVICE" and p["granted"] for p in perms_list)
    is_oem = package_name in ["com.miui.msa.global", "com.miui.android.fashiongallery", "com.xiaomi.mipicks", "com.amazon.appmanager"]

    ad_count = len(detected_ads)
    threat_verdicts = []

    if (has_saw or has_reorder) and ad_count > 0:
        hijack_perm = "REORDER_TASKS (Bawa tugas ke depan)" if has_reorder else "SYSTEM_ALERT_WINDOW (Overlay)"
        if has_saw and has_reorder:
            hijack_perm = "REORDER_TASKS & Overlay"
        threat_verdicts.append(
            f"🚨 INDIKASI ADWARE POP-UP SELAYAR: Aplikasi ini memiliki modul iklan DAN izin '{hijack_perm}'! "
            "Ini adalah penyebab paling umum iklan selayar penuh tiba-tiba muncul saat membuka WhatsApp atau aplikasi lainnya."
        )

    if has_ime and ad_count > 0:
        threat_verdicts.append(
            "🚨 ADWARE KEYBOARD (IME): Aplikasi ini bertindak sebagai papan ketik/keyboard sistem yang disusupi modul iklan komersial. "
            "Iklan dapat terpicu setiap kali Anda membuka percakapan chat, WhatsApp, atau mengetik di layar."
        )

    if is_oem:
        threat_verdicts.append(
            "🏢 ADWARE SISTEM BAWAAN (OEM): Layanan promosi latar belakang bawaan pabrik yang memuat iklan rekomendasi, "
            "katalog lockscreen, atau pop-up recall."
        )

    if has_fgs and ad_count > 0 and not threat_verdicts:
        threat_verdicts.append(
            "⚡ BACKGROUND AD SERVICE: Menjalankan layanan latar belakang (Foreground Service) terus-menerus yang memuat modul iklan."
        )

    if threat_verdicts:
        threat_level = "CRITICAL"
    elif ad_count >= 2:
        threat_level = "HIGH"
    elif ad_count > 0:
        threat_level = "MEDIUM"
    else:
        threat_level = "CLEAN"

    info["threat_assessment"] = {
        "threat_level": threat_level,
        "has_overlay": has_saw,
        "has_reorder_tasks": has_reorder,
        "has_ime": has_ime,
        "has_fgs": has_fgs,
        "is_oem_adware": is_oem,
        "verdicts": threat_verdicts
    }

    return info


def scan_adware_on_device(serial: str, progress_cb=None) -> List[Dict[str, Any]]:
    """
    Perform a complete device scan to discover rogue popup adware,
    invasive monetization SDKs, and OEM ad daemons.
    """
    if not serial:
        return []

    # Get all currently installed packages for user 0
    ok_all, out_all = cmd_runner.run_adb(["shell", "pm", "list", "packages"], serial=serial)
    all_installed = set()
    if ok_all and out_all:
        for line in out_all.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                all_installed.add(line[8:].strip())

    # Get 3rd-party packages
    ok, out = cmd_runner.run_adb(["shell", "pm", "list", "packages", "-3"], serial=serial)
    pkgs = []
    if ok and out:
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                p = line[8:].strip()
                if p in all_installed:
                    pkgs.append(p)

    # Include known OEM ad daemons only if currently installed on device
    known_oem = ["com.miui.msa.global", "com.miui.android.fashiongallery", "com.xiaomi.mipicks", "com.amazon.appmanager"]
    for oem in known_oem:
        if oem in all_installed and oem not in pkgs:
            pkgs.append(oem)

    results = []
    total = len(pkgs)
    for idx, pkg in enumerate(pkgs):
        if progress_cb:
            progress_cb(idx + 1, total, pkg)
        audit = audit_package(serial, pkg)
        if not audit or "error" in audit:
            continue

        threat = audit.get("threat_assessment", {})
        lvl = threat.get("threat_level", "CLEAN")
        if lvl in ["CRITICAL", "HIGH", "MEDIUM"]:
            results.append(audit)

    # Sort results: CRITICAL first, then HIGH, then MEDIUM
    rank_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "CLEAN": 3}
    results.sort(key=lambda x: (
        rank_order.get(x.get("threat_assessment", {}).get("threat_level", "CLEAN"), 3),
        -len(x.get("ad_networks", []))
    ))
    return results
