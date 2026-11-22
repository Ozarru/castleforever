"""Reusable access guards for dashboard URLs.

Every route under ``/dashboard/`` is wrapped with :func:`staff_required` at the
URL layer, so a new dashboard view cannot accidentally be exposed to regular
customers just because its class forgot to inherit the staff mixin.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy("accounts:login")


def _access_required(test, message):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user = getattr(request, "user", None)
            if user is None or not user.is_authenticated:
                return redirect_to_login(request.get_full_path(), str(LOGIN_URL))
            if not test(user):
                raise PermissionDenied(message)
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


staff_required = _access_required(
    lambda user: user.is_staff,
    "Staff access required.",
)

superuser_required = _access_required(
    lambda user: user.is_staff and user.is_superuser,
    "Superuser access required.",
)
