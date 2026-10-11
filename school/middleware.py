from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from .models import SoftwareLicense


class SoftwareLicenseMiddleware:
    """
    Standard License & Subscription Enforcement Middleware:
    Verifies that the software installation is within an active trial or paid subscription period.
    When expired, redirects web traffic to the Renewal Contact Screen (/license/expired/)
    while exempting developer renewal endpoints, static assets, and authentication paths.
    """

    EXEMPT_PREFIXES = [
        "/license/",
        "/static/",
        "/media/",
        "/favicon.ico",
        "/admin/login/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Allow exempt paths
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)

        # Check license validity
        try:
            lic = SoftwareLicense.get_license()
            if not lic.is_valid():
                # If AJAX / JSON request, return 403 JSON
                is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
                if is_ajax or request.content_type == "application/json":
                    return JsonResponse({
                        "status": "error",
                        "license_expired": True,
                        "message": "Software Subscription Expired. Contact developer for renewal.",
                        "developer_phone": lic.developer_phone,
                        "developer_whatsapp": lic.developer_whatsapp,
                    }, status=403)

                return redirect(reverse("license_expired"))
        except Exception:
            # If database table not initialized yet, allow request to prevent setup locking
            pass

        return self.get_response(request)
