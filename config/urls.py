from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

API_V1 = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Routes
    path(API_V1 + "auth/", include("apps.accounts.urls", namespace="accounts")),
    path(API_V1 + "internships/", include("apps.internships.urls", namespace="internships")),
    path(API_V1 + "applications/", include("apps.applications.urls", namespace="applications")),
    # OpenAPI schema & docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)