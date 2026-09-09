from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Kohisar Model School & College (KMS) Admin Branding
admin.site.site_header = "Kohisar Model School & College (KMS)"
admin.site.site_title = "KMS Portal Administration"
admin.site.index_title = "Institutional Control & Database Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("finance/", include("finance.urls")),
    path("cashbook/", include("accounts.urls")),
    path("exams/", include("exams.urls")),
    path("", include("school.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "school.views.custom_page_not_found"
handler500 = "school.views.custom_server_error"
