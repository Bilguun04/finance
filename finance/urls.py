from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("social/", include("social.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("bankroll/", include("bankroll.urls")),
    path("", include("core.urls")),
]
