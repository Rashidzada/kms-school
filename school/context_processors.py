from datetime import timedelta
from django.utils import timezone
from .models import AcademicSession, BackupEmailAccount, SchoolSetting, SoftwareLicense


def school_context(request):
    """
    Injects active academic session, school setting, software license, and daily auto-backup
    trigger status into every template context.
    """
    setting = SchoolSetting.objects.first()
    if not setting:
        setting = SchoolSetting(
            name="Kohisar Model School & College",
            address="Qalagay, Tehsil Kabal, District Swat, Khyber Pakhtunkhwa",
            contact="+92 344 9631323 / +92 345 3407095",
        )

    active_session = AcademicSession.objects.filter(is_active=True).first()
    if not active_session:
        active_session = AcademicSession.objects.first()

    try:
        software_license = SoftwareLicense.get_license()
    except Exception:
        software_license = None

    auto_backup_due = False
    try:
        if request.user.is_authenticated and setting.pk and setting.auto_backup_enabled:
            has_credentials = BackupEmailAccount.objects.filter(
                is_active=True
            ).exclude(email="").exclude(app_password="").exists()
            if has_credentials:
                interval_days = max(1, int(setting.auto_backup_interval_days or 1))
                if not setting.last_auto_backup_at:
                    auto_backup_due = True
                else:
                    elapsed = timezone.now() - setting.last_auto_backup_at
                    if elapsed >= timedelta(days=interval_days):
                        auto_backup_due = True
    except Exception:
        auto_backup_due = False

    return {
        "school_setting": setting,
        "active_session": active_session,
        "software_license": software_license,
        "auto_backup_due": auto_backup_due,
    }


