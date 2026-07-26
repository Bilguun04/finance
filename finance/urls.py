from django.urls import include, path

urlpatterns = [
    path('account/', include("account.urls")),
    path('social/', include('social.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('', include('core.urls')),
]
