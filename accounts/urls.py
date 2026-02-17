from django.urls import path
from .views import UserLoginView
from django.contrib.auth.views import LogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/accounts/login/"), name="logout"),
]
