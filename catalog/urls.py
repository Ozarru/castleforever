from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
    path("venues/", views.venues, name="venues"),
    path("estates/", views.venues, name="estates"),
    path("venues/", views.venues, name="venue-list"),
    path("venues/<slug:slug>/", views.venue_detail, name="venue-detail"),
    path("cars/", views.car_rentals, name="car-rentals"),
    path("rentals/", views.car_rentals, name="rentals"),
    path("vehicles/", views.car_rentals, name="vehicles"),
]
