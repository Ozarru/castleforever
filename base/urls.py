from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("cookies/", views.cookies, name="cookies"),
    path("destinations/", views.destinations, name="destinations"),
    path("destination/", views.destinations, name="destination"),
    path("approach/", views.approach, name="approach"),
    path("our-approach/", views.approach, name="our-approach"),
    path("our_approach/", views.approach, name="our_approach"),
    path("payment-approach/", views.approach, name="payment-approach"),
    path("payments/", views.approach, name="payments"),
]
