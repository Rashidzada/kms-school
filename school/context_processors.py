from .models import AcademicSession, SchoolSetting, SoftwareLicense


def school_context(request):
    """
    Injects active academic session, school setting, and software license into every template context.
    """
    setting = SchoolSetting.objects.first()
    if not setting:
        # Provide a default instance if none exists in DB yet
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

    return {
        "school_setting": setting,
        "active_session": active_session,
        "software_license": software_license,
    }

