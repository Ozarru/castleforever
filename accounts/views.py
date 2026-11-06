from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.models import Booking, ContactInquiry, ServiceRequest
from .forms import ProfileForm, SignupForm


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("base:home")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required(login_url="accounts:login")
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form, "user": request.user})


@login_required(login_url="accounts:login")
def notifications(request):
    return render(request, "accounts/notifications.html")


@login_required(login_url="accounts:login")
def activity(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    service_requests = ServiceRequest.objects.filter(email__iexact=request.user.email).order_by("-created_at")
    inquiries = ContactInquiry.objects.filter(email__iexact=request.user.email).order_by("-created_at")
    return render(request, "accounts/activity.html", {
        "bookings": bookings,
        "service_requests": service_requests,
        "inquiries": inquiries,
    })