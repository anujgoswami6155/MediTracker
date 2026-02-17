from django.urls import path
<<<<<<< HEAD
from .views import UserLoginView
from django.contrib.auth.views import LogoutView
=======
from .views import UserRegisterView, UserLoginView, UserLogoutView
>>>>>>> 57f8c8a6c814a38c0e4536d2c406f487cddb3ece

app_name = "accounts"

urlpatterns = [
<<<<<<< HEAD
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/accounts/login/"), name="logout"),
=======
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
>>>>>>> 57f8c8a6c814a38c0e4536d2c406f487cddb3ece
]
