from .models import AcademicSession, AcademicTerm, SiteConfig


def site_defaults(request):
    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    vals = SiteConfig.objects.all()
    contexts = {
        "current_session": current_session.name if current_session else "",
        "current_term": current_term.name if current_term else "",
    }
    for val in vals:
        contexts[val.key] = val.value

    return contexts
