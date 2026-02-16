from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps


def role_required(required_role):
    """
    Usage:
    @role_required("patient")
    @role_required("doctor")
    @role_required("family")
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Safety check
            if not hasattr(user, "role"):
                return redirect("accounts:login")

            if user.role != required_role:
                return redirect("accounts:login")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
