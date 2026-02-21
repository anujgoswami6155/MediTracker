from django.urls import path
from .views import UserRegisterView, UserLoginView, logout_view  # ← Changed here

app_name = "accounts"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),  # ← Changed here (function, not .as_view())
]