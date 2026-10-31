from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('social/', include('social.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('bankroll/', include('bankroll.urls')),
    path('', include('core.urls')),
]
