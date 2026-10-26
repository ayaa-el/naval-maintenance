from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("comptes.urls")),
    path("facturation/", include("facturation.urls")),
    path("conventionnement/", include("conventionnement.urls")),
    path("navires/", include("navires.urls")),
    path("rh/", include("rh.urls")),
    path("equipements/", include("equipements.urls")),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)