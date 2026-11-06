from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        email = username if username is not None else kwargs.get("email")
        if email is None:
            return None
        try:
            user = user_model.objects.get(email__iexact=email)
        except user_model.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None