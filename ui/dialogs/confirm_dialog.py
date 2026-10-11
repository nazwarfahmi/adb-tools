"""
Two-Step Verification & Safe Confirmation Dialogs module.
Prevents accidental misclicks on destructive operations:
- Uninstalling applications
- Clearing application data/cache
- Deleting files/directories
- Freezing/disabling packages
"""

from PySide6.QtWidgets import QMessageBox, QWidget


def confirm_two_step(
    parent: QWidget,
    action_type: str,
    target_title: str,
    target_identifier: str = "",
    extra_warning: str = "",
    is_critical_system: bool = False
) -> bool:
    """
    Executes a 2-step confirmation dialog with default 'No' to prevent accidental misclicks.
    Returns True only if the user explicitly approves both steps.
    """
    if action_type == "uninstall":
        step1_title = "⚠️ Konfirmasi Uninstall (Langkah 1/2)"
        step1_msg = (
            f"Apakah Anda yakin ingin mencopot (uninstall) aplikasi berikut?\n\n"
            f"📱 <b>{target_title}</b>"
        )
        if target_identifier:
            step1_msg += f"\n📦 Paket: <code>{target_identifier}</code>"
        step1_msg += "\n\nKlik <b>'Ya, Lanjutkan'</b> untuk masuk ke verifikasi akhir."

        step2_title = "🚨 Verifikasi Akhir Uninstall (Langkah 2/2)"
        if is_critical_system:
            step2_msg = (
                f"🚨 <b>PERINGATAN BAHAYA KRITIS SISTEM!</b>\n\n"
                f"Aplikasi '<b>{target_title}</b>' merupakan komponen penting sistem Android.\n"
                f"{extra_warning}\n\n"
                f"⚠️ Menghapus aplikasi ini berisiko menyebabkan <b>BOOTLOOP</b> atau HP gagal menyala!\n\n"
                f"Apakah Anda BENAR-BENAR YAKIN ingin menanggung risiko ini dan tetap mencopot pemasangan?"
            )
        else:
            step2_msg = (
                f"<b>PERINGATAN PERMANEN:</b>\n\n"
                f"Aplikasi '<b>{target_title}</b>' dan seluruh berkas data penggunanya akan dihapus permanen dari perangkat.\n\n"
                f"Apakah Anda <b>BENAR-BENAR YAKIN</b> ingin mencopot pemasangan sekarang?"
            )

    elif action_type == "clear_data":
        step1_title = "🧹 Konfirmasi Hapus Data (Langkah 1/2)"
        step1_msg = (
            f"Apakah Anda yakin ingin menghapus seluruh data & cache aplikasi:\n\n"
            f"📱 <b>{target_title}</b>"
        )
        if target_identifier:
            step1_msg += f"\n📦 Paket: <code>{target_identifier}</code>"
        step1_msg += "\n\nKlik <b>'Ya, Lanjutkan'</b> untuk masuk ke verifikasi akhir."

        step2_title = "🚨 Verifikasi Akhir Hapus Data (Langkah 2/2)"
        step2_msg = (
            f"<b>PERINGATAN RESET TOTAL:</b>\n\n"
            f"Seluruh basis data, berkas unduhan, akun login, dan preferensi pada '<b>{target_title}</b>' "
            f"akan direset ke kondisi awal seperti baru dipasang.\n\n"
            f"Apakah Anda <b>BENAR-BENAR YAKIN</b> ingin mengosongkan seluruh data aplikasi?"
        )

    elif action_type == "delete_file":
        step1_title = "🗑️ Konfirmasi Hapus Berkas (Langkah 1/2)"
        step1_msg = (
            f"Apakah Anda yakin ingin menghapus berkas berikut?\n\n"
            f"📁 <b>{target_title}</b>"
        )
        if target_identifier:
            step1_msg += f"\nJalur: <code>{target_identifier}</code>"
        step1_msg += "\n\nKlik <b>'Ya, Lanjutkan'</b> untuk verifikasi akhir."

        step2_title = "🚨 Verifikasi Akhir Hapus Berkas (Langkah 2/2)"
        step2_msg = (
            f"<b>PERINGATAN PERMANEN:</b>\n\n"
            f"Berkas yang dihapus TIDAK masuk ke tempat sampah (Recycle Bin) dan <b>TIDAK DAPAT DIPULIHKAN</b> kembali!\n\n"
            f"Apakah Anda <b>BENAR-BENAR YAKIN</b> ingin menghapus berkas ini secara permanen?"
        )

    elif action_type == "freeze":
        step1_title = "❄️ Konfirmasi Bekukan Aplikasi (Langkah 1/2)"
        step1_msg = (
            f"Apakah Anda yakin ingin membekukan (freeze / nonaktifkan) aplikasi:\n\n"
            f"📱 <b>{target_title}</b>"
        )
        if target_identifier:
            step1_msg += f"\n📦 Paket: <code>{target_identifier}</code>"
        step1_msg += "\n\nAplikasi akan disembunyikan sampai diaktifkan kembali.\nKlik <b>'Ya, Lanjutkan'</b> untuk verifikasi."

        step2_title = "⚠️ Verifikasi Pembekuan (Langkah 2/2)"
        if is_critical_system:
            step2_msg = (
                f"🚨 <b>PERINGATAN KEAMANAN SISTEM:</b>\n\n"
                f"Paket ini berstatus: {extra_warning}\n"
                f"Membekukan aplikasi ini dapat memengaruhi fitur atau kestabilan sistem perangkat.\n\n"
                f"Apakah Anda yakin ingin tetap membekukan paket ini?"
            )
        else:
            step2_msg = (
                f"Aplikasi '<b>{target_title}</b>' akan dihentikan dan dinonaktifkan.\n\n"
                f"Apakah Anda yakin ingin membekukan aplikasi ini sekarang?"
            )

    else:
        step1_title = f"Konfirmasi Tindakan: {action_type} (Langkah 1/2)"
        step1_msg = f"Lanjutkan tindakan {action_type} pada '<b>{target_title}</b>'?"
        step2_title = f"Verifikasi Akhir: {action_type} (Langkah 2/2)"
        step2_msg = f"Apakah Anda benar-benar yakin ingin melanjutkan {action_type}?"

    # --- LANGKAH 1 ---
    msg1 = QMessageBox(parent)
    msg1.setIcon(QMessageBox.Question)
    msg1.setWindowTitle(step1_title)
    msg1.setText(step1_msg)
    btn_yes1 = msg1.addButton("Ya, Lanjutkan", QMessageBox.YesRole)
    btn_no1 = msg1.addButton("Batal", QMessageBox.NoRole)
    msg1.setDefaultButton(btn_no1)
    msg1.exec()

    if msg1.clickedButton() != btn_yes1:
        return False

    # --- LANGKAH 2 (Verifikasi Akhir) ---
    msg2 = QMessageBox(parent)
    msg2.setIcon(QMessageBox.Critical if is_critical_system else QMessageBox.Warning)
    msg2.setWindowTitle(step2_title)
    msg2.setText(step2_msg)
    btn_yes2 = msg2.addButton("Ya, Saya Yakin", QMessageBox.YesRole)
    btn_no2 = msg2.addButton("Batal", QMessageBox.NoRole)
    msg2.setDefaultButton(btn_no2)
    msg2.exec()

    return msg2.clickedButton() == btn_yes2
