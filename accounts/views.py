<<<<<<< HEAD
from django.contrib.auth.views import LoginView

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
=======
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegisterForm
from .models import User


# 🔹 Signup View
class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")


# 🔹 Login View
class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == "patient":
            return reverse_lazy("patients:dashboard")

        elif user.role == "doctor":
            return reverse_lazy("doctors:dashboard")

        elif user.role == "family":
            return reverse_lazy("monitoring:dashboard")

        return reverse_lazy("accounts:login")


# 🔹 Logout View
class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
>>>>>>> 57f8c8a6c814a38c0e4536d2c406f487cddb3ece
