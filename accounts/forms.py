from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()

INPUT_CLASSES = (
    "w-full bg-white/80 border border-[#d8d0c0] px-4 py-3.5 text-sm "
    "placeholder:text-gray-400 focus:border-[#A58A5A] focus:outline-none "
    "focus:ring-1 focus:ring-[#A58A5A]/40 transition"
)


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "••••••••",
            "autocomplete": "current-password",
        }),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": INPUT_CLASSES})


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("password1", "password2"):
            self.fields[field_name].widget.attrs.update({
                "class": INPUT_CLASSES,
                "placeholder": "Password" if field_name == "password1" else "Confirm password",
                "autocomplete": "new-password",
            })
            self.fields[field_name].help_text = ""
        # Remove the default username field entirely.
        self.fields.pop("username", None)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user
