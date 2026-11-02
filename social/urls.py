from django.urls import path

from . import views

app_name = "social"

urlpatterns = [
    path("", views.friends, name="friends"),
    path("requests/send/", views.send_request, name="send_request"),
    path("requests/<int:request_id>/accept/", views.accept_request, name="accept_request"),
    path("requests/<int:request_id>/decline/", views.decline_request, name="decline_request"),
    path("requests/<int:request_id>/cancel/", views.cancel_request, name="cancel_request"),
    path("friends/<str:username>/", views.friend_profile, name="friend_profile"),
    path("friends/<str:username>/unfriend/", views.unfriend, name="unfriend"),
]
