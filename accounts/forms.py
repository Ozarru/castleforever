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


class DashboardUserCreationForm(UserCreationForm):
    """Superuser-only form for creating dashboard accounts."""

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )
    first_name = forms.CharField(
        label=_("First name"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "First name",
        }),
    )
    last_name = forms.CharField(
        label=_("Last name"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Last name",
        }),
    )
    phone = forms.CharField(
        label=_("Phone"),
        required=False,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "+33 0 11 22 33 44",
        }),
    )
    is_staff = forms.BooleanField(
        label=_("Staff access"),
        required=False,
        help_text=_("Can sign in to the dashboard."),
        widget=forms.CheckboxInput(attrs={"class": "h-4 w-4 accent-[#A58A5A]"}),
    )
    is_superuser = forms.BooleanField(
        label=_("Superuser access"),
        required=False,
        help_text=_("Full administrative access, including creating other users."),
        widget=forms.CheckboxInput(attrs={"class": "h-4 w-4 accent-[#A58A5A]"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_staff",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Email is the login identifier, so the separate username input is not
        # shown. It is populated from the email address in save().
        self.fields.pop("username", None)
        for field_name in ("password1", "password2"):
            field = self.fields[field_name]
            field.widget.attrs.update({
                "class": INPUT_CLASSES,
                "placeholder": _("Password") if field_name == "password1" else _("Confirm password"),
                "autocomplete": "new-password",
            })
            field.help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if (
            User.objects.filter(email__iexact=email).exists()
            or User.objects.filter(username__iexact=email).exists()
        ):
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("is_superuser"):
            # A superuser without staff access would be locked out of the
            # dashboard itself, so keep the two flags consistent.
            cleaned_data["is_staff"] = True
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user


class DashboardUserChangeForm(forms.ModelForm):
    """Superuser-only editable fields for an existing dashboard account."""

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "is_staff",
            "is_superuser",
            "is_active",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": INPUT_CLASSES}),
            "first_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "is_staff": forms.CheckboxInput(attrs={"class": "h-4 w-4 accent-[#A58A5A]"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "h-4 w-4 accent-[#A58A5A]"}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-4 w-4 accent-[#A58A5A]"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists() or User.objects.filter(
            username__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("is_superuser"):
            cleaned_data["is_staff"] = True
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user
