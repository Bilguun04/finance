from django.urls import path

from . import views

app_name = "social"

urlpatterns = [
    path("friends/", views.friend_list, name="friend_list"),
    path("friends/search/", views.friend_search, name="friend_search"),
    path("friends/request/<str:target_uid>/", views.friend_request_send, name="friend_request_send"),
    path("friends/accept/<str:request_id>/", views.friend_request_accept, name="friend_request_accept"),
    path("friends/decline/<str:request_id>/", views.friend_request_decline, name="friend_request_decline"),
    path("friends/<str:target_uid>/portfolio/", views.friend_portfolio_view, name="friend_portfolio"),
]
