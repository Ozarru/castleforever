from django.urls import path
from . import views

app_name = "catalog"
urlpatterns = [
    path("estates/", views.estates, name="estates"),
    path("estates/", views.estates, name="estate-list"),
    path("estates/<slug:slug>/", views.estate_detail, name="estate-detail"),
    path("cars/", views.car_rentals, name="car-rentals"),
    path("rentals/", views.car_rentals, name="rentals"),
    path("vehicles/", views.car_rentals, name="vehicles"),
]
